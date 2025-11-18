import ast
import unittest

from museflow.pyjs_compiler.pyjs_compiler_unit_abs import PYJSCompilerUnitException
from museflow.pyjs_compiler.pyjs_compiler_units.name_unit import NameUnit


class TestNameUnit(unittest.TestCase):
    def setUp(self):
        self.unit = NameUnit()

    def test_simple_name(self):
        node = ast.Name(id='foo', ctx=ast.Load())
        res =self.unit.compile(node)
        self.assertEqual(res, 'foo')

    def test_another_name(self):
        node = ast.Name(id='bar', ctx=ast.Load())
        res =self.unit.compile(node)
        self.assertEqual(res, 'bar')

    def test_invalid_node_type(self):
        node = ast.Constant(value=123)
        with self.assertRaises(PYJSCompilerUnitException):
            self.unit.compile(node)

    def test_attribute_as_name_should_fail(self):
        node = ast.Attribute(value=ast.Name(id='foo', ctx=ast.Load()), attr='bar', ctx=ast.Load())
        with self.assertRaises(PYJSCompilerUnitException):
            self.unit.compile(node)

    def test_name_with_context_store(self):
        for ctx_type in (ast.Load, ast.Store, ast.Del):
            node = ast.Name(id='baz', ctx=ctx_type())
            res =self.unit.compile(node)
            self.assertEqual(res, 'baz')
