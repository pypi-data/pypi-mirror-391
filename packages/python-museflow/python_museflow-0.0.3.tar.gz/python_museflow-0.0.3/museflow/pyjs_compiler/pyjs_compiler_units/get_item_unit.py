import ast
from typing import Any

from museflow.pyjs_compiler.pyjs_compiler_unit_abs import PYJSCompilerUnit, PYJSCompilerUnitException


class GetItemUnit(PYJSCompilerUnit):
    @property
    def variant(self) -> Any:
        return ast.Subscript

    def compile(self, node: ast.AST) -> str:
        if not isinstance(node, ast.Subscript):
            raise PYJSCompilerUnitException(f'Invalid node type: {type(node)}, expected: Subscript')

        obj_js = self._compile_value(node.value)  # noqa
        key_js = self._compile_value(node.slice)  # noqa

        return f'{obj_js}[{key_js}]'
