import ast
import unittest

from museflow.pyjs_compiler.pyjs_compiler_units.fstring_unit import FStringUnit


class TestFStringUnit(unittest.TestCase):
    def test_compile_constant_only(self):
        node = ast.JoinedStr(values=[ast.Constant(value="hello")])
        res =  FStringUnit().compile(node)
        self.assertEqual(res, "`hello`")

    def test_compile_with_formatted_value(self):
        node = ast.JoinedStr(values=[
            ast.Constant(value="hello "),
            ast.FormattedValue(value=ast.Name(id="name", ctx=ast.Load()), conversion=-1)
        ])
        res =  FStringUnit().compile(node)
        self.assertEqual(res, "`hello ${name}`")

    def test_compile_mixed(self):
        node = ast.JoinedStr(values=[
            ast.FormattedValue(value=ast.Name(id="greeting", ctx=ast.Load()), conversion=-1),
            ast.Constant(value=", "),
            ast.FormattedValue(value=ast.Name(id="name", ctx=ast.Load()), conversion=-1),
            ast.Constant(value="!")
        ])
        res =  FStringUnit().compile(node)
        self.assertEqual(res, "`${greeting}, ${name}!`")
