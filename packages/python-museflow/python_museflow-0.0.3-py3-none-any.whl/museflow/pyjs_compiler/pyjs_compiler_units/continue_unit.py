import ast
from typing import Any

from museflow.pyjs_compiler.pyjs_compiler_unit_abs import PYJSCompilerUnit, PYJSCompilerUnitException


class ContinueUnit(PYJSCompilerUnit):
    @property
    def variant(self) -> Any:
        return ast.Continue

    def compile(self, node: ast.AST) -> str:
        if not isinstance(node, ast.Continue):
            raise PYJSCompilerUnitException(f'Invalid node type: {type(node)}, expected: Continue')
        return 'continue;'
