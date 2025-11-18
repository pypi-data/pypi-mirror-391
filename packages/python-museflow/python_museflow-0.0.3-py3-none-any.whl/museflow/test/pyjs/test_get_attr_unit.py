import ast
import unittest

from museflow.pyjs_compiler.pyjs_compiler_unit_abs import PYJSCompilerUnitException
from museflow.pyjs_compiler.pyjs_compiler_units.get_attr_unit import GetAttrUnit


class TestGetAttrUnit(unittest.TestCase):

    def setUp(self):
        self.unit = GetAttrUnit()

        def stub_compile_value(node: ast.AST) -> str:
            if isinstance(node, ast.Name):
                return node.id
            elif isinstance(node, ast.Constant):
                return str(node.value)
            return 'compiled_expression_stub'

        if not hasattr(self.unit, '_compile_value'):
            self.unit._compile_value = stub_compile_value

    def test_simple_attribute_access(self):
        node = ast.Attribute(
            value=ast.Name(id='user', ctx=ast.Load()),
            attr='name',
            ctx=ast.Load()
        )
        self.assertEqual('user.name', self.unit.compile(node))

    def test_nested_attribute_access(self):
        inner_node = ast.Attribute(
            value=ast.Name(id='user', ctx=ast.Load()),
            attr='profile',
            ctx=ast.Load()
        )
        node = ast.Attribute(
            value=inner_node,
            attr='address',
            ctx=ast.Load()
        )

        self.assertEqual('user.profile.address', self.unit.compile(node))

    def test_attribute_on_call_result(self):
        call_node = ast.Call(
            func=ast.Name(id='get_data', ctx=ast.Load()),
            args=[],
            keywords=[]
        )
        node = ast.Attribute(
            value=call_node,
            attr='id',
            ctx=ast.Load()
        )

        self.assertEqual('get_data().id', self.unit.compile(node))

    def test_attribute_on_constant_value(self):
        node = ast.Attribute(
            value=ast.Constant(value=123),
            attr='toFixed',
            ctx=ast.Load()
        )

        self.assertEqual('123.toFixed', self.unit.compile(node))

    def test_invalid_node_type(self):
        with self.assertRaisesRegex(PYJSCompilerUnitException, r'Invalid node type'):
            self.unit.compile(ast.Name(id='a', ctx=ast.Load()))

    def test_set_attribute_context(self):
        node = ast.Attribute(
            value=ast.Name(id='user', ctx=ast.Load()),
            attr='name',
            ctx=ast.Store()  # Context is Store
        )

        self.assertEqual('user.name', self.unit.compile(node))

    def test_delete_attribute_context(self):
        node = ast.Attribute(
            value=ast.Name(id='obj', ctx=ast.Load()),
            attr='attr_key',
            ctx=ast.Del()  # Context is Del
        )

        self.assertEqual('obj.attr_key', self.unit.compile(node))
