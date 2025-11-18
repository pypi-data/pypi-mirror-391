import ast
import unittest

from museflow.pyjs_compiler.pyjs_compiler_unit_abs import PYJSCompilerUnitException
from museflow.pyjs_compiler.pyjs_compiler_units.set_unit import SetUnit


class TestSetUnit(unittest.TestCase):
    def setUp(self):
        self.unit = SetUnit()

    def test_empty_set(self):
        node = ast.Set(elts=[])
        res =self.unit.compile(node)
        self.assertEqual(res, '[]')

    def test_simple_set(self):
        node = ast.Set(elts=[ast.Constant(value=1), ast.Constant(value=2)])
        res =self.unit.compile(node)
        self.assertEqual(res, '[1, 2]')

    def test_set_with_strings(self):
        node = ast.Set(elts=[ast.Constant(value="a"), ast.Constant(value="b")])
        res =self.unit.compile(node)
        self.assertEqual(res, '["a", "b"]')

    def test_nested_set_elements(self):
        node = ast.Set(elts=[
            ast.Tuple(elts=[ast.Constant(value=1), ast.Constant(value=2)], ctx=ast.Load()),
            ast.Tuple(elts=[ast.Constant(value=3), ast.Constant(value=4)], ctx=ast.Load())
        ])
        res =self.unit.compile(node)
        self.assertEqual(res, '[[1, 2], [3, 4]]')

    def test_invalid_element(self):
        node = ast.Set(elts=[ast.Name(id='x', ctx=ast.Load())])
        with self.assertRaises(PYJSCompilerUnitException):
            self.unit.compile(node)
