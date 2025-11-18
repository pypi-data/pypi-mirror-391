import ast
from typing import Any

from museflow.pyjs_compiler.pyjs_compiler_unit_abs import PYJSCompilerUnit, PYJSCompilerUnitException


class BoolUnit(PYJSCompilerUnit):
    @property
    def variant(self) -> Any:
        return ast.Constant

    def compile(self, node: ast.AST) -> str:
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.Not):
            value_js = self._compile_value(node.operand)  # noqa
            return f'!{value_js}'

        elif isinstance(node, ast.BoolOp):
            op_js = '&&' if isinstance(node.op, ast.And) else '||'
            values_js = [self._compile_value(v) for v in node.values]
            return f' {op_js} '.join(values_js)

        elif isinstance(node, ast.Compare):
            left_js = self._compile_value(node.left)  # noqa
            comparisons = []
            for op, comparator in zip(node.ops, node.comparators):
                right_js = self._compile_value(comparator)  # noqa
                op_str = self._map_compare_op(op)
                comparisons.append(f'{left_js} {op_str} {right_js}')
                left_js = self._compile_value(comparator)  # noqa
            return ' && '.join(comparisons)

        # Literal True/False
        elif isinstance(node, ast.Constant) and isinstance(node.value, bool):
            return 'true' if node.value else 'false'

        else:
            raise PYJSCompilerUnitException(f'Unsupported boolean node: {type(node)}')

    # noinspection PyMethodMayBeStatic
    def _map_compare_op(self, op: ast.cmpop) -> str:
        mapping = {
            ast.Eq: '==',
            ast.NotEq: '!=',
            ast.Lt: '<',
            ast.LtE: '<=',
            ast.Gt: '>',
            ast.GtE: '>=',
            ast.Is: '===',
            ast.IsNot: '!==',
            ast.In: 'in',
            ast.NotIn: '!(in)',
        }
        for py_op, js_op in mapping.items():
            if isinstance(op, py_op):
                return js_op
        raise PYJSCompilerUnitException(f'Unsupported comparison operator: {type(op)}')
