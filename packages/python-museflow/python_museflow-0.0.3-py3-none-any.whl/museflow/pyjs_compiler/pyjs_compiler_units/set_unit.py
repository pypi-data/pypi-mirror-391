import ast
from typing import Any

from museflow.pyjs_compiler.pyjs_compiler_unit_abs import PYJSCompilerUnit, PYJSCompilerUnitException
from museflow.pyjs_compiler.pyjs_compiler_units.list_unit import ListUnit


class SetUnit(PYJSCompilerUnit):
    @property
    def variant(self) -> Any:
        return ast.Set

    def compile(self, node: ast.AST) -> str:
        if not isinstance(node, ast.Set):
            raise PYJSCompilerUnitException(f'Invalid node type: {type(node)}, expected: Set')

        for elt in node.elts:
            if not isinstance(elt, (ast.Constant, ast.Tuple)):
                raise PYJSCompilerUnitException(f'Unsupported set element type: {type(elt)}')

        as_list_node = ast.List(elts=node.elts, ctx=ast.Load())
        return ListUnit().compile(as_list_node)
