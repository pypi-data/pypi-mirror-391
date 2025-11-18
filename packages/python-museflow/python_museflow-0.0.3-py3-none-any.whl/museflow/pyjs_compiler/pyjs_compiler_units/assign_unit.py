import ast
from typing import Any

from museflow.pyjs_compiler.pyjs_compiler_unit_abs import PYJSCompilerUnit, PYJSCompilerUnitException


class AssignUnit(PYJSCompilerUnit):
    """
    Compiles an ast.Assign node (for single targets) to JavaScript

    Algorithm:
    1. Compile the assignment target and value
    2. If the target is not an ast.Name (E.G. Attribute or Subscript), return a simple assignment
    3. If the target is an ast.Name:
       a. Check if the variable is defined in global scope or any nested scope.
       b. If defined (reassignment), return simple assignment ('name = value;')
       c. If not defined:
          I. If 'do_declare' is True, track the variable in the current scope and return 'let name = value;'
          II. If 'do_declare' is False (suppressed declaration), return simple assignment ('name = value;') without tracking
    """

    def __init__(self):
        super().__init__()
        self._global_vars = set()
        self.do_declare = True  # Controls 'let' generation for new variables - If False, 'let' is suppressed

    @property
    def variant(self) -> Any:
        return ast.Assign

    def mark_global(self, names):
        self._global_vars.update(names)

    @property
    def current_scope(self):
        return self._scope_stack[-1]

    def compile(self, node: ast.AST) -> str:
        if not isinstance(node, ast.Assign):
            raise PYJSCompilerUnitException(f'Invalid node type: {type(node)}, expected Assign')

        target_node = node.targets[0]
        target = self._compile_target(target_node)
        value = self._compile_value(node.value)

        if isinstance(target_node, ast.Name):
            is_defined = target in self._global_vars or self._find_in_scopes(target)

            if is_defined:
                return f'{target} = {value};'

            elif self.do_declare:
                self.current_scope.add(target)
                return f'let {target} = {value};'
            else:
                return f'{target} = {value};'
        else:
            return f'{target} = {value};'



    def _find_in_scopes(self, name: str) -> bool:
        for scope in reversed(self._scope_stack):
            if name in scope:
                return True
        return False
