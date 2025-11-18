import unittest
import ast

from museflow.pyjs_compiler.pyjs_compiler_unit_abs import PYJSCompilerUnitException
from museflow.pyjs_compiler.pyjs_compiler_units.continue_unit import ContinueUnit


class TestContinueUnit(unittest.TestCase):

    def setUp(self):
        self.unit = ContinueUnit()

    def test_simple_continue(self):
        node = ast.Continue()
        self.assertEqual('continue;', self.unit.compile(node))

    def test_invalid_node_type(self):
        with self.assertRaisesRegex(PYJSCompilerUnitException, r'Invalid node type'):
            self.unit.compile(ast.Break())
