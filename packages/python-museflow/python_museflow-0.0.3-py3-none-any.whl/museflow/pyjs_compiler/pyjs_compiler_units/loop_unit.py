import ast
from typing import Any

from museflow.pyjs_compiler.pyjs_compiler_unit_abs import PYJSCompilerUnit, PYJSCompilerUnitException


class LoopUnit(PYJSCompilerUnit):
    @property
    def variant(self) -> Any:
        return ast.For, ast.While

    def compile(self, node: ast.AST, indent_level: int = 0) -> str:
        indent = '    ' * indent_level

        if isinstance(node, ast.For):
            # 1. Compile body ONLY if the node is a loop type
            body_js = self._compile_body(node.body, indent_level + 1)  # noqa

            is_range_call = isinstance(node.iter, ast.Call) and \
                            isinstance(node.iter.func, ast.Name) and \
                            node.iter.func.id == 'range'

            target_js = self._compile_value(node.target)  # noqa

            if is_range_call:
                call = node.iter
                if len(call.args) == 1:
                    limit_js = self._compile_value(call.args[0])  # noqa
                    return f"{indent}for (let {target_js} = 0; {target_js} < {limit_js}; {target_js}++) {{\n{body_js}\n{indent}}}"
                else:
                    raise PYJSCompilerUnitException("Only range(N) is supported for C-style loop translation in this unit.")

            iter_js = self._compile_value(node.iter)  # noqa
            return f"{indent}for (let {target_js} of {iter_js}) {{\n{body_js}\n{indent}}}"

        elif isinstance(node, ast.While):
            # 2. Compile body ONLY if the node is a loop type
            body_js = self._compile_body(node.body, indent_level + 1)  # noqa

            test_js = self._compile_value(node.test)  # noqa
            return f"{indent}while ({test_js}) {{\n{body_js}\n{indent}}}"

        else:
            raise PYJSCompilerUnitException(f"Unsupported loop node type: {type(node)}")

    def _compile_body(self, body_nodes: list[ast.AST], indent_level: int) -> str:
        js_lines = []
        indent = '    ' * indent_level

        for node in body_nodes:
            if isinstance(node, (ast.For, ast.While)):
                js_lines.append(self.compile(node, indent_level))  # noqa

            elif isinstance(node, ast.Assign):
                target_js = self._compile_value(node.targets[0])  # noqa
                value_js = self._compile_value(node.value)  # noqa
                js_lines.append(f'{indent}{target_js} = {value_js};')

            elif isinstance(node, ast.Expr):
                js_lines.append(f'{indent}{self._compile_value(node.value)};')  # noqa

            elif isinstance(node, ast.Return):
                value_js = self._compile_value(node.value) if node.value else 'undefined'  # noqa
                js_lines.append(f'{indent}return {value_js};')

            else:
                compiled_code = self._compile_value(node)
                indent = '    ' * indent_level
                indented_lines = [indent + line for line in compiled_code.splitlines() if line.strip()]  # noqa
                js_lines.extend(indented_lines)

        return '\n'.join(js_lines)
