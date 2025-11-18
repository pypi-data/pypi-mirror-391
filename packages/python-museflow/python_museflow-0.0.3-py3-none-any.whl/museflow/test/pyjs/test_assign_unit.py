import ast
import unittest

from museflow.pyjs_compiler.pyjs_compiler_units.assign_unit import AssignUnit


class TestAssignUnit(unittest.TestCase):
    def setUp(self):
        self.unit = AssignUnit()

    def test_new_variable_declaration(self):
        node = ast.Assign(
            targets=[ast.Name(id='a', ctx=ast.Store())],
            value=ast.Constant(value=10)
        )
        result = self.unit.compile(node)

        self.assertEqual('let a = 10;', result)
        self.assertIn('a', self.unit.current_scope)

    def test_reassignment_to_scoped_variable(self):
        self.unit.current_scope.add('b')

        node = ast.Assign(
            targets=[ast.Name(id='b', ctx=ast.Store())],
            value=ast.Constant(value=20)
        )
        result = self.unit.compile(node)

        self.assertEqual('b = 20;', result)
        self.assertIn('b', self.unit.current_scope)

    def test_reassignment_to_global_variable(self):
        self.unit.mark_global({'c'})

        node = ast.Assign(
            targets=[ast.Name(id='c', ctx=ast.Store())],
            value=ast.Constant(value=30)
        )
        result = self.unit.compile(node)

        self.assertEqual('c = 30;', result)

    def test_non_top_level_assignment(self):
        try:
            self.unit.do_declare = False
            node = ast.Assign(
                targets=[ast.Name(id='d', ctx=ast.Store())],
                value=ast.Constant(value=40)
            )
            result = self.unit.compile(node)

            self.assertEqual('d = 40;', result)
            self.assertNotIn('d', self.unit.current_scope)
        finally:
            self.unit.do_declare = True

    def test_scope_stack_isolation(self):
        node_1 = ast.Assign(targets=[ast.Name(id='x', ctx=ast.Store())], value=ast.Constant(value=1))
        self.unit.compile(node_1)

        # Expected is now the first argument
        self.assertEqual([{'x'}], self.unit._scope_stack)

        self.unit.enter_scope()
        self.assertEqual([{'x'}, set()], self.unit._scope_stack)

        node_2 = ast.Assign(targets=[ast.Name(id='y', ctx=ast.Store())], value=ast.Constant(value=2))
        result_2 = self.unit.compile(node_2)

        # Expected is now the first argument
        self.assertEqual('let y = 2;', result_2)
        self.assertEqual([{'x'}, {'y'}], self.unit._scope_stack)

        node_3 = ast.Assign(targets=[ast.Name(id='x', ctx=ast.Store())], value=ast.Constant(value=3))
        result_3 = self.unit.compile(node_3)

        # Expected is now the first argument
        self.assertEqual('x = 3;', result_3)

        self.unit.exit_scope()

    def test_attribute_assignment_in_nested_scope(self):
        node_setup = ast.Assign(
            targets=[ast.Name(id='obj', ctx=ast.Store())],
            value=ast.Constant(value='{}')  # Assume _compile_value returns '{}'
        )
        self.unit.compile(node_setup)
        self.assertIn('obj', self.unit.current_scope)

        self.unit.enter_scope()
        self.assertEqual(len(self.unit._scope_stack), 2)

        assign_node = ast.Assign(
            targets=[ast.Attribute(
                value=ast.Name(id='obj', ctx=ast.Load()),
                attr='prop',
                ctx=ast.Store()
            )],
            value=ast.Constant(value=50)
        )
        result = self.unit.compile(assign_node)

        self.assertEqual('obj.prop = 50;', result)

        self.assertEqual(len(self.unit.current_scope), 0)

        self.unit.exit_scope()
