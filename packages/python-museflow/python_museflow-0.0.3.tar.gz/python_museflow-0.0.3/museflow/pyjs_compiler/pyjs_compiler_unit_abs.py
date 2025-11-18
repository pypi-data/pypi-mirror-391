import ast
from abc import ABC, abstractmethod

from museflow.pyjs_compiler.pyjs_dispatcher import PYJSDispatcher


class PYJSCompilerUnitException(Exception):
    def __init__(self, message: str):
        super().__init__(f'{self.__class__.__name__}: {message}')


class PYJSCompilerUnit(ABC):
    """ Python to JavaScript Compiler Unit - A class for converting a specific type of Python AST node to JavaScript """

    def __init__(self):
        self.__dispatch_map = None
        self._scope_stack = [set()]
        self.do_declare = True  # Controls 'let' generation for new variables - If False, 'let' is suppressed

    @property
    @abstractmethod
    def variant(self) -> str:
        """ Returns the node variant (type) this unit handles as a string """
        raise NotImplementedError

    @abstractmethod
    def compile(self, node: ast.AST) -> str:
        raise NotImplementedError

    @property
    def dispatch_map(self) -> dict:
        if self.__dispatch_map is None:
            self.__dispatch_map = PYJSDispatcher.get_dispatch_map()
        return self.__dispatch_map

    # noinspection PyMethodMayBeStatic
    def _compile_value(self, node: ast.AST) -> str:
        for unit in self.dispatch_map.values():
            variant = unit.variant
            if isinstance(variant, tuple):
                if isinstance(node, variant):
                    unit.do_declare = self.do_declare
                    unit._scope_stack = self._scope_stack
                    unit.enter_scope = self.enter_scope
                    unit.exit_scope = self.exit_scope
                    return unit.compile(node)
            else:
                if isinstance(node, variant):
                    unit.do_declare = self.do_declare
                    unit._scope_stack = self._scope_stack
                    unit.enter_scope = self.enter_scope
                    unit.exit_scope = self.exit_scope
                    return unit.compile(node)

        raise PYJSCompilerUnitException(f'Unsupported AST node type: {type(node)}, node dump: {ast.dump(node, indent=2)}')

    def _compile_target(self, target: ast.AST) -> str:
        """ Compiles an AST node representing the left-hand side (LHS) of an assignment """
        if isinstance(target, ast.Name):
            return target.id
        elif isinstance(target, ast.Attribute):
            value_js = self._compile_value(target.value)  # noqa
            return f'{value_js}.{target.attr}'
        elif isinstance(target, ast.Subscript):
            value_js = self._compile_value(target.value)  # noqa
            slice_js = self._compile_value(target.slice)  # noqa
            return f'{value_js}[{slice_js}]'
        else:
            raise PYJSCompilerUnitException(f'Unsupported assignment target: {type(target)}')

    def enter_scope(self):
        self._scope_stack.append(set())

    def exit_scope(self):
        if len(self._scope_stack) > 1:
            self._scope_stack.pop()

    @property
    def current_scope(self):
        """ Returns the set representing the variables in the innermost scope """
        return self._scope_stack[-1]