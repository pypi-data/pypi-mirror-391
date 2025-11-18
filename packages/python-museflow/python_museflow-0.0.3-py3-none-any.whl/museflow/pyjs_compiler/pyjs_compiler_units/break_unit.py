import ast
from typing import Any

from museflow.pyjs_compiler.pyjs_compiler_unit_abs import PYJSCompilerUnit, PYJSCompilerUnitException


class BreakUnit(PYJSCompilerUnit):
    @property
    def variant(self) -> Any:
        return ast.Break

    def compile(self, node: ast.AST) -> str:
        if not isinstance(node, ast.Break):
            raise PYJSCompilerUnitException(f'Invalid node type: {type(node)}, expected: Break')
        return 'break;'
