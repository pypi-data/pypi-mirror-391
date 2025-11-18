import ast
from typing import Any

from museflow.pyjs_compiler.pyjs_compiler_unit_abs import PYJSCompilerUnit, PYJSCompilerUnitException


class FloatUnit(PYJSCompilerUnit):
    @property
    def variant(self) -> Any:
        return ast.Constant

    def compile(self, node: ast.AST) -> str:
        if not isinstance(node, ast.Constant) or not isinstance(node.value, float):
            raise PYJSCompilerUnitException(f'Invalid node type: {type(node)}, expected: float')
        return str(node.value)
