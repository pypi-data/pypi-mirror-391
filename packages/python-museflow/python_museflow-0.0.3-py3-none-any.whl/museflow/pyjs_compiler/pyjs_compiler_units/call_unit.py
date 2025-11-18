import ast
from typing import Any

from museflow.pyjs_compiler.pyjs_compiler_unit_abs import PYJSCompilerUnit, PYJSCompilerUnitException


class CallUnit(PYJSCompilerUnit):
    @property
    def variant(self) -> Any:
        return ast.Call

    def compile(self, node: ast.AST) -> str:
        if not isinstance(node, ast.Call):
            raise PYJSCompilerUnitException(f'Invalid node type: {type(node)}, expected Call')

        func_js = self._compile_value(node.func)  # noqa

        args_js = ', '.join(self._compile_value(arg) for arg in node.args)  # noqa

        return f'{func_js}({args_js})'

    # noinspection PyMethodMayBeStatic
    def _compile_node(self, node: ast.AST) -> str:
        if isinstance(node, ast.Expr):
            return self._compile_node(node.value)  # noqa

        for variant, unit in self.dispatch_map.items():
            if isinstance(variant, (tuple, list)):
                if isinstance(node, tuple(variant)):
                    return unit.compile(node)
            else:
                if isinstance(node, variant):
                    return unit.compile(node)

        raise PYJSCompilerUnitException(f'Unsupported AST node type: {type(node)}')
