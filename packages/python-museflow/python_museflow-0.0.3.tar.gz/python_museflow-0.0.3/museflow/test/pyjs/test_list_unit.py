import ast
import unittest

from museflow.pyjs_compiler.pyjs_compiler_unit_abs import PYJSCompilerUnitException
from museflow.pyjs_compiler.pyjs_compiler_units.list_unit import ListUnit


class TestListUnit(unittest.TestCase):
    def setUp(self):
        self.unit = ListUnit()

    def test_empty_list(self):
        node = ast.List(elts=[], ctx=ast.Load())
        res =self.unit.compile(node)
        self.assertEqual(res, '[]')

    def test_single_element_list(self):
        node = ast.List(elts=[ast.Constant(value=1)], ctx=ast.Load())
        res =self.unit.compile(node)
        self.assertEqual(res, '[1]')

    def test_multiple_elements_list(self):
        node = ast.List(elts=[ast.Constant(value=1), ast.Constant(value=2), ast.Constant(value=3)], ctx=ast.Load())
        res =self.unit.compile(node)
        self.assertEqual(res, '[1, 2, 3]')

    def test_nested_list(self):
        node = ast.List(
            elts=[ast.Constant(value=1), ast.List(elts=[ast.Constant(value=2), ast.Constant(value=3)], ctx=ast.Load())],
            ctx=ast.Load()
        )
        res =self.unit.compile(node)
        self.assertEqual(res, '[1, [2, 3]]')

    def test_invalid_node(self):
        node = ast.Constant(value=123)
        with self.assertRaises(PYJSCompilerUnitException):
            self.unit.compile(node)


class TestListUnitMultidimensional(unittest.TestCase):
    def setUp(self):
        self.unit = ListUnit()

    def test_multidimensional_list(self):
        node = ast.List(
            elts=[
                ast.List(elts=[ast.Constant(value=1), ast.Constant(value=2)], ctx=ast.Load()),
                ast.List(elts=[ast.Constant(value=3), ast.Constant(value=4)], ctx=ast.Load())
            ],
            ctx=ast.Load()
        )
        res =self.unit.compile(node)
        self.assertEqual(res, '[[1, 2], [3, 4]]')

    def test_mixed_nested(self):
        node = ast.List(
            elts=[
                ast.Constant(value=1),
                ast.Tuple(elts=[ast.Constant(value=2), ast.Constant(value=3)], ctx=ast.Load()),
                ast.List(elts=[ast.Constant(value=4), ast.Constant(value=5)], ctx=ast.Load())
            ],
            ctx=ast.Load()
        )
        res =self.unit.compile(node)
        self.assertEqual(res, '[1, [2, 3], [4, 5]]')
