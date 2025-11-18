import ast
import unittest

from museflow.pyjs_compiler.pyjs_compiler_unit_abs import PYJSCompilerUnitException
from museflow.pyjs_compiler.pyjs_compiler_units.none_unit import NoneUnit


class TestNoneUnit(unittest.TestCase):
    def setUp(self):
        self.unit = NoneUnit()

    def test_simple_none(self):
        node = ast.Constant(value=None)
        res =self.unit.compile(node)
        self.assertEqual(res, 'null')

    def test_none_in_list(self):
        from museflow.pyjs_compiler.pyjs_compiler_units.list_unit import ListUnit
        node = ast.List(elts=[ast.Constant(value=None), ast.Constant(value=1)], ctx=ast.Load())
        res =ListUnit()._compile_element(node.elts[0])
        self.assertEqual(res, 'null')

    def test_none_invalid_node(self):
        node = ast.Constant(value=123)
        with self.assertRaises(PYJSCompilerUnitException):
            self.unit.compile(node)

    def test_none_invalid_type(self):
        node = ast.Name(id='x', ctx=ast.Load())
        with self.assertRaises(PYJSCompilerUnitException):
            self.unit.compile(node)
