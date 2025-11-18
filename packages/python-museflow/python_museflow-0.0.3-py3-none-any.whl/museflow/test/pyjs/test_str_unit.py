import ast
import unittest

from museflow.pyjs_compiler.pyjs_compiler_unit_abs import PYJSCompilerUnitException
from museflow.pyjs_compiler.pyjs_compiler_units.str_unit import StrUnit


class TestStrUnit(unittest.TestCase):
    def setUp(self):
        self.unit = StrUnit()

    def test_valid_string(self):
        node = ast.Constant(value="hello world")
        res =self.unit.compile(node)
        self.assertEqual(res, '"hello world"')

    def test_escaped_quotes(self):
        node = ast.Constant(value='He said "hi"')
        res =self.unit.compile(node)
        self.assertEqual(res, '"He said "hi""')

    def test_invalid_type_int(self):
        node = ast.Constant(value=123)
        with self.assertRaises(PYJSCompilerUnitException):
            self.unit.compile(node)

    def test_invalid_node(self):
        node = ast.Name(id="x", ctx=ast.Load())
        with self.assertRaises(PYJSCompilerUnitException):
            self.unit.compile(node)
