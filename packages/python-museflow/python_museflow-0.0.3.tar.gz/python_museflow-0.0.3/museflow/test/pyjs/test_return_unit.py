import ast
import unittest

from museflow.pyjs_compiler.pyjs_compiler_unit_abs import PYJSCompilerUnitException
from museflow.pyjs_compiler.pyjs_compiler_units.return_unit import ReturnUnit


class TestReturnUnit(unittest.TestCase):
    def setUp(self):
        self.unit = ReturnUnit()

    def test_return_constant(self):
        node = ast.Return(value=ast.Constant(value=42))
        res =self.unit.compile(node)
        self.assertEqual(res, 'return 42;')

    def test_return_boolean(self):
        node = ast.Return(value=ast.Constant(value=True))
        res =self.unit.compile(node)
        self.assertEqual(res, 'return true;')

    def test_return_name(self):
        node = ast.Return(value=ast.Name(id='x', ctx=ast.Load()))
        res =self.unit.compile(node)
        self.assertEqual(res, 'return x;')

    def test_return_none(self):
        node = ast.Return(value=None)
        res =self.unit.compile(node)
        self.assertEqual(res, 'return;')

    def test_invalid_return(self):
        node = ast.Return(value=ast.Lambda(args=ast.arguments(args=[], posonlyargs=[], kwonlyargs=[], kw_defaults=[], defaults=[]),
                                           body=ast.Constant(value=1)))
        with self.assertRaises(PYJSCompilerUnitException):
            self.unit.compile(node)

    def test_return_expression(self):
        node = ast.Return(
            value=ast.BinOp(
                left=ast.Name(id='x', ctx=ast.Load()),
                op=ast.Add(),
                right=ast.Constant(value=1)
            )
        )
        res =self.unit.compile(node)
        self.assertEqual(res, 'return (x + 1);')

    def test_return_complex_expression(self):
        node = ast.Return(
            value=ast.BinOp(
                left=ast.UnaryOp(
                    op=ast.USub(),
                    operand=ast.BinOp(
                        left=ast.Name(id='x', ctx=ast.Load()),
                        op=ast.Add(),
                        right=ast.Call(
                            func=ast.Name(id='foo', ctx=ast.Load()),
                            args=[ast.Constant(value=2)],
                            keywords=[]
                        )
                    )
                ),
                op=ast.Mult(),
                right=ast.Constant(value=3)
            )
        )

        res =self.unit.compile(node)
        expected = 'return (-(x + foo(2)) * 3);'
        self.assertEqual(expected, res)
