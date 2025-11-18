import ast

from museflow.pyjs_compiler.pyjs_compiler_unit_abs import PYJSCompilerUnit, PYJSCompilerUnitException


class NoneUnit(PYJSCompilerUnit):
    @property
    def variant(self):
        return ast.Constant  # dispatch for all constants

    def compile(self, node: ast.AST) -> str:
        if not isinstance(node, ast.Constant) or node.value is not None:
            raise PYJSCompilerUnitException(f'Invalid node type: {type(node)}, expected: None')
        return 'null'
