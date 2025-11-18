import ast
from typing import Any

from museflow.pyjs_compiler.pyjs_compiler_unit_abs import PYJSCompilerUnit, PYJSCompilerUnitException


class FunctionUnit(PYJSCompilerUnit):
    def __init__(self):
        super().__init__()
        self.do_declare = False  # Controls 'let' generation for new variables - If False, 'let' is suppressed

    @property
    def variant(self) -> Any:
        return ast.FunctionDef

    def compile(self, node: ast.AST) -> str:
        if not isinstance(node, ast.FunctionDef):
            raise PYJSCompilerUnitException(f'Invalid node type: {type(node)}, expected: FunctionDef')

        func_name = node.name
        args_js, arg_names = self._compile_args_and_get_names(node)
        original_do_declare = self.do_declare
        self.do_declare = False
        self.enter_scope()

        for arg in arg_names:
            self.current_scope.add(arg)

        body_js = self._compile_body(node.body)
        self.exit_scope()
        self.do_declare = original_do_declare

        return f'function {func_name}({args_js}) {{\n{body_js}\n}}'

    def _compile_args_and_get_names(self, node: ast.FunctionDef) -> tuple[str, list[str]]:

        all_args_nodes = node.args.posonlyargs + node.args.args

        arg_names = [arg.arg for arg in all_args_nodes]
        defaults = node.args.defaults
        num_defaults = len(defaults)

        args_js = []

        for i, arg_name in enumerate(arg_names):
            default_index = i - (len(arg_names) - num_defaults)

            if default_index >= 0:
                default_node = defaults[default_index]
                default_js = self._compile_value(default_node)
                args_js.append(f'{arg_name} = {default_js}')
            else:
                args_js.append(arg_name)

        return ', '.join(args_js), arg_names

    def _compile_args(self, node: ast.FunctionDef) -> str:
        # Retained for compatibility if tests rely on this helper name
        args_js, _ = self._compile_args_and_get_names(node)
        return args_js

    def _compile_body(self, body_nodes: list[ast.AST]) -> str:
        js_lines = []
        for node in body_nodes:
            js_line = self._compile_value(node)

            if not js_line.endswith(';'):
                js_line += ';'

            js_lines.append(js_line)

        return '\n'.join(js_lines)
