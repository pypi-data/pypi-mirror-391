import ast
import unittest

from museflow.pyjs_compiler.pyjs_compiler_unit_abs import PYJSCompilerUnitException
from museflow.pyjs_compiler.pyjs_compiler_units.if_unit import IfUnit


class TestIfUnit(unittest.TestCase):
    def setUp(self):
        self.unit = IfUnit()

    def test_simple_if(self):
        node = ast.If(
            test=ast.Constant(value=True),
            body=[ast.Assign(targets=[ast.Name(id='x', ctx=ast.Store())], value=ast.Constant(value=1))],
            orelse=[]
        )
        res =  self.unit.compile(node)
        expected = (
            'if (true) {\n'
            '    x = 1;\n'
            '}'
        )
        self.assertEqual(expected, res)

    def test_if_else(self):
        node = ast.If(
            test=ast.Constant(value=True),
            body=[ast.Assign(targets=[ast.Name(id='x', ctx=ast.Store())], value=ast.Constant(value=1))],
            orelse=[ast.Assign(targets=[ast.Name(id='x', ctx=ast.Store())], value=ast.Constant(value=2))]
        )
        res =  self.unit.compile(node)

        expected = (
            'if (true) {\n'
            '    x = 1;\n'
            '} else {\n'
            '    x = 2;\n'
            '}'
        )
        self.assertEqual(expected, res)

    def test_if_elif_else(self):
        node = ast.If(
            test=ast.Name(id='a', ctx=ast.Load()),
            body=[ast.Assign(targets=[ast.Name(id='x', ctx=ast.Store())], value=ast.Constant(value=1))],
            orelse=[
                ast.If(
                    test=ast.Name(id='b', ctx=ast.Load()),
                    body=[ast.Assign(targets=[ast.Name(id='x', ctx=ast.Store())], value=ast.Constant(value=2))],
                    orelse=[ast.Assign(targets=[ast.Name(id='x', ctx=ast.Store())], value=ast.Constant(value=3))]
                )
            ]
        )

        res =  self.unit.compile(node)

        expected = (
            'if (a) {\n'
            '    x = 1;\n'
            '} else if (b) {\n'
            '    x = 2;\n'
            '} else {\n'
            '    x = 3;\n'
            '}'
        )
        self.assertEqual(expected, res)

    def test_nested_if(self):
        node = ast.If(
            test=ast.Name(id='a', ctx=ast.Load()),
            body=[
                ast.If(
                    test=ast.Name(id='b', ctx=ast.Load()),
                    body=[ast.Assign(targets=[ast.Name(id='x', ctx=ast.Store())], value=ast.Constant(value=1))],
                    orelse=[]
                )
            ],
            orelse=[]
        )
        res =  self.unit.compile(node)
        expected = (
            'if (a) {\n'
            '    if (b) {\n'
            '        x = 1;\n'
            '    }\n'
            '}'
        )
        self.assertEqual(expected, res)

    def test_if_with_return(self):
        node = ast.If(
            test=ast.Constant(value=True),
            body=[ast.Return(value=ast.Constant(value=42))],
            orelse=[]
        )
        res =  self.unit.compile(node)
        expected = (
            'if (true) {\n'
            '    return 42;\n'
            '}'
        )
        self.assertEqual(expected, res)

    def test_invalid_body_node_raises_exception(self):
        node = ast.If(
            test=ast.Constant(value=True),
            body=[ast.Global(names=['foo'])],
            orelse=[]
        )
        with self.assertRaises(PYJSCompilerUnitException):
            self.unit.compile(node)

    def test_if_with_local_declaration(self):
        node = ast.If(
            test=ast.Name(id='a', ctx=ast.Load()),
            body=[
                ast.Assign(targets=[ast.Name(id='x', ctx=ast.Store())], value=ast.Constant(value=1))
            ],
            orelse=[]
        )

        res =  self.unit.compile(node)

        expected = (
            'if (a) {\n'
            '    x = 1;\n'
            '}'
        )

        self.assertEqual(expected, res)

    def test_deeply_nested_control_flow(self):
        node = ast.If(
            test=ast.Name(id='a', ctx=ast.Load()),
            body=[
                ast.Assign(targets=[ast.Name(id='x', ctx=ast.Store())], value=ast.Constant(value=1)),

                ast.For(
                    target=ast.Name(id='i', ctx=ast.Store()),
                    iter=ast.Call(func=ast.Name(id='range', ctx=ast.Load()), args=[ast.Constant(value=5)], keywords=[]),
                    body=[
                        ast.Expr(value=ast.Call(func=ast.Name(id='log', ctx=ast.Load()), args=[ast.Name(id='i', ctx=ast.Load())], keywords=[]))
                    ],
                    orelse=[]
                ),
                ast.Expr(value=ast.Call(func=ast.Name(id='done', ctx=ast.Load()), args=[], keywords=[]))
            ],
            orelse=[
                ast.If(
                    test=ast.Compare(
                        left=ast.Name(id='y', ctx=ast.Load()),
                        ops=[ast.Gt()],
                        comparators=[ast.Constant(value=10)]
                    ),
                    body=[
                        ast.Assign(targets=[ast.Name(id='z', ctx=ast.Store())], value=ast.Constant(value=2)),

                        ast.While(
                            test=ast.Name(id='flag', ctx=ast.Load()),
                            body=[
                                ast.Expr(value=ast.Call(func=ast.Name(id='calculate', ctx=ast.Load()), args=[], keywords=[]))
                            ],
                            orelse=[]
                        )
                    ],
                    orelse=[
                        ast.Assign(targets=[ast.Name(id='x', ctx=ast.Store())], value=ast.Constant(value=3)),
                        ast.Return(value=ast.Constant(value=False))
                    ]
                )
            ]
        )

        res =  self.unit.compile(node)

        expected = (
            'if (a) {\n'
            '    x = 1;\n'
            '    for (let i = 0; i < 5; i++) {\n'
            '        log(i);\n'
            '    }\n'
            '    done();\n'
            '} else if (y > 10) {\n'
            '    z = 2;\n'
            '    while (flag) {\n'
            '        calculate();\n'
            '    }\n'
            '} else {\n'
            '    x = 3;\n'
            '    return false;\n'
            '}'
        )

        self.assertEqual(expected, res)
