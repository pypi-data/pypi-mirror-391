import ast
from typing import Any

from museflow.pyjs_compiler.pyjs_compiler_unit_abs import PYJSCompilerUnit, PYJSCompilerUnitException


class TryUnit(PYJSCompilerUnit):
    @property
    def variant(self) -> Any:
        return ast.Try

    def compile(self, node: ast.AST) -> str:
        if not isinstance(node, ast.Try):
            raise PYJSCompilerUnitException(f'Invalid node type: {type(node)}, expected: Try')

        js_lines = []

        try_body = self._indent('\n'.join(self._compile_value(stmt) for stmt in node.body))  # noqa
        js_lines.append(f'try {{\n{try_body}\n}}')

        for handler in node.handlers:
            exc_name = handler.name or 'e'
            handler_body = self._indent('\n'.join(self._compile_value(stmt) for stmt in handler.body))
            if handler.type:
                type_check = self._compile_value(handler.type)
                js_lines.append(
                    f'catch ({exc_name}) {{ if (!({exc_name} instanceof {type_check})) throw {exc_name};\n{handler_body}\n}}'
                )
            else:
                js_lines.append(f'catch ({exc_name}) {{\n{handler_body}\n}}')

        # Compile finally block
        if node.finalbody:
            final_body = self._indent('\n'.join(self._compile_value(stmt) for stmt in node.finalbody))
            js_lines.append(f'finally {{\n{final_body}\n}}')

        return '\n'.join(js_lines)

    def _compile_value(self, node: ast.AST) -> str:
        """Compile a node using dispatch_map, or handle constants directly."""
        node_type = type(node)

        # Handle constants separately
        if isinstance(node, ast.Constant):
            v = node.value
            # Dispatch booleans
            if isinstance(v, bool):
                unit = self._import_unit("bool_unit.BoolUnit")()
                return unit.compile(node)
            if v is None:
                return 'null'
            if isinstance(v, str):
                return f'"{v}"'
            return str(v)

        if node_type in self.dispatch_map:
            factory = self.dispatch_map[node_type]
            if factory is None:
                raise PYJSCompilerUnitException(f'Cannot handle {node_type} via dispatch_map')
            return factory.compile(node)

        raise PYJSCompilerUnitException(f'Unsupported node type in TryUnit: {type(node)}')

    @staticmethod
    def _indent(code: str, level: int = 1) -> str:
        prefix = '  ' * level
        return '\n'.join(prefix + line if line.strip() else line for line in code.split('\n'))

    @staticmethod
    def _import_unit(path: str):
        module_name, class_name = path.rsplit(".", 1)
        module = __import__(f'pyjs_compiler.pyjs_compiler_units.{module_name}', fromlist=[class_name])
        return getattr(module, class_name)
