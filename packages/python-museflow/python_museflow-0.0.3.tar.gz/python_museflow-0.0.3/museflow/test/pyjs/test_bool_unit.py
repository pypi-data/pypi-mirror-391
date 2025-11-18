import ast
import unittest

from museflow.pyjs_compiler.pyjs_compiler_unit_abs import PYJSCompilerUnitException
from museflow.pyjs_compiler.pyjs_compiler_units.bool_unit import BoolUnit


class TestBoolUnit(unittest.TestCase):
    def setUp(self):
        self.unit = BoolUnit()

    def test_true(self):
        node = ast.Constant(value=True)
        res =self.unit.compile(node)
        self.assertEqual(res, 'true')

    def test_false(self):
        node = ast.Constant(value=False)
        res =self.unit.compile(node)
        self.assertEqual(res, 'false')

    def test_invalid_type(self):
        node = ast.Constant(value=123)
        with self.assertRaises(PYJSCompilerUnitException):
            self.unit.compile(node)

    def test_invalid_node(self):
        node = ast.Name(id='Invalid', ctx=ast.Load())
        with self.assertRaises(PYJSCompilerUnitException):
            self.unit.compile(node)
