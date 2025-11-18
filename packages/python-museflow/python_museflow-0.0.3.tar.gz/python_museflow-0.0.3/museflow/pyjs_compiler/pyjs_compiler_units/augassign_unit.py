import ast
from typing import Any

from museflow.pyjs_compiler.pyjs_compiler_unit_abs import PYJSCompilerUnit, PYJSCompilerUnitException


class AugAssignUnit(PYJSCompilerUnit):
    @property
    def variant(self) -> Any:
        return ast.AugAssign

    def compile(self, node: ast.AugAssign) -> str:
        if not isinstance(node, ast.AugAssign):
            raise PYJSCompilerUnitException(f'Invalid node type: {type(node)}, expected: AugAssign')

        target_js = self._compile_target(node.target)
        value_js = self._compile_value(node.value)

        if isinstance(node.op, ast.FloorDiv):
            return f'{target_js} = Math.floor({target_js} / {value_js});'

        elif isinstance(node.op, ast.Pow):
            return f'{target_js} = Math.pow({target_js}, {value_js});'

        op_js = self._map_operator(node.op)
        return f'{target_js} {op_js}= {value_js};'

    # noinspection PyMethodMayBeStatic
    def _map_operator(self, op: ast.operator) -> str:
        mapping = {
            ast.Add: '+',
            ast.Sub: '-',
            ast.Mult: '*',
            ast.Div: '/',
            ast.Mod: '%',
            ast.Pow: '**',
            ast.BitOr: '|',
            ast.BitAnd: '&',
            ast.BitXor: '^',
            ast.LShift: '<<',
            ast.RShift: '>>',
        }

        for py_op, js_op in mapping.items():
            if isinstance(op, py_op):
                return js_op

        raise PYJSCompilerUnitException(f'Unsupported augmented operator: {type(op)}')
