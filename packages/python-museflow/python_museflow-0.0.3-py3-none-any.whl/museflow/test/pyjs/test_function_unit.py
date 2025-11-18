import ast
import unittest

from museflow.pyjs_compiler.pyjs_compiler_unit_abs import PYJSCompilerUnitException
from museflow.pyjs_compiler.pyjs_compiler_units.function_unit import FunctionUnit


class TestFunctionUnit(unittest.TestCase):

    def setUp(self):
        self.unit = FunctionUnit()

    def test_basic_function_no_args(self):
        """Tests a function with no arguments and a simple body."""
        node = ast.FunctionDef(
            name='say_hello',
            args=ast.arguments(posonlyargs=[], args=[], vararg=None, defaults=[], kwonlyargs=[], kw_defaults=[], kwarg=None),
            body=[ast.Expr(value=ast.Constant(value=None))],
            decorator_list=[], returns=None, type_comment=None
        )

        # 🎯 FIX: Update the expected output to reflect correct compilation ('null;')
        expected = (
            'function say_hello() {\n'
            'null;\n'
            '}'
        )
        self.assertEqual(expected, self.unit.compile(node))

    def test_function_with_positional_args(self):
        node = ast.FunctionDef(
            name='add',
            args=ast.arguments(
                posonlyargs=[],
                args=[ast.arg(arg='a'), ast.arg(arg='b')],
                vararg=None, defaults=[], kwonlyargs=[], kw_defaults=[], kwarg=None
            ),
            body=[],
            decorator_list=[], returns=None, type_comment=None
        )
        expected = 'function add(a, b) {\n\n}'
        self.assertEqual(expected, self.unit.compile(node))

    def test_function_with_return(self):
        node = ast.FunctionDef(
            name='get_value',
            args=ast.arguments(posonlyargs=[], args=[], vararg=None, defaults=[], kwonlyargs=[], kw_defaults=[], kwarg=None),
            body=[ast.Return(value=ast.Constant(value=10))],
            decorator_list=[], returns=None, type_comment=None
        )

        expected = (
            'function get_value() {\n'
            'return 10;\n'
            '}'
        )

        self.unit.return_handled = False
        self.assertEqual(expected, self.unit.compile(node))

    def test_local_assignment_and_scope(self):
        node = ast.FunctionDef(
            name='calculate',
            args=ast.arguments(posonlyargs=[], args=[ast.arg(arg='x')], vararg=None, defaults=[], kwonlyargs=[], kw_defaults=[], kwarg=None),
            body=[
                ast.Assign(targets=[ast.Name(id='y', ctx=ast.Store())], value=ast.Constant(value=2)),  # New variable
                ast.Assign(targets=[ast.Name(id='x', ctx=ast.Store())], value=ast.Constant(value=100))  # Reassignment of argument
            ],
            decorator_list=[], returns=None, type_comment=None
        )
        expected = (
            'function calculate(x) {\n'
            'y = 2;\n'
            'x = 100;\n'
            '}'
        )

        self.assertEqual(expected, self.unit.compile(node))

    def test_empty_function_body(self):
        node = ast.FunctionDef(
            name='no_op',
            args=ast.arguments(posonlyargs=[], args=[], vararg=None, defaults=[], kwonlyargs=[], kw_defaults=[], kwarg=None),
            body=[],
            decorator_list=[], returns=None, type_comment=None
        )
        expected = 'function no_op() {\n\n}'
        self.assertEqual(expected, self.unit.compile(node))

    def test_function_with_positional_only_args(self):
        node = ast.FunctionDef(
            name='pos_only',
            args=ast.arguments(
                posonlyargs=[ast.arg(arg='a')],
                args=[ast.arg(arg='b')],
                vararg=None, defaults=[], kwonlyargs=[], kw_defaults=[], kwarg=None
            ),
            body=[],
            decorator_list=[], returns=None, type_comment=None
        )

        expected = 'function pos_only(a, b) {\n\n}'
        self.assertEqual(expected, self.unit.compile(node))

    def test_invalid_node_type(self):
        with self.assertRaisesRegex(PYJSCompilerUnitException, r'Invalid node type'):
            self.unit.compile(ast.Assign(targets=[], value=ast.Constant(value=1)))
