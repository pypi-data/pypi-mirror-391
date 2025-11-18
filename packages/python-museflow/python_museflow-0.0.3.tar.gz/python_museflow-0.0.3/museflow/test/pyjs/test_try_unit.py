import ast
import unittest

from museflow.pyjs_compiler.pyjs_compiler_unit_abs import PYJSCompilerUnitException
from museflow.pyjs_compiler.pyjs_compiler_units.try_unit import TryUnit


class TestTryUnit(unittest.TestCase):
    def setUp(self):
        self.unit = TryUnit()

    def test_simple_try_except(self):
        node = ast.Try(
            body=[ast.Expr(ast.Call(func=ast.Name(id='foo', ctx=ast.Load()), args=[], keywords=[]))],
            handlers=[ast.ExceptHandler(
                type=ast.Name(id='Exception', ctx=ast.Load()),
                name=None,
                body=[ast.Expr(ast.Call(func=ast.Name(id='bar', ctx=ast.Load()), args=[], keywords=[]))]
            )],
            orelse=[],
            finalbody=[]
        )
        res =self.unit.compile(node)
        expected = (
            'try {\n'
            '  foo();\n'
            '}\n'
            'catch (e) { if (!(e instanceof Exception)) throw e;\n'
            '  bar();\n'
            '}'
        )
        self.assertEqual(expected, res)

    def test_try_finally(self):
        node = ast.Try(
            body=[ast.Expr(ast.Call(func=ast.Name(id='foo', ctx=ast.Load()), args=[], keywords=[]))],
            handlers=[],
            orelse=[],
            finalbody=[ast.Expr(ast.Call(func=ast.Name(id='bar', ctx=ast.Load()), args=[], keywords=[]))]
        )
        res =self.unit.compile(node)
        expected = (
            'try {\n'
            '  foo();\n'
            '}\n'
            'finally {\n'
            '  bar();\n'
            '}'
        )
        self.assertEqual(expected, res)

    def test_try_except_finally(self):
        node = ast.Try(
            body=[ast.Expr(ast.Call(func=ast.Name(id='foo', ctx=ast.Load()), args=[], keywords=[]))],
            handlers=[ast.ExceptHandler(
                type=ast.Name(id='Exception', ctx=ast.Load()),
                name=None,
                body=[ast.Expr(ast.Call(func=ast.Name(id='bar', ctx=ast.Load()), args=[], keywords=[]))]
            )],
            orelse=[],
            finalbody=[ast.Expr(ast.Call(func=ast.Name(id='baz', ctx=ast.Load()), args=[], keywords=[]))]
        )
        res =self.unit.compile(node)
        expected = (
            'try {\n'
            '  foo();\n'
            '}\n'
            'catch (e) { if (!(e instanceof Exception)) throw e;\n'
            '  bar();\n'
            '}\n'
            'finally {\n'
            '  baz();\n'
            '}'
        )
        self.assertEqual(expected, res)

    def test_nested_try(self):
        """
        Python:
            try:
                try:
                    foo()
                except Exception:
                    bar()
            except AnotherException:
                baz()
        JS (expected):
            try {
              try {
                foo();
              }
              catch (e) { if (!(e instanceof Exception)) throw e;
                bar();
              }
            }
            catch (e) { if (!(e instanceof AnotherException)) throw e;
              baz();
            }
        """
        node = ast.Try(
            body=[ast.Try(
                body=[ast.Expr(ast.Call(func=ast.Name(id='foo', ctx=ast.Load()), args=[], keywords=[]))],
                handlers=[ast.ExceptHandler(
                    type=ast.Name(id='Exception', ctx=ast.Load()),
                    name=None,
                    body=[ast.Expr(ast.Call(func=ast.Name(id='bar', ctx=ast.Load()), args=[], keywords=[]))]
                )],
                orelse=[],
                finalbody=[]
            )],
            handlers=[ast.ExceptHandler(
                type=ast.Name(id='AnotherException', ctx=ast.Load()),
                name=None,
                body=[ast.Expr(ast.Call(func=ast.Name(id='baz', ctx=ast.Load()), args=[], keywords=[]))]
            )],
            orelse=[],
            finalbody=[]
        )

        res =self.unit.compile(node)
        expected = (
            'try {\n'
            '  try {\n'
            '    foo();\n'
            '  }\n'
            '  catch (e) { if (!(e instanceof Exception)) throw e;\n'
            '    bar();\n'
            '  }\n'
            '}\n'
            'catch (e) { if (!(e instanceof AnotherException)) throw e;\n'
            '  baz();\n'
            '}'
        )
        self.assertEqual(expected, res)

    def test_invalid_node(self):
        node = ast.Constant(value=123)
        with self.assertRaises(PYJSCompilerUnitException):
            self.unit.compile(node)
