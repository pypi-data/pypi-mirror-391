import ast
import inspect
import re
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4

import syntax_checker
from lxml import html as lxml_html
from playwright.sync_api import sync_playwright

from museflow.element.element import Element
from museflow.element.inventory_fft import factory_for_tag
from museflow.element.style import Style
from museflow.pyjs_compiler.pyjs_compiler import PYJSCompiler


class _CallRewriter(ast.NodeTransformer):
    """
    AST transformer that rewrites variable and function name references according to a provided rename map

    This is primarily used during Museflow’s script preprocessing step to
    ensure that calls and references to top-level functions, classes, and
    variables match their namespace-prefixed versions injected by `_NamespaceInjector`

    Example:
        Suppose the following namespace renaming occurred:
            rename_map = {"init": "main_init", "App": "main_App"}

        A code snippet like:
            init()
            a = App()

        would be transformed into:
            main_init()
            a = main_App()

    Parameters
    ----------
    rename_map : dict[str, str]
        A mapping of original identifiers (unprefixed names) to their namespaced equivalents
    """

    def __init__(self, rename_map):
        self.rename_map = rename_map

    def visit_Name(self, node):
        if node.id in self.rename_map:
            return ast.copy_location(ast.Name(id=self.rename_map[node.id], ctx=node.ctx), node)
        return node


import ast


class _NamespaceInjector(ast.NodeTransformer):
    """
    Injects a namespace prefix into top-level identifiers (functions, classes, assignments)
    while leaving loop variables, comprehensions, and nested definitions intact
    """

    def __init__(self, namespace: str):
        self.namespace = namespace
        self.top_level = True
        self.in_loop = False

    def _enter_scope(self):
        old_top = self.top_level
        old_loop = self.in_loop
        self.top_level = False
        self.in_loop = False
        return old_top, old_loop

    def _exit_scope(self, old_top, old_loop):
        self.top_level = old_top
        self.in_loop = old_loop

    def visit_FunctionDef(self, node: ast.FunctionDef):
        if self.top_level:
            node.name = f'{self.namespace}_{node.name}'
        old_top, old_loop = self._enter_scope()
        self.generic_visit(node)
        self._exit_scope(old_top, old_loop)
        return node

    def visit_ClassDef(self, node: ast.ClassDef):
        if self.top_level:
            node.name = f'{self.namespace}_{node.name}'
        old_top, old_loop = self._enter_scope()
        self.generic_visit(node)
        self._exit_scope(old_top, old_loop)
        return node

    def visit_Assign(self, node: ast.Assign):
        if self.top_level and not self.in_loop:
            for target in node.targets:
                if isinstance(target, ast.Name):
                    target.id = f'{self.namespace}_{target.id}'
        self.generic_visit(node)
        return node

    def visit_For(self, node: ast.For):
        old_loop = self.in_loop
        self.in_loop = True  # mark that we're inside a loop
        self.generic_visit(node)
        self.in_loop = old_loop
        return node

    def visit_While(self, node: ast.While):
        old_loop = self.in_loop
        self.in_loop = True
        self.generic_visit(node)
        self.in_loop = old_loop
        return node

    def visit_ListComp(self, node: ast.ListComp):
        old_top, old_loop = self._enter_scope()
        self.generic_visit(node)
        self._exit_scope(old_top, old_loop)
        return node

    def visit_DictComp(self, node: ast.DictComp):
        old_top, old_loop = self._enter_scope()
        self.generic_visit(node)
        self._exit_scope(old_top, old_loop)
        return node

    def visit_SetComp(self, node: ast.SetComp):
        old_top, old_loop = self._enter_scope()
        self.generic_visit(node)
        self._exit_scope(old_top, old_loop)
        return node

    def visit_GeneratorExp(self, node: ast.GeneratorExp):
        old_top, old_loop = self._enter_scope()
        self.generic_visit(node)
        self._exit_scope(old_top, old_loop)
        return node


@dataclass(frozen=True)
class _MuseflowPyScript:
    """
       Represents a Python script intended for JavaScript compilation

       Attributes:
           invoker (str): Path of the script or module that is invoking this script
                          Used to resolve relative imports and paths
           path (str): Filesystem path to the actual Python script to be read and processed

       Methods:
           read() -> str:
               Reads and returns the full content of the script file as a string
       """
    invoker: str
    path: str

    def __str__(self):
        return f'{self.__class__.__name__}, Invoker: {self.invoker}, Path: {self.path}'

    def __repr__(self):
        return self.__str__()

    def read(self) -> str:
        with open(self.path, 'r') as fd:
            return fd.read()


class MuseflowException(Exception):
    def __init__(self, message: str):
        super().__init__(f'{self.__class__.__name__}: {message}')


