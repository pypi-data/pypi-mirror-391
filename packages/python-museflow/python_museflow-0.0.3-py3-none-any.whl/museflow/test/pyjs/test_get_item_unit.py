import ast
import unittest

from museflow.pyjs_compiler.pyjs_compiler_unit_abs import PYJSCompilerUnitException
from museflow.pyjs_compiler.pyjs_compiler_units.get_item_unit import GetItemUnit


class TestGetItemUnit(unittest.TestCase):

    def setUp(self):
        self.unit = GetItemUnit()

        def stub_compile_value(node: ast.AST) -> str:
            if isinstance(node, ast.Name):
                return node.id
            elif isinstance(node, ast.Constant):
                if isinstance(node.value, str):
                    return f'"{node.value}"'
                return str(node.value)
            return 'compiled_expression_stub'

        if not hasattr(self.unit, '_compile_value'):
            self.unit._compile_value = stub_compile_value
        # -------------------------------------

    def test_numeric_index_access(self):
        node = ast.Subscript(
            value=ast.Name(id='arr', ctx=ast.Load()),
            slice=ast.Constant(value=0),
            ctx=ast.Load()
        )
        self.assertEqual('arr[0]', self.unit.compile(node))

    def test_string_key_access(self):
        node = ast.Subscript(
            value=ast.Name(id='obj', ctx=ast.Load()),
            slice=ast.Constant(value='name'),
            ctx=ast.Load()
        )

        self.assertEqual('obj["name"]', self.unit.compile(node))

    def test_variable_index_access(self):
        node = ast.Subscript(
            value=ast.Name(id='data', ctx=ast.Load()),
            slice=ast.Name(id='i', ctx=ast.Load()),
            ctx=ast.Load()
        )
        self.assertEqual('data[i]', self.unit.compile(node))

    def test_access_on_complex_expression(self):
        call_node = ast.Call(
            func=ast.Name(id='func_call', ctx=ast.Load()),
            args=[],
            keywords=[]
        )
        node = ast.Subscript(
            value=call_node,
            slice=ast.Constant(value=10),
            ctx=ast.Load()
        )

        self.assertEqual('func_call()[10]', self.unit.compile(node))

    def test_complex_index_expression(self):
        binop_node = ast.BinOp(
            left=ast.Name(id='a', ctx=ast.Load()),
            op=ast.Add(),
            right=ast.Constant(value=1)
        )
        node = ast.Subscript(
            value=ast.Name(id='arr', ctx=ast.Load()),
            slice=binop_node,
            ctx=ast.Load()
        )

        self.assertEqual('arr[a + 1]', self.unit.compile(node))

    def test_invalid_node_type(self):
        with self.assertRaisesRegex(PYJSCompilerUnitException, r'Invalid node type'):
            self.unit.compile(ast.Assign(targets=[], value=ast.Constant(value=1)))

    def test_set_item_context(self):
        node = ast.Subscript(
            value=ast.Name(id='arr', ctx=ast.Load()),
            slice=ast.Name(id='i', ctx=ast.Load()),
            ctx=ast.Store()
        )
        self.assertEqual('arr[i]', self.unit.compile(node))

    def test_delete_item_context(self):
        node = ast.Subscript(
            value=ast.Name(id='obj', ctx=ast.Load()),
            slice=ast.Constant(value='key'),
            ctx=ast.Del()
        )
        self.assertEqual('obj["key"]', self.unit.compile(node))
