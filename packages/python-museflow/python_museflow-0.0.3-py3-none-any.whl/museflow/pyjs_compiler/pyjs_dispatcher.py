from typing import Dict, TYPE_CHECKING, Any

if TYPE_CHECKING:
    from museflow.pyjs_compiler.pyjs_compiler_unit_abs import PYJSCompilerUnit


class PYJSDispatcher:
    """ Provides a lazy-access dispatch map for compiler units """

    __dispatch_map: Dict[Any, 'PYJSCompilerUnit'] | None = None

    @classmethod
    def get_dispatch_map(cls) -> Dict[Any, 'PYJSCompilerUnit']:
        """ Return (and cache) the Nexus dispatch map without creating circular imports """
        if cls.__dispatch_map is None:
            from museflow.pyjs_compiler.pyjs_nexus import PYJSNexus
            cls.__dispatch_map = PYJSNexus.to_dispatch_map()
        return cls.__dispatch_map
