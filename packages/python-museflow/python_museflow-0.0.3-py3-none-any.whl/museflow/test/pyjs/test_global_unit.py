import ast
import unittest

from museflow.pyjs_compiler.pyjs_compiler_unit_abs import PYJSCompilerUnitException
from museflow.pyjs_compiler.pyjs_compiler_units.global_unit import GlobalUnit


class TestGlobalUnit(unittest.TestCase):
    def setUp(self):
        self.unit = GlobalUnit()

    def test_single_global_raises_exception(self):
        node = ast.Global(names=['foo'])
        with self.assertRaises(PYJSCompilerUnitException) as cm:
            self.unit.compile(node)
        self.assertIn('not allowed', str(cm.exception))

    def test_multiple_globals_raises_exception(self):
        node = ast.Global(names=['foo', 'bar', 'baz'])
        with self.assertRaises(PYJSCompilerUnitException) as cm:
            self.unit.compile(node)
        self.assertIn('not allowed', str(cm.exception))

    def test_invalid_node_raises_exception(self):
        node = ast.Constant(value=42)
        with self.assertRaises(PYJSCompilerUnitException):
            self.unit.compile(node)
