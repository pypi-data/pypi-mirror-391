import ast
from typing import Any

from museflow.pyjs_compiler.pyjs_compiler_unit_abs import PYJSCompilerUnit, PYJSCompilerUnitException


class GetAttrUnit(PYJSCompilerUnit):
    @property
    def variant(self) -> Any:
        return ast.Attribute

    def compile(self, node: ast.AST) -> str:
        if not isinstance(node, ast.Attribute):
            raise PYJSCompilerUnitException(f'Invalid node type: {type(node)}, expected: Attribute')

        value_js = self._compile_value(node.value)  # noqa

        return f'{value_js}.{node.attr}'
