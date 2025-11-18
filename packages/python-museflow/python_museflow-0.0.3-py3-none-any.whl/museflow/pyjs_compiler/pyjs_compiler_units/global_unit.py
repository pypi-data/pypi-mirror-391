import ast

from museflow.pyjs_compiler.pyjs_compiler_unit_abs import PYJSCompilerUnit, PYJSCompilerUnitException


class GlobalUnit(PYJSCompilerUnit):
    @property
    def variant(self):
        return ast.Global

    def compile(self, node: ast.AST) -> None:
        raise PYJSCompilerUnitException('Python "global" statement is not allowed !')
