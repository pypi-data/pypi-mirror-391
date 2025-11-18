import ast
import unittest

from museflow.pyjs_compiler.pyjs_compiler_unit_abs import PYJSCompilerUnitException
from museflow.pyjs_compiler.pyjs_compiler_units.loop_unit import LoopUnit


class TestLoopUnit(unittest.TestCase):
    def setUp(self):
        self.unit = LoopUnit()

    def test_simple_for_loop(self):
        node = ast.For(
            target=ast.Name(id='i', ctx=ast.Store()),
            iter=ast.Call(func=ast.Name(id='range', ctx=ast.Load()), args=[ast.Constant(3)], keywords=[]),
            body=[ast.Expr(ast.Call(func=ast.Name(id='foo', ctx=ast.Load()), args=[ast.Name(id='i', ctx=ast.Load())], keywords=[]))],
            orelse=[]
        )

        res = self.unit.compile(node)

        expected = (
            'for (let i = 0; i < 3; i++) {\n'
            '    foo(i);\n'
            '}'
        )
        self.assertEqual(expected, res)

    def test_while_loop(self):
        node = ast.While(
            test=ast.Compare(
                left=ast.Name(id='x', ctx=ast.Load()),
                ops=[ast.Lt()],
                comparators=[ast.Constant(5)]
            ),
            body=[ast.Assign(
                targets=[ast.Name(id='x', ctx=ast.Store())],
                value=ast.BinOp(
                    left=ast.Name(id='x', ctx=ast.Load()),
                    op=ast.Add(),
                    right=ast.Constant(1)
                )
            )],
            orelse=[]
        )
        res = self.unit.compile(node)

        expected = (
            'while (x < 5) {\n'
            '    x = x + 1;\n'
            '}'
        )
        self.assertEqual(expected, res)

    def test_nested_loops(self):
        node = ast.For(
            target=ast.Name(id='i', ctx=ast.Store()),
            iter=ast.Name(id='arr', ctx=ast.Load()),
            body=[
                ast.For(
                    target=ast.Name(id='j', ctx=ast.Store()),
                    iter=ast.Name(id='arr2', ctx=ast.Load()),
                    body=[ast.Expr(ast.Call(func=ast.Name(id='process', ctx=ast.Load()),
                                            args=[ast.Name(id='i', ctx=ast.Load()),
                                                  ast.Name(id='j', ctx=ast.Load())],
                                            keywords=[]))],
                    orelse=[]
                )
            ],
            orelse=[]
        )
        res = self.unit.compile(node)
        expected = (
            'for (let i of arr) {\n'
            '    for (let j of arr2) {\n'
            '        process(i, j);\n'
            '    }\n'
            '}'
        )
        self.assertEqual(expected, res)

    def test_invalid_node(self):
        node = ast.Constant(value=123)
        with self.assertRaises(PYJSCompilerUnitException):
            self.unit.compile(node)

    def test_complex_nested_loops(self):
        node = ast.For(
            target=ast.Name(id='i', ctx=ast.Load()),
            iter=ast.Call(func=ast.Name(id='range', ctx=ast.Load()), args=[ast.Constant(value=3)], keywords=[]),
            body=[
                ast.For(
                    target=ast.Name(id='j', ctx=ast.Load()),
                    iter=ast.Call(func=ast.Name(id='range', ctx=ast.Load()), args=[ast.Constant(value=2)], keywords=[]),
                    body=[
                        ast.Assign(
                            targets=[ast.Name(id='x', ctx=ast.Store())],
                            value=ast.BinOp(
                                left=ast.Name(id='i', ctx=ast.Load()),
                                op=ast.Add(),
                                right=ast.Name(id='j', ctx=ast.Load())
                            )
                        ),
                        ast.Expr(
                            value=ast.Call(func=ast.Name(id='foo', ctx=ast.Load()), args=[ast.Name(id='x', ctx=ast.Load())], keywords=[])
                        )
                    ],
                    orelse=[]
                ),
                ast.While(
                    test=ast.Compare(
                        left=ast.Name(id='x', ctx=ast.Load()),
                        ops=[ast.Lt()],
                        comparators=[ast.Constant(value=5)]
                    ),
                    body=[
                        ast.Assign(
                            targets=[ast.Name(id='x', ctx=ast.Store())],
                            value=ast.BinOp(
                                left=ast.Name(id='x', ctx=ast.Load()),
                                op=ast.Add(),
                                right=ast.Constant(value=1)
                            )
                        )
                    ],
                    orelse=[]
                )
            ],
            orelse=[]
        )

        res = self.unit.compile(node)

        expected = (
            'for (let i = 0; i < 3; i++) {\n'
            '    for (let j = 0; j < 2; j++) {\n'
            "        x = i + j;\n"
            '        foo(x);\n'
            '    }\n'
            '    while (x < 5) {\n'
            "        x = x + 1;\n"
            '    }\n'
            '}'
        )

        self.assertEqual(expected, res)
