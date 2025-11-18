import ast
import unittest

from museflow.pyjs_compiler.pyjs_compiler_unit_abs import PYJSCompilerUnitException
from museflow.pyjs_compiler.pyjs_compiler_units.call_unit import CallUnit


class TestCallUnit(unittest.TestCase):
    def setUp(self):
        self.unit = CallUnit()

    def test_simple_call(self):
        node = ast.Call(func=ast.Name(id='foo', ctx=ast.Load()), args=[], keywords=[])
        res =self.unit.compile(node)
        self.assertEqual(res, 'foo()')

    def test_call_with_args(self):
        node = ast.Call(
            func=ast.Name(id='sum', ctx=ast.Load()),
            args=[ast.Constant(value=1), ast.Constant(value=2)],
            keywords=[]
        )
        res =self.unit.compile(node)
        self.assertEqual(res, 'sum(1, 2)')

    def test_call_with_nested_call(self):
        node = ast.Call(
            func=ast.Name(id='outer', ctx=ast.Load()),
            args=[
                ast.Call(func=ast.Name(id='inner', ctx=ast.Load()), args=[], keywords=[])
            ],
            keywords=[]
        )
        res =self.unit.compile(node)
        self.assertEqual(res, 'outer(inner())')

    def test_invalid_node(self):
        node = ast.Constant(value=123)
        with self.assertRaises(PYJSCompilerUnitException):
            self.unit.compile(node)

    def test_complex_nested_call(self):
        """
        Python:
            foo(1, bar(True, [2, 3], baz(4)), "hello", None)
        JS (expected):
            foo(1, bar(true, [2, 3], baz(4)), "hello", null)
        """
        node = ast.Call(
            func=ast.Name(id='foo', ctx=ast.Load()),
            args=[
                ast.Constant(value=1),
                ast.Call(
                    func=ast.Name(id='bar', ctx=ast.Load()),
                    args=[
                        ast.Constant(value=True),
                        ast.List(elts=[ast.Constant(value=2), ast.Constant(value=3)], ctx=ast.Load()),
                        ast.Call(func=ast.Name(id='baz', ctx=ast.Load()), args=[ast.Constant(value=4)], keywords=[])
                    ],
                    keywords=[]
                ),
                ast.Constant(value="hello"),
                ast.Constant(value=None)
            ],
            keywords=[]
        )

        res =self.unit.compile(node)
        expected = 'foo(1, bar(true, [2, 3], baz(4)), "hello", null)'
        self.assertEqual(expected, res)
