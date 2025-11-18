import ast
from typing import Any

from museflow.pyjs_compiler.pyjs_compiler_unit_abs import PYJSCompilerUnit, PYJSCompilerUnitException


class BinOpUnit(PYJSCompilerUnit):
    @property
    def variant(self) -> Any:
        return ast.BinOp

    # noinspection PyMethodMayBeStatic
    def _map_operator(self, op: ast.operator) -> str:
        """
        Maps simple Python arithmetic operators to JavaScript equivalents.
        Does NOT handle Pow or FloorDiv, as they require function calls.
        """
        mapping = {
            ast.Add: '+',
            ast.Sub: '-',
            ast.Mult: '*',
            ast.Div: '/',
            ast.Mod: '%',
        }

        op_type = type(op)
        if op_type in mapping:
            return mapping[op_type]

        raise PYJSCompilerUnitException(f'Unsupported binary operator: {op_type}')

    def compile(self, node: ast.AST) -> str:
        if not isinstance(node, ast.BinOp):
            raise PYJSCompilerUnitException(f'Invalid node type: {type(node)}, expected BinOp')

        left_js = self._compile_value(node.left)
        right_js = self._compile_value(node.right)

        if isinstance(node.op, ast.FloorDiv):
            return f'Math.floor({left_js} / {right_js})'

        if isinstance(node.op, ast.Pow):
            return f'Math.pow({left_js}, {right_js})'

        op_js = self._map_operator(node.op)

        return f'{left_js} {op_js} {right_js}'
