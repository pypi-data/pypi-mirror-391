import ast
import unittest

from museflow.pyjs_compiler.pyjs_compiler_unit_abs import PYJSCompilerUnitException
from museflow.pyjs_compiler.pyjs_compiler_units.expr_unit import ExprUnit


class TestExprUnit(unittest.TestCase):

    def setUp(self):
        self.unit = ExprUnit()

        def stub_compile_value(node: ast.AST) -> str:
            if isinstance(node, ast.Constant):
                if isinstance(node.value, str):
                    return f'"{node.value}"'
                if isinstance(node.value, (int, float)):
                    return str(node.value)
            elif isinstance(node, ast.Name) and node.id == 'print':
                # Stub out common function calls
                return 'console.log'
            # Stub out complex expressions based on type
            elif isinstance(node, ast.Call):
                return 'console.log("hello")'
            elif isinstance(node, ast.BinOp):
                return '5 + a'
            return 'compiled_expression_stub'

        if not hasattr(self.unit, '_compile_value'):
            self.unit._compile_value = stub_compile_value

    def test_string_literal_expr(self):
        node = ast.Expr(value=ast.Constant(value='hello world'))
        result = self.unit.compile(node)
        self.assertEqual(result, '"hello world";')

    def test_numeric_literal_expr(self):
        node = ast.Expr(value=ast.Constant(value=10))
        result = self.unit.compile(node)
        self.assertEqual(result, '10;')

    def test_call_expr(self):
        node = ast.Expr(value=ast.Call(
            func=ast.Name(id='print', ctx=ast.Load()),
            args=[ast.Constant(value='hello')],
            keywords=[]
        ))
        result = self.unit.compile(node)

        self.assertEqual('print("hello");', result)

    def test_invalid_node_type(self):
        with self.assertRaisesRegex(PYJSCompilerUnitException, r'Invalid node type'):
            self.unit.compile(
                ast.Assign(
                    targets=[],
                    value=ast.Constant(value=1)
                )
            )
