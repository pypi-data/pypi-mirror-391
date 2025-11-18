import ast
import unittest

from museflow.pyjs_compiler.pyjs_compiler_unit_abs import PYJSCompilerUnitException
from museflow.pyjs_compiler.pyjs_compiler_units.unaryop_unit import UnaryOpUnit


class TestUnaryOpUnit(unittest.TestCase):
    def setUp(self):
        self.unit = UnaryOpUnit()

        self.COMPLEX_STUB = 'a + 5'

        def stub_map_operator(op: ast.unaryop) -> str:
            mapping = {
                ast.UAdd: '+',
                ast.USub: '-',
                ast.Not: '!',
                ast.Invert: '~'
            }
            op_type = type(op)
            if op_type in mapping:
                return mapping[op_type]
            raise PYJSCompilerUnitException(f'Unsupported unary operator: {op_type}')

        def stub_compile_value(node: ast.AST) -> str:
            if isinstance(node, ast.Name):
                return node.id
            elif isinstance(node, ast.Constant):
                if isinstance(node.value, str):
                    return f'"{node.value}"'
                return str(node.value)

            if isinstance(node, ast.BinOp):
                return self.COMPLEX_STUB

            return 'compiled_expression_stub'

        if not hasattr(self.unit, '_map_operator'):
            self.unit._map_operator = stub_map_operator
        if not hasattr(self.unit, '_compile_value'):
            self.unit._compile_value = stub_compile_value

    def test_negation_on_variable(self):
        node = ast.UnaryOp(
            op=ast.USub(),
            operand=ast.Name(id='x', ctx=ast.Load())
        )
        self.assertEqual('-x', self.unit.compile(node))

    def test_positive_on_constant(self):
        node = ast.UnaryOp(
            op=ast.UAdd(),
            operand=ast.Constant(value=5)
        )
        self.assertEqual('+5', self.unit.compile(node))

    def test_logical_not(self):
        node = ast.UnaryOp(
            op=ast.Not(),
            operand=ast.Name(id='flag', ctx=ast.Load())
        )
        self.assertEqual('!flag', self.unit.compile(node))

    def test_bitwise_not(self):
        node = ast.UnaryOp(
            op=ast.Invert(),
            operand=ast.Name(id='mask', ctx=ast.Load())
        )
        self.assertEqual('~mask', self.unit.compile(node))

    def test_negation_on_complex_expression(self):
        binop_node = ast.BinOp(
            left=ast.Name(id='a', ctx=ast.Load()),
            op=ast.Add(),
            right=ast.Constant(value=5)
        )

        node = ast.UnaryOp(
            op=ast.USub(),
            operand=binop_node
        )
        self.assertEqual(f'-({self.COMPLEX_STUB})', self.unit.compile(node))

    def test_invalid_node_type(self):
        expected_regex = r'Expected UnaryOp, got <class \'ast\.Constant\'>'

        with self.assertRaisesRegex(PYJSCompilerUnitException, expected_regex):
            self.unit.compile(ast.Constant(value=1))
