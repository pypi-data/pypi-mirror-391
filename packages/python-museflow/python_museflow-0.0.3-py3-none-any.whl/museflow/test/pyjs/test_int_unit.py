import ast
import unittest

from museflow.pyjs_compiler.pyjs_compiler_units.int_unit import IntUnit


class TestIntUnit(unittest.TestCase):
    def setUp(self):
        self.unit = IntUnit()

    def test_simple_int(self):
        node = ast.Constant(value=67)
        res = self.unit.compile(node)
        self.assertEqual(res, '67')

    def test_invalid_node(self):
        with self.assertRaises(Exception):
            self.unit.compile(ast.Constant(value='Invalid'))
