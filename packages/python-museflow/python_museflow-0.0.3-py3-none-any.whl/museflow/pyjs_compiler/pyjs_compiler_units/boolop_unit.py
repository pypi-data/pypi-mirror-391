import ast
from typing import Any

from museflow.pyjs_compiler.pyjs_compiler_unit_abs import PYJSCompilerUnit, PYJSCompilerUnitException


class BoolOpUnit(PYJSCompilerUnit):
    @property
    def variant(self) -> Any:
        return ast.BoolOp

    def compile(self, node: ast.AST) -> str:
        if not isinstance(node, ast.BoolOp):
            raise PYJSCompilerUnitException(f'Invalid node type: {type(node)}, expected: BoolOp')

        op_js = self._map_operator(node.op)

        values_js = [self._compile_value(v) for v in node.values]

        return f'({f' {op_js} '.join(values_js)})'

    # noinspection PyMethodMayBeStatic
    def _map_operator(self, op: ast.boolop) -> str:
        if isinstance(op, ast.And):
            return '&&'
        elif isinstance(op, ast.Or):
            return '||'
        else:
            raise PYJSCompilerUnitException(f'Unsupported boolean operator: {type(op)}')
