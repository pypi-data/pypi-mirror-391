import ast
from typing import Any
from museflow.pyjs_compiler.pyjs_compiler_unit_abs import PYJSCompilerUnit, PYJSCompilerUnitException

class UnaryOpUnit(PYJSCompilerUnit):
    @property
    def variant(self) -> Any:
        return ast.UnaryOp

    def compile(self, node: ast.UnaryOp) -> str:
        if not isinstance(node, ast.UnaryOp):
            raise PYJSCompilerUnitException(f'Expected UnaryOp, got {type(node)}')

        operand_js = self._compile_value(node.operand)  # noqa

        if isinstance(node.op, ast.USub):
            op_str = '-'
        elif isinstance(node.op, ast.UAdd):
            op_str = '+'
        elif isinstance(node.op, ast.Not):
            op_str = '!'
        elif isinstance(node.op, ast.Invert):
            op_str = '~'
        else:
            raise PYJSCompilerUnitException(f'Unsupported unary operator: {type(node.op)}')

        is_simple_operand = isinstance(node.operand, (ast.Name, ast.Constant))

        if not is_simple_operand:
            return f'{op_str}({operand_js})'
        else:
            return f'{op_str}{operand_js}'
