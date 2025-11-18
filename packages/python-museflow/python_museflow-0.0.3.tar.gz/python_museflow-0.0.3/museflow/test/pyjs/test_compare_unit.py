import ast
import unittest

from museflow.pyjs_compiler.pyjs_compiler_unit_abs import PYJSCompilerUnitException
from museflow.pyjs_compiler.pyjs_compiler_units.compare_unit import CompareUnit


class TestCompareUnit(unittest.TestCase):
    def setUp(self):
        self.unit = CompareUnit()

        def stub_map_operator(op: ast.operator) -> str:
            mapping = {
                ast.Eq: '==',
                ast.NotEq: '!=',
                ast.Lt: '<',
                ast.LtE: '<=',
                ast.Gt: '>',
                ast.GtE: '>=',
                ast.Is: '===',
                ast.IsNot: '!==',
                ast.In: '.includes',
                ast.NotIn: '!.includes'
            }
            op_type = type(op)
            if op_type in mapping:
                if op_type in (ast.In, ast.NotIn):
                    return mapping[op_type]
                return mapping[op_type]
            raise PYJSCompilerUnitException(f'Unsupported operator: {op_type}')

        def stub_compile_value(node: ast.AST) -> str:
            if isinstance(node, ast.Name):
                return node.id
            elif isinstance(node, ast.Constant):
                return str(node.value)
            return 'compiled_stub'

        if not hasattr(self.unit, '_map_operator'):
            self.unit._map_operator = stub_map_operator
        if not hasattr(self.unit, '_compile_value'):
            self.unit._compile_value = stub_compile_value

    def test_single_less_than(self):
        node = ast.Compare(
            left=ast.Name(id='a', ctx=ast.Load()),
            ops=[ast.Lt()],
            comparators=[ast.Constant(value=10)]
        )
        self.assertEqual('a < 10', self.unit.compile(node))

    def test_single_equal_to(self):
        node = ast.Compare(
            left=ast.Name(id='b', ctx=ast.Load()),
            ops=[ast.Eq()],
            comparators=[ast.Constant(value=5)]
        )
        self.assertEqual('b == 5', self.unit.compile(node))

    def test_single_not_equal(self):
        node = ast.Compare(
            left=ast.Name(id='c', ctx=ast.Load()),
            ops=[ast.NotEq()],
            comparators=[ast.Name(id='d', ctx=ast.Load())]
        )
        self.assertEqual('c != d', self.unit.compile(node))

    def test_single_is_not_check(self):
        node = ast.Compare(
            left=ast.Name(id='x', ctx=ast.Load()),
            ops=[ast.IsNot()],
            comparators=[ast.Name(id='null', ctx=ast.Load())]
        )
        self.assertEqual('x !== null', self.unit.compile(node))

    def test_chained_comparisons(self):
        node = ast.Compare(
            left=ast.Constant(value=0),
            ops=[ast.Lt(), ast.LtE()],
            comparators=[ast.Name(id='x', ctx=ast.Load()), ast.Constant(value=10)]
        )

        self.assertEqual('0 < x && x <= 10', self.unit.compile(node))

    def test_triple_chained_comparisons(self):
        node = ast.Compare(
            left=ast.Name(id='a', ctx=ast.Load()),
            ops=[ast.Eq(), ast.NotEq()],
            comparators=[ast.Name(id='b', ctx=ast.Load()), ast.Name(id='c', ctx=ast.Load())]
        )

        self.assertEqual('a == b && b != c', self.unit.compile(node))  # New

    def test_in_operator(self):
        node = ast.Compare(
            left=ast.Name(id='item', ctx=ast.Load()),
            ops=[ast.In()],
            comparators=[ast.Name(id='arr', ctx=ast.Load())]
        )
        # Expected: arr.includes(item)
        self.assertEqual('arr.includes(item)', self.unit.compile(node))

    def test_not_in_operator(self):
        node = ast.Compare(
            left=ast.Name(id='item', ctx=ast.Load()),
            ops=[ast.NotIn()],
            comparators=[ast.Name(id='arr', ctx=ast.Load())]
        )
        self.assertEqual('!arr.includes(item)', self.unit.compile(node))

    def test_invalid_node_type(self):
        with self.assertRaisesRegex(PYJSCompilerUnitException, r'Invalid node type'):
            self.unit.compile(ast.Constant(value=1))
