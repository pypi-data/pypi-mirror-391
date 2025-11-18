import ast
from typing import Any

from museflow.pyjs_compiler.pyjs_compiler_unit_abs import PYJSCompilerUnit, PYJSCompilerUnitException


class FStringUnit(PYJSCompilerUnit):
    @property
    def variant(self) -> Any:
        return ast.JoinedStr

    def compile(self, node: ast.AST) -> str:
        if not isinstance(node, ast.JoinedStr):
            raise PYJSCompilerUnitException(f'Invalid node type: {type(node)}, expected JoinedStr')

        parts = []
        for value in node.values:
            if isinstance(value, ast.Constant):
                parts.append(value.value)
            elif isinstance(value, ast.FormattedValue):
                expr_js = self._compile_value(value.value)  # noqa
                parts.append(f"${{{expr_js}}}")
            else:
                raise PYJSCompilerUnitException(f'Unexpected node in f-string: {type(value)}')

        return f'`{"".join(parts)}`'
