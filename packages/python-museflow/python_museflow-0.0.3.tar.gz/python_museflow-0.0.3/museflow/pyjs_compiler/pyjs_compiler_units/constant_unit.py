import ast

from museflow.pyjs_compiler.pyjs_compiler_unit_abs import PYJSCompilerUnit, PYJSCompilerUnitException


class ConstantUnit(PYJSCompilerUnit):
    @property
    def variant(self):
        return ast.Constant  # handles all constants

    def compile(self, node: ast.AST) -> str:
        if not isinstance(node, ast.Constant):
            raise PYJSCompilerUnitException(f'Invalid node type: {type(node)}, expected: Constant')

        value = node.value
        if value is None:
            return 'null'
        elif isinstance(value, bool):
            return 'true' if value else 'false'
        elif isinstance(value, str):
            escaped = value.replace('"', '\\"')
            return f'"{escaped}"'
        elif isinstance(value, (int, float)):
            return str(value)
        else:
            raise PYJSCompilerUnitException(f'Unsupported constant type: {type(value)}')
