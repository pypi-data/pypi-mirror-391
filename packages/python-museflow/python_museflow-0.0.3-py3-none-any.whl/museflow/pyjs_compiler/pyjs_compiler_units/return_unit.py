import ast
from typing import Any

from museflow.pyjs_compiler.pyjs_compiler_unit_abs import PYJSCompilerUnit, PYJSCompilerUnitException

class ReturnUnit(PYJSCompilerUnit):
    @property
    def variant(self) -> Any:
        return ast.Return

    def compile(self, node: ast.AST) -> str:
        if not isinstance(node, ast.Return):
            raise PYJSCompilerUnitException(f'Invalid node type: {type(node)}, expected: Return')

        if node.value is None:
            return 'return;'

        value_js = self._compile_value(node.value)  # noqa

        if isinstance(node.value, (ast.BinOp, ast.BoolOp, ast.Compare, ast.Call)):
            if not value_js.startswith('('):
                value_js = f'({value_js})'

        return f'return {value_js};'
