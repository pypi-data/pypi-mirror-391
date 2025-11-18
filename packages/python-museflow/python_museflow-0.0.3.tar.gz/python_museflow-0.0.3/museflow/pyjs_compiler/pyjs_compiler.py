import ast

from museflow.pyjs_compiler.pyjs_compiler_unit_abs import PYJSCompilerUnitException
from museflow.pyjs_compiler.pyjs_nexus import PYJSNexus


class PYJSCompiler:
    """ Python-to-JavaScript Compiler """

    @classmethod
    def compile(cls, code: str) -> str:
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            raise PYJSCompilerUnitException(f'Syntax error in Python code: {e}')

        js_lines = []
        for node in tree.body:
            js_line = cls._compile_node(node)
            js_lines.append(js_line)

        js_code = '\n'.join(js_lines)
        return js_code

    @classmethod
    def _compile_node(cls, node: ast.AST) -> str:
        """
        Compile a single AST node using the PYJSNexus dispatch map.
        Supports single AST types and tuples of AST types.
        """

        dispatch_map = PYJSNexus.to_dispatch_map()

        for variant, unit in dispatch_map.items():
            if isinstance(node, variant):
                return unit.compile(node)

        raise PYJSCompilerUnitException(f'Unsupported AST node type: {type(node)}')
