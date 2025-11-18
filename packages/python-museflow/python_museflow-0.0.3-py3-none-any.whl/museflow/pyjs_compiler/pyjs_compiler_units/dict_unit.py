import ast
from typing import Any

from museflow.pyjs_compiler.pyjs_compiler_unit_abs import PYJSCompilerUnit, PYJSCompilerUnitException


class DictUnit(PYJSCompilerUnit):
    @property
    def variant(self) -> Any:
        return ast.Dict

    def compile(self, node: ast.AST) -> str:
        if not isinstance(node, ast.Dict):
            raise PYJSCompilerUnitException(f'Invalid node type: {type(node)}, expected: Dict')

        js_items = []
        for key_node, value_node in zip(node.keys, node.values):
            key_js = self._compile_key(key_node)  # noqa
            value_js = self._compile_value(value_node)  # noqa
            js_items.append(f'{key_js}: {value_js}')

        return f'{{{", ".join(js_items)}}}'

    # noinspection PyMethodMayBeStatic
    def _compile_key(self, node: ast.AST) -> str:
        if isinstance(node, ast.Constant):
            if isinstance(node.value, str):
                return f'"{node.value}"'
            if isinstance(node.value, int):
                return str(node.value)
            if node.value is None:
                return 'null'
        if isinstance(node, ast.Name):
            return node.id
        raise PYJSCompilerUnitException(f'Unsupported dict key type: {type(node)}')
