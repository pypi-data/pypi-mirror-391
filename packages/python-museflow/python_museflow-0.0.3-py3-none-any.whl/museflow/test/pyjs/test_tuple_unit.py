import ast
import ast
import unittest

from museflow.pyjs_compiler.pyjs_compiler_unit_abs import PYJSCompilerUnitException
from museflow.pyjs_compiler.pyjs_compiler_units.tuple_unit import TupleUnit


class TestTupleUnit(unittest.TestCase):
    def setUp(self):
        self.unit = TupleUnit()

    def test_empty_tuple(self):
        node = ast.Tuple(elts=[], ctx=ast.Load())
        res = self.unit.compile(node)
        self.assertEqual(res, '[]')

    def test_single_element_tuple(self):
        node = ast.Tuple(elts=[ast.Constant(value=1)], ctx=ast.Load())
        res = self.unit.compile(node)
        self.assertEqual(res, '[1]')

    def test_multiple_elements_tuple(self):
        node = ast.Tuple(elts=[ast.Constant(value=1), ast.Constant(value=2), ast.Constant(value=3)], ctx=ast.Load())
        res = self.unit.compile(node)
        self.assertEqual(res, '[1, 2, 3]')

    def test_nested_tuple(self):
        node = ast.Tuple(
            elts=[ast.Constant(value=1), ast.Tuple(elts=[ast.Constant(value=2), ast.Constant(value=3)], ctx=ast.Load())],
            ctx=ast.Load()
        )
        res = self.unit.compile(node)
        self.assertEqual(res, '[1, [2, 3]]')

    def test_invalid_node(self):
        node = ast.Constant(value=123)
        with self.assertRaises(PYJSCompilerUnitException):
            self.unit.compile(node)


class TestTupleUnitMultidimensional(unittest.TestCase):
    def setUp(self):
        self.unit = TupleUnit()

    def test_multidimensional_tuple(self):
        node = ast.Tuple(
            elts=[
                ast.Tuple(elts=[ast.Constant(value=1), ast.Constant(value=2)], ctx=ast.Load()),
                ast.Tuple(elts=[ast.Constant(value=3), ast.Constant(value=4)], ctx=ast.Load())
            ],
            ctx=ast.Load()
        )
        res = self.unit.compile(node)
        self.assertEqual(res, '[[1, 2], [3, 4]]')

    def test_mixed_nested(self):
        node = ast.Tuple(
            elts=[
                ast.Constant(value=1),
                ast.Tuple(elts=[ast.Constant(value=2), ast.Constant(value=3)], ctx=ast.Load()),
                ast.List(elts=[ast.Constant(value=4), ast.Constant(value=5)], ctx=ast.Load())
            ],
            ctx=ast.Load()
        )
        res = self.unit.compile(node)
        self.assertEqual(res, '[1, [2, 3], [4, 5]]')

    def test_complex_mixed_nested(self):
        node = ast.Tuple(
            elts=[
                ast.Constant(value=1),
                ast.Tuple(elts=[ast.Constant(value=True), ast.Constant(value=None)], ctx=ast.Load()),
                ast.List(elts=[ast.Constant(value=2), ast.Constant(value="hello")], ctx=ast.Load()),
                ast.Call(func=ast.Name(id='foo', ctx=ast.Load()), args=[ast.Constant(value=3)], keywords=[]),
                ast.Tuple(
                    elts=[
                        ast.Tuple(elts=[ast.Constant(value=4), ast.Constant(value=5)], ctx=ast.Load()),
                        ast.List(
                            elts=[
                                ast.Constant(value=False),
                                ast.Call(func=ast.Name(id='bar', ctx=ast.Load()), args=[], keywords=[])
                            ],
                            ctx=ast.Load()
                        )
                    ],
                    ctx=ast.Load()
                )
            ],
            ctx=ast.Load()
        )

        res = self.unit.compile(node)
        expected = '[1, [true, null], [2, "hello"], foo(3), [[4, 5], [false, bar()]]]'
        self.assertEqual(expected, res)
