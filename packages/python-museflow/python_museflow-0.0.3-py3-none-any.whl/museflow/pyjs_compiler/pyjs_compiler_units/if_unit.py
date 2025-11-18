import ast
from typing import Any

from museflow.pyjs_compiler.pyjs_compiler_unit_abs import PYJSCompilerUnit, PYJSCompilerUnitException


class IfUnit(PYJSCompilerUnit):
    @property
    def variant(self) -> Any:
        return ast.If

    def compile(self, node: ast.AST) -> str:
        """
            Compiles an ast.If node (including chained elif/else structures)
            while preserving Python's function-scope behavior for variables

            This method achieves Python-like scoping (where an assignment in an 'if'
            block modifies the surrounding function scope variable) by ensuring that
            the 'let' declaration keyword is suppressed for all assignments within
            the conditional structure
        """
        if not isinstance(node, ast.If):
            raise PYJSCompilerUnitException(f'Invalid node type: {type(node)}, expected If')

        return self._compile_if_chain(node, do_declare=False)

    def _compile_if_chain(self, node: ast.If, do_declare: bool = False) -> str:
        old_top = self.dispatch_map[ast.Assign].do_declare
        self.dispatch_map[ast.Assign].do_declare = do_declare

        try:
            test_js = self._compile_value(node.test)  # noqa
            body_js = self._compile_body(node.body, indent=4, do_declare=False)  # noqa
            js = f'if ({test_js}) {{\n{body_js}\n}}'

            if node.orelse:
                first = node.orelse[0]
                if isinstance(first, ast.If):
                    js += f' else {self._compile_if_chain(first, do_declare=False)}'
                else:
                    js += f' else {{\n{self._compile_body(node.orelse, indent=4, do_declare=False)}\n}}'  # noqa

            return js

        finally:
            self.dispatch_map[ast.Assign].do_declare = old_top

    def _compile_body(self, body_nodes: list[ast.AST], indent: int = 4, do_declare: bool = False) -> str:
        js_lines = []
        pad = ' ' * indent

        for node in body_nodes:
            if isinstance(node, ast.Assign):
                js_lines.append(self.dispatch_map[ast.Assign].compile(node))

            elif isinstance(node, ast.If):
                js_lines.append(self._compile_if_chain(node, do_declare=False))

            elif isinstance(node, ast.Return):
                value_js = self._compile_value(node.value) if node.value else 'undefined'  # noqa
                js_lines.append(f'return {value_js};')  # noqa

            elif isinstance(node, (ast.For, ast.While)):
                js_lines.append(self._compile_value(node))  # noqa

            elif isinstance(node, ast.Expr):
                js_lines.append(self._compile_value(node.value) + ';')  # noqa

            else:
                raise PYJSCompilerUnitException(f'Unsupported body node type: {type(node)}')

        indented_lines = []
        for line in js_lines:
            for sub_line in line.splitlines():
                if sub_line.strip():
                    indented_lines.append(pad + sub_line)
                else:
                    indented_lines.append(sub_line)

        return '\n'.join(indented_lines)

    # noinspection PyMethodMayBeStatic
    def _indent(self, code: str, spaces: int = 4) -> str:
        pad = ' ' * spaces
        return '\n'.join(pad + line if line.strip() else line for line in code.splitlines())
