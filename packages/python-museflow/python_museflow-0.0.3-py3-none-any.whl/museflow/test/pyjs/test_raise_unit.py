import ast
import unittest

from museflow.pyjs_compiler.pyjs_compiler_unit_abs import PYJSCompilerUnitException
from museflow.pyjs_compiler.pyjs_compiler_units.raise_unit import RaiseUnit


class TestRaiseUnit(unittest.TestCase):
    def setUp(self):
        self.unit = RaiseUnit()

    def test_simple_raise(self):
        node = ast.Raise(
            exc=ast.Call(func=ast.Name(id='Exception', ctx=ast.Load()), args=[], keywords=[]),
            cause=None
        )
        res =self.unit.compile(node)
        self.assertEqual(res, 'throw new Exception();')

    def test_raise_with_message(self):
        node = ast.Raise(
            exc=ast.Call(
                func=ast.Name(id='Exception', ctx=ast.Load()),
                args=[ast.Constant(value='Error occurred')],
                keywords=[]
            ),
            cause=None
        )
        res =self.unit.compile(node)
        self.assertEqual(res, 'throw new Exception("Error occurred");')

    def test_raise_variable_exception(self):
        node = ast.Raise(
            exc=ast.Name(id='my_error', ctx=ast.Load()),
            cause=None
        )
        res =self.unit.compile(node)
        self.assertEqual(res, 'throw my_error;')

    def test_invalid_node(self):
        node = ast.Constant(value=123)
        with self.assertRaises(PYJSCompilerUnitException):
            self.unit.compile(node)

    def test_nested_raise_calls(self):
        node1 = ast.Raise(
            exc=ast.Call(
                func=ast.Name(id='CustomError', ctx=ast.Load()),
                args=[
                    ast.Call(func=ast.Name(id='foo', ctx=ast.Load()), args=[ast.Constant(42)], keywords=[]),
                    ast.Call(func=ast.Name(id='bar', ctx=ast.Load()), args=[], keywords=[]),
                ],
                keywords=[]
            )
        )
        res1 = self.unit.compile(node1)
        self.assertEqual(res1, 'throw new CustomError(foo(42), bar());')

        node2 = ast.Raise(exc=ast.Name(id='my_error', ctx=ast.Load()))
        res2 = self.unit.compile(node2)
        self.assertEqual(res2, 'throw my_error;')

        node3 = ast.Raise(exc=None)
        res3 = self.unit.compile(node3)
        self.assertEqual(res3, 'throw undefined;')

        node4 = ast.Raise(
            exc=ast.Call(
                func=ast.Name(id='ValidationError', ctx=ast.Load()),
                args=[ast.Constant(value='Invalid input')],
                keywords=[]
            )
        )
        res4 = self.unit.compile(node4)
        self.assertEqual(res4, 'throw new ValidationError("Invalid input");')
