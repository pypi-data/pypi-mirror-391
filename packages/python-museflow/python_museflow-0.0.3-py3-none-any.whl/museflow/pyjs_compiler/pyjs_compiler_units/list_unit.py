import ast
from typing import Any

from museflow.pyjs_compiler.pyjs_compiler_unit_abs import PYJSCompilerUnit, PYJSCompilerUnitException


class ListUnit(PYJSCompilerUnit):
    @property
    def variant(self) -> Any:
        return ast.List

    def compile(self, node: ast.List) -> str:
        if not isinstance(node, ast.List):
            raise PYJSCompilerUnitException(f'Invalid node type: {type(node)}, expected: List')

        elements = [self._compile_element(e) for e in node.elts]
        return f'[{', '.join(elements)}]'

    def _compile_element(self, node: ast.AST) -> str:
        """Compile list elements recursively using dispatch_map."""
        if isinstance(node, ast.Constant):
            v = node.value
            if isinstance(v, bool):
                unit = self._import_unit('bool_unit.BoolUnit')()
                return unit.compile(node)
            if v is None:
                unit = self._import_unit('none_unit.NoneUnit')()
                return unit.compile(node)
            if isinstance(v, str):
                unit = self._import_unit('str_unit.StrUnit')()
                return unit.compile(node)
            if isinstance(v, int):
                unit = self._import_unit('int_unit.IntUnit')()
                return unit.compile(node)
            if isinstance(v, float):
                unit = self._import_unit('float_unit.FloatUnit')()
                return unit.compile(node)

        # Use dispatch_map for other AST types
        node_type = type(node)
        if node_type in self.dispatch_map:
            unit_factory = self.dispatch_map[node_type]
            if unit_factory is None:
                raise PYJSCompilerUnitException(f'Cannot handle {node_type} via dispatch_map')
            return unit_factory.compile(node)

        raise PYJSCompilerUnitException(f'Unsupported list element type: {type(node)}')

    @staticmethod
    def _import_unit(path: str):
        """ Dynamically import a unit class from a string path """
        module_name, class_name = path.rsplit('.', 1)
        module = __import__(f'museflow.pyjs_compiler.pyjs_compiler_units.{module_name}', fromlist=[class_name])
        return getattr(module, class_name)
