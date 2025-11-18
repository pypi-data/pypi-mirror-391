import ast

from museflow.pyjs_compiler.pyjs_compiler_unit_abs import PYJSCompilerUnit, PYJSCompilerUnitException


class ExprUnit(PYJSCompilerUnit):
    @property
    def variant(self):
        return ast.Expr

    def compile(self, node: ast.AST) -> str:
        if not isinstance(node, ast.Expr):
            raise PYJSCompilerUnitException(f'Invalid node type: {type(node)}, expected: Expr')
        return self._compile_value(node.value) + ';'  # noqa

    def _compile_value(self, node: ast.AST) -> str:
        for unit in self.dispatch_map.values():
            variant = unit.variant
            if isinstance(variant, tuple):
                if isinstance(node, variant):
                    return unit.compile(node)
            else:
                if isinstance(node, variant):
                    return unit.compile(node)

        raise PYJSCompilerUnitException(f'Unsupported AST node type: {type(node)}, node dump: {ast.dump(node, indent=2)}')
