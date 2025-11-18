import ast
import unittest

from museflow.pyjs_compiler.pyjs_compiler_unit_abs import PYJSCompilerUnitException
from museflow.pyjs_compiler.pyjs_compiler_units.dict_unit import DictUnit


class TestDictUnit(unittest.TestCase):

    def setUp(self):
        self.unit = DictUnit()

        def mock_compile_value(node: ast.AST) -> str:
            if isinstance(node, ast.Constant):
                if isinstance(node.value, str):
                    return f'"{node.value}"'
                if isinstance(node.value, (int, float)):
                    return str(node.value)
                if node.value is None:
                    return 'null'
            elif isinstance(node, ast.Name):
                return node.id
            return f'compiled_stub_{type(node).__name__}'

        self.unit._compile_value = mock_compile_value

    def test_empty_dictionary(self):
        node = ast.Dict(keys=[], values=[])
        result = self.unit.compile(node)
        self.assertEqual('{}', result)

    def test_simple_string_keys_and_values(self):
        node = ast.Dict(
            keys=[ast.Constant(value='name'), ast.Constant(value='age')],
            values=[ast.Constant(value='Alice'), ast.Constant(value=30)]
        )
        result = self.unit.compile(node)
        self.assertEqual('{"name": "Alice", "age": 30}', result)

    def test_variable_keys_and_values(self):
        node = ast.Dict(
            keys=[ast.Name(id='key_var', ctx=ast.Load()), ast.Constant(value='value_var')],
            values=[ast.Constant(value=100), ast.Name(id='data', ctx=ast.Load())]
        )
        result = self.unit.compile(node)
        self.assertEqual('{key_var: 100, "value_var": data}', result)

    def test_mixed_types_and_length(self):
        node = ast.Dict(
            keys=[
                ast.Constant(value='status'),
                ast.Constant(value=1)
            ],
            values=[
                ast.Constant(value=None),
                ast.Constant(value=3.14)
            ]
        )
        result = self.unit.compile(node)
        self.assertEqual('{"status": null, 1: 3.14}', result)

    def test_invalid_node_type(self):
        with self.assertRaisesRegex(PYJSCompilerUnitException, r'Invalid node type'):
            self.unit.compile(ast.List(elts=[], ctx=ast.Load()))

    def test_computed_key_and_call_value(self):
        call_node = ast.Call(
            func=ast.Name(id='func', ctx=ast.Load()),
            args=[ast.BinOp(left=ast.Name(id='x', ctx=ast.Load()), op=ast.Add(), right=ast.Constant(value=1))],
            keywords=[]
        )

        binop_node = ast.BinOp(
            left=ast.Constant(value=5),
            op=ast.Mult(),
            right=ast.Name(id='y', ctx=ast.Load())
        )

        node = ast.Dict(
            keys=[
                ast.Constant(value='status'),
                ast.Name(id='key_var', ctx=ast.Load())
            ],
            values=[
                call_node,
                binop_node
            ]
        )

        expected_js = '{"status": compiled_stub_Call, key_var: compiled_stub_BinOp}'

        result = self.unit.compile(node)
        self.assertEqual(expected_js, result)
