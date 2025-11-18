import ast
from typing import Any

from museflow.pyjs_compiler.pyjs_compiler_unit_abs import PYJSCompilerUnit, PYJSCompilerUnitException


class NameUnit(PYJSCompilerUnit):
    @property
    def variant(self) -> Any:
        return ast.Name

    def compile(self, node: ast.AST) -> str:
        if not isinstance(node, ast.Name):
            raise PYJSCompilerUnitException(f'Invalid node type: {type(node)}, expected: Name')
        return node.id
