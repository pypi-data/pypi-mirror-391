import ast
import unittest

from museflow.pyjs_compiler.pyjs_compiler_unit_abs import PYJSCompilerUnitException
from museflow.pyjs_compiler.pyjs_compiler_units.binop_unit import BinOpUnit


class TestBinOpUnit(unittest.TestCase):
    def setUp(self):
        self.unit = BinOpUnit()

        def stub_map_operator(op: ast.operator) -> str:
            op_map = {
                ast.Add: '+', ast.Sub: '-', ast.Mult: '*',
                ast.Div: '/', ast.Mod: '%'
            }
            op_type = type(op)
            if op_type in op_map:
                return op_map[op_type]
            raise PYJSCompilerUnitException(f'Unsupported operator: {op_type}')

        def stub_compile_value(node: ast.AST) -> str:
            if isinstance(node, ast.Constant):
                return str(node.value)
            if isinstance(node, ast.Name):
                return node.id
            if isinstance(node, (ast.List, ast.Tuple)) and not node.elts:
                return '[]'
            return 'compiled_stub'

        if not hasattr(self.unit, '_map_operator'):
            self.unit._map_operator = stub_map_operator
        if not hasattr(self.unit, '_compile_value'):
            self.unit._compile_value = stub_compile_value

    def test_addition(self):
        node = ast.BinOp(left=ast.Constant(value=5), op=ast.Add(), right=ast.Name(id='a', ctx=ast.Load()))
        # assertEqual(expected, actual)
        self.assertEqual('5 + a', self.unit.compile(node))

    def test_multiplication(self):
        node = ast.BinOp(left=ast.Name(id='x', ctx=ast.Load()), op=ast.Mult(), right=ast.Constant(value=20))
        self.assertEqual('x * 20', self.unit.compile(node))

    def test_division(self):
        node = ast.BinOp(left=ast.Name(id='total', ctx=ast.Load()), op=ast.Div(), right=ast.Constant(value=10))
        self.assertEqual('total / 10', self.unit.compile(node))

    def test_modulus(self):
        node = ast.BinOp(left=ast.Name(id='n', ctx=ast.Load()), op=ast.Mod(), right=ast.Constant(value=2))
        self.assertEqual('n % 2', self.unit.compile(node))

    def test_power(self):
        node = ast.BinOp(left=ast.Name(id='base', ctx=ast.Load()), op=ast.Pow(), right=ast.Constant(value=3))
        self.assertEqual('Math.pow(base, 3)', self.unit.compile(node))

    def test_floor_division(self):
        node = ast.BinOp(left=ast.Constant(value=15), op=ast.FloorDiv(), right=ast.Constant(value=4))
        self.assertEqual('Math.floor(15 / 4)', self.unit.compile(node))

    def test_complex_operands(self):
        node = ast.BinOp(left=ast.List(elts=[], ctx=ast.Load()), op=ast.Sub(), right=ast.Tuple(elts=[], ctx=ast.Load()))
        self.assertEqual('[] - []', self.unit.compile(node))

    def test_invalid_node_type(self):
        with self.assertRaisesRegex(PYJSCompilerUnitException, r'Invalid node type'):
            self.unit.compile(ast.Constant(value=1))
