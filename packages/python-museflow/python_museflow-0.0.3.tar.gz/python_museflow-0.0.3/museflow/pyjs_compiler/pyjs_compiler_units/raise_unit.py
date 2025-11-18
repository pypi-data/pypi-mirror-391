import ast
from typing import Any

from museflow.pyjs_compiler.pyjs_compiler_unit_abs import PYJSCompilerUnit, PYJSCompilerUnitException


class RaiseUnit(PYJSCompilerUnit):
    @property
    def variant(self) -> Any:
        return ast.Raise

    def compile(self, node: ast.Raise) -> str:
        if not isinstance(node, ast.Raise):
            raise PYJSCompilerUnitException(f'Invalid node type: {type(node)}, expected: Raise')

        if node.exc:
            exc_js = self._compile_value(node.exc)  # noqa

            if isinstance(node.exc, ast.Call):
                return f'throw new {exc_js};'
            else:
                return f'throw {exc_js};'
        else:
            return 'throw undefined;'
