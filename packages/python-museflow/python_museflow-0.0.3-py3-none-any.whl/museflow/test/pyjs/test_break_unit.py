import unittest
import ast

from museflow.pyjs_compiler.pyjs_compiler_unit_abs import PYJSCompilerUnitException
from museflow.pyjs_compiler.pyjs_compiler_units.break_unit import BreakUnit


class TestBreakUnit(unittest.TestCase):
    def setUp(self):
        self.unit = BreakUnit()

    def test_simple_break(self):
        node = ast.Break()
        self.assertEqual('break;', self.unit.compile(node))

    def test_invalid_node_type(self):
        with self.assertRaisesRegex(PYJSCompilerUnitException, r'Invalid node type'):
            self.unit.compile(ast.Continue())
