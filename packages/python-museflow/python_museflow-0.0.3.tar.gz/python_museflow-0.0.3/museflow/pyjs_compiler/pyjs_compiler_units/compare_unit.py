import ast
from typing import Any

from museflow.pyjs_compiler.pyjs_compiler_unit_abs import PYJSCompilerUnit, PYJSCompilerUnitException


class CompareUnit(PYJSCompilerUnit):
    @property
    def variant(self) -> Any:
        return ast.Compare

    def compile(self, node: ast.AST) -> str:
        if not isinstance(node, ast.Compare):
            raise PYJSCompilerUnitException(f'Invalid node type: {type(node)}, expected: Compare')

        comparisons = []
        current_left_js = self._compile_value(node.left)

        for op, comparator in zip(node.ops, node.comparators):
            right_js = self._compile_value(comparator)

            if isinstance(op, ast.In):
                comparison_js = f'{right_js}.includes({current_left_js})'
            elif isinstance(op, ast.NotIn):
                comparison_js = f'!{right_js}.includes({current_left_js})'

            else:
                op_js = self._map_operator(op)
                comparison_js = f'{current_left_js} {op_js} {right_js}'

            comparisons.append(comparison_js)

            current_left_js = right_js

        return ' && '.join(comparisons)

    # noinspection PyMethodMayBeStatic
    def _map_operator(self, op: ast.cmpop) -> str:
        mapping = {
            ast.Eq: '==',
            ast.NotEq: '!=',
            ast.Lt: '<',
            ast.LtE: '<=',
            ast.Gt: '>',
            ast.GtE: '>=',
            ast.Is: '===',
            ast.IsNot: '!=='
        }

        for py_op, js_op in mapping.items():
            if isinstance(op, py_op):
                return js_op

        raise PYJSCompilerUnitException(f'Unsupported comparison operator: {type(op)}')
