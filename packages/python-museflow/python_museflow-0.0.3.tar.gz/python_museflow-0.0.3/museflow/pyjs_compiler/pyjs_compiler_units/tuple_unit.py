import ast
from typing import Any

from museflow.pyjs_compiler.pyjs_compiler_unit_abs import PYJSCompilerUnit, PYJSCompilerUnitException


class TupleUnit(PYJSCompilerUnit):
    @property
    def variant(self) -> Any:
        return ast.Tuple

    def compile(self, node: ast.Tuple) -> str:
        if not isinstance(node, ast.Tuple):
            raise PYJSCompilerUnitException(f'Unsupported node: {type(node)}')

        elements_js = [self._compile_value(e) for e in node.elts]  # noqa
        return f'[{', '.join(elements_js)}]'

    def _compile_value(self, node: ast.AST) -> str:
        # Handle constants separately
        if isinstance(node, ast.Constant):
            v = node.value
            if isinstance(v, bool):
                unit = self._import_unit('bool_unit.BoolUnit')()
                return unit.compile(node)
            if v is None:
                return 'null'
            if isinstance(v, str):
                return f'"{v}"'
            if isinstance(v, (int, float)):
                return str(v)

        # Dispatch other node types dynamically
        node_type = type(node)
        if node_type in self.dispatch_map:
            factory = self.dispatch_map[node_type]
            if factory is None:
                raise PYJSCompilerUnitException(f'Cannot handle {node_type} via dispatch_map')
            return factory.compile(node)

        raise PYJSCompilerUnitException(f'Unsupported tuple element type: {type(node)}')

    @staticmethod
    def _import_unit(path: str):
        """Dynamically import a unit class from a string path."""
        module_name, class_name = path.rsplit('.', 1)
        module = __import__(f'museflow.pyjs_compiler.pyjs_compiler_units.{module_name}', fromlist=[class_name])
        return getattr(module, class_name)