class Museflow:
    """
    Museflow page generator: embeds HTML and a script (Python transpiled to JS)
    into a fully working standalone HTML page

    :parameters:
    - element: the root HTML element
    - script: the Python script to embed (Optional)
    """

    @classmethod
    def verify_html_integrity(cls, html_text: str) -> None:
        """
        Verify HTML integrity using lxml.html
        Raises MuseflowException if parsing fails
        This parser correctly handles void elements and non-XML HTML syntax
        """
        try:
            lxml_html.fromstring(html_text)
        except Exception as e:
            raise MuseflowException(f'HTML parsing error: {e}\nHTML: {html_text}')

    @classmethod
    def load_py_script(cls, script_file: Path) -> _MuseflowPyScript:
        """
        Load a Python script for Museflow preprocessing and compilation.

        Automatically resolves both:
          - The path of the caller (invoker)
          - The absolute path to the script being loaded

        The 'invoker' is the Python file that called this method
        The 'path' is the fully resolved path to the script file to be compiled
        """
        caller_frame = inspect.stack()[1]
        caller_path = Path(caller_frame.filename).resolve()
        script_path = Path(script_file)

        if not script_path.is_absolute():
            script_path = (caller_path.parent / script_path).resolve()

        return _MuseflowPyScript(invoker=str(caller_path), path=str(script_path))

    @classmethod
    def __preprocess_script(cls, py_script: "_MuseflowPyScript") -> str:
        """
        Preprocess a Python script for JavaScript compilation:
        - Inject namespace prefixes for all top-level variables, functions, and classes.
        - Recursively inline imported scripts.
        - Update main script calls to match the namespace-prefixed names.
        """
        processed_files = set()
        rename_map = {}  # original_name -> namespaced_name
        top_invoker = Path(py_script.invoker).parent.resolve()

        def _preprocess(script: "_MuseflowPyScript") -> str:
            script_path = Path(script.path).resolve()
            if script_path in processed_files:
                return ''
            processed_files.add(script_path)

            code = script.read()

            # Strip <-PY_SKIP-> ... <-PY_SKIP_END-> blocks
            code = re.sub(r'# <-PY_SKIP->.*?# <-PY_SKIP_END->', '', code, flags=re.DOTALL)

            # Process <-PY_IMPORT-> MODULE:PATH recursively
            pyimport_pattern = re.compile(r'# <-PY_IMPORT->\s*(\w+)\s*:\s*(.+)')
            inlined_code = ''  # noqa

            for line in code.splitlines():
                stripped = line.strip()
                match = pyimport_pattern.match(stripped)
                if match:
                    module_name, module_path_str = match.groups()
                    module_path_obj = Path(module_path_str)
                    if not module_path_obj.is_absolute():
                        module_full_path = (script_path.parent / module_path_obj).resolve()
                    else:
                        module_full_path = module_path_obj.resolve()
                    module_script = _MuseflowPyScript(invoker=str(top_invoker), path=str(module_full_path))
                    inlined_code += _preprocess(module_script)

            # Inject namespace for this script
            namespace_name = script_path.stem
            try:
                tree = ast.parse(code)  # noqa
                injector = _NamespaceInjector(namespace_name)
                tree = injector.visit(tree)  # noqa
                code = ast.unparse(tree)
            except Exception as e:  # noqa
                raise MuseflowException(f'Failed to inject namespace for {namespace_name}: {e}')

            # Build rename map for this script (top-level names)
            for node in ast.iter_child_nodes(ast.parse(code)):
                if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                    rename_map[node.name.replace(f'{namespace_name}_', '')] = node.name
                elif isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            rename_map[target.id.replace(f'{namespace_name}_', '')] = target.id

            inlined_code += f'# Script {namespace_name} with namespace injected\n{code}\n'
            return inlined_code

        inlined_code = _preprocess(py_script)

        try:
            tree = ast.parse(inlined_code)
            tree = _CallRewriter(rename_map).visit(tree)
            inlined_code = ast.unparse(tree)
        except Exception as e:
            raise MuseflowException(f'Failed to rewrite main calls with namespace: {e}')

        return inlined_code

    @classmethod
    def __postprocess_script(cls, javascript_code: str) -> str:
        """
        Postprocess compiled JavaScript

        Tasks performed:
        - Strip single-line and multi-line comments
        - Optionally, normalize whitespace
        """
        try:
            code = javascript_code

            # Remove Single-Line Comments (// ...)
            single_line_comment_pattern = re.compile(r'^\s*//.*$', re.MULTILINE)
            code = re.sub(single_line_comment_pattern, '', code)

            # Remove Multi-Line Comments (/* ... */)
            multi_line_comment_pattern = re.compile(r'/\*.*?\*/', re.DOTALL)
            code = re.sub(multi_line_comment_pattern, '', code)

            # Remove Empty Lines and Normalize Spacing
            code_lines = [line.rstrip() for line in code.splitlines() if line.strip()]
            code = '\n'.join(code_lines)

            # JS Syntax Verification
            res = syntax_checker.check_syntax('js', code)
            errors = res.errors
            desc_errors = []

            # Remove 'var __name__ = '__main__'
            pattern = r"^\s*var __name__ = '__main__';\s*\n?"
            code = re.sub(pattern, '', code, flags=re.MULTILINE)

            # --- Remove "export var ..." declarations ---
            export_var_pattern = re.compile(
                r'^\s*export\s+var\s+([A-Za-z0-9_]+)\s*=\s*',  # match "export var name ="
                re.MULTILINE
            )
            # Replace `export var x =` → `var x =`
            code = re.sub(export_var_pattern, r'var \1 = ', code)

            if errors:
                lines = code.splitlines()
                for line_num, col_num in errors:
                    if 0 < line_num <= len(lines):
                        line = lines[line_num - 1]
                        pointer = ' ' * (col_num - 1) + '^'
                        desc_errors.append(f'{line_num}:{col_num} {line}\n{pointer}\n')
                raise MuseflowException(f'JavaScript Syntax errors:\n' + ''.join(desc_errors))

            return code
        except Exception as e:
            raise MuseflowException(f'Failed to compile Python to JavaScript: {e}')

    @classmethod
    def compile_to_js(cls, py_script: _MuseflowPyScript) -> str:
        """ Compile Python code to JavaScript """
        pre_processed_code = None
        code = None

        try:
            pre_processed_code = cls.__preprocess_script(py_script)
            code = PYJSCompiler.compile(pre_processed_code)
            return cls.__postprocess_script(code)
        except Exception as e:
            raise MuseflowException(f'Failed to compile Python script: {e}\nInput:\n{pre_processed_code}\nOutput:{code}')

    @classmethod
    def verify_render_integrity(cls, html_text: str) -> None:
        """
        Ensure the rendered HTML is error-free by inspecting the browser console logs
        Note: This only verifies issues that occur during page load, not runtime events
              triggered by user interactions (E.G. clicks or form submissions)
        """
        subprocess.run([sys.executable, '-m', 'playwright', 'install'], check=True)

        with tempfile.TemporaryDirectory() as tmpdir:
            html_file = Path(tmpdir) / f'{uuid4().hex}.html'
            html_file.write_text(html_text, encoding='utf-8')

            errors = []

            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()

                def handle_page_error(err):
                    text = str(err).strip()
                    errors.append(('pageerror', text))

                page.on('pageerror', handle_page_error)

                page.goto(f'file://{html_file.resolve()}')
                page.wait_for_load_state('load')

                browser.close()

        if errors:
            raise MuseflowException(f'Render integrity verification error:' + '\n'.join(errors))

    @classmethod
    def render(
            cls,
            root: Element,
            script: _MuseflowPyScript | None = None,
            indent: int = 2,
            force: bool = False,
            verify: bool = False
    ) -> str:
        # if getattr(root, 'tag', None) != 'html':
        #     raise MuseflowException(f'Root element must be <html>, got: {root.tag}')

        if script:
            # Wrap the script in a <script> element
            script_element = Element(tag='script', is_void_element=False)
            script_element.adopt(cls.compile_to_js(script))

            body = root.find_child_element(tag='body')
            if body is None:
                raise MuseflowException('Script provided, but no <body> element found')
            body.adopt(script_element)

        # Render HTML
        html_text = root.render(indent=indent)

        if not force:
            cls.verify_html_integrity(html_text)

        if verify:
            cls.verify_render_integrity(html_text)

        return html_text

    @classmethod
    def render_file(
            cls,
            root: Element,
            script: _MuseflowPyScript | None = None,
            indent: int = 2,
            verify: bool = False,
            target_file: Path = None
    ) -> None:
        """ Write a full HTML string with optional embedded script to a file """
        target_file = target_file or Path('index.html')

        html_text = cls.render(root=root, script=script, indent=indent, verify=verify)

        with target_file.open('w', encoding='utf-8') as fd:
            fd.write(html_text)

    @classmethod
    def interpret(cls, html_text: str) -> Element:
        """ Convert an HTML string into a corresponding Element """
        cls.verify_html_integrity(html_text=html_text)

        try:
            parser = lxml_html.HTMLParser()
            root_node = lxml_html.fromstring(html_text, parser=parser)
            elem_params = inspect.signature(Element.__init__).parameters

            def recurse(node) -> Element | str | None:
                if not isinstance(node.tag, str):
                    text = node.text.strip() if node.text else None
                    return text if text else None

                attrib = dict(node.attrib)

                # print('1:', attrib)

                if 'class' in attrib:
                    attrib['_class'] = attrib.pop('class')
                if 'id' in attrib:
                    attrib['_id'] = attrib.pop('id')
                if 'style' in attrib:
                    parsed = Style.parse_inline_style(attrib['style'])  # returns dict
                    attrib['style'] = Style(**parsed)

                # Create element using factory
                # print('2:', attrib)
                produce = factory_for_tag(node.tag)
                try:
                    el = produce(**attrib)
                except Exception as e:
                    raise MuseflowException(f'Unable to interpret tag: {node.tag}: {e}')

                # Recursively process children
                children = []
                if node.text and node.text.strip():
                    children.append(node.text.strip())

                for child in node:
                    child_el = recurse(child)
                    if child_el:
                        children.append(child_el)
                    if child.tail and child.tail.strip():
                        children.append(child.tail.strip())

                if children:
                    el.adopt(children if len(children) > 1 else children[0])

                return el

            return recurse(root_node)

        except Exception as e:
            raise MuseflowException(f'Failed to interpret HTML: {e}')
