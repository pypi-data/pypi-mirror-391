import ast
import unittest

from museflow.pyjs_compiler.pyjs_compiler_unit_abs import PYJSCompilerUnitException
from museflow.pyjs_compiler.pyjs_compiler_units.augassign_unit import AugAssignUnit


class TestAugAssignUnit(unittest.TestCase):
    def setUp(self):
        self.unit = AugAssignUnit()

    def test_add_operator(self):
        node = ast.AugAssign(
            target=ast.Name(id='x', ctx=ast.Store()),
            op=ast.Add(),
            value=ast.Constant(value=5)
        )
        result = self.unit.compile(node)
        self.assertEqual('x += 5;', result)

    def test_subtract_operator(self):
        node = ast.AugAssign(
            target=ast.Name(id='count', ctx=ast.Store()),
            op=ast.Sub(),
            value=ast.Constant(value=1)
        )
        result = self.unit.compile(node)
        # Swapped
        self.assertEqual('count -= 1;', result)

    def test_multiply_operator(self):
        node = ast.AugAssign(
            target=ast.Name(id='total', ctx=ast.Store()),
            op=ast.Mult(),
            value=ast.Name(id='rate', ctx=ast.Load())
        )
        result = self.unit.compile(node)
        self.assertEqual('total *= rate;', result)

    def test_bitwise_and_shift_operators(self):
        node_and = ast.AugAssign(target=ast.Name(id='mask', ctx=ast.Store()), op=ast.BitAnd(), value=ast.Constant(value=0xFF))
        node_lshift = ast.AugAssign(target=ast.Name(id='v', ctx=ast.Store()), op=ast.LShift(), value=ast.Constant(value=2))

        self.assertEqual('mask &= 255;', self.unit.compile(node_and))
        self.assertEqual('v <<= 2;', self.unit.compile(node_lshift))

    def test_attribute_target(self):
        node = ast.AugAssign(
            target=ast.Attribute(
                value=ast.Name(id='data', ctx=ast.Load()),
                attr='counter',
                ctx=ast.Store()
            ),
            op=ast.Add(),
            value=ast.Constant(value=1)
        )
        result = self.unit.compile(node)
        self.assertEqual('data.counter += 1;', result)

    def test_subscript_target(self):
        subscript_target = ast.Subscript(
            value=ast.Name(id='arr', ctx=ast.Load()),
            slice=ast.Constant(value=0),
            ctx=ast.Store()
        )

        node = ast.AugAssign(
            target=subscript_target,
            op=ast.Sub(),
            value=ast.Constant(value=5)
        )
        result = self.unit.compile(node)
        self.assertEqual('arr[0] -= 5;', result)

    def test_power_operator(self):
        node = ast.AugAssign(
            target=ast.Name(id='p', ctx=ast.Store()),
            op=ast.Pow(),
            value=ast.Constant(value=2)
        )
        result = self.unit.compile(node)
        self.assertEqual('p = Math.pow(p, 2);', result)

    def test_floor_division_operator(self):
        node = ast.AugAssign(
            target=ast.Name(id='num', ctx=ast.Store()),
            op=ast.FloorDiv(),
            value=ast.Constant(value=3)
        )
        result = self.unit.compile(node)

        expected_js = 'num = Math.floor(num / 3);'
        self.assertEqual(expected_js, result)

    def test_invalid_operator(self):
        class UnsupportedOp(ast.operator):
            pass

        node = ast.AugAssign(
            target=ast.Name(id='z', ctx=ast.Store()),
            op=UnsupportedOp(),
            value=ast.Constant(value=10)
        )
        with self.assertRaisesRegex(PYJSCompilerUnitException, r'Unsupported augmented operator'):
            self.unit.compile(node)
