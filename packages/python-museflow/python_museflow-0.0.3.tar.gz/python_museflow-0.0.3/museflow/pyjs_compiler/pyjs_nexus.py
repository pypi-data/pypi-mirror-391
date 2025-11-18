from dataclasses import dataclass

from museflow.pyjs_compiler.pyjs_compiler_units.assign_unit import AssignUnit
from museflow.pyjs_compiler.pyjs_compiler_units.augassign_unit import AugAssignUnit
from museflow.pyjs_compiler.pyjs_compiler_units.binop_unit import BinOpUnit
from museflow.pyjs_compiler.pyjs_compiler_units.boolop_unit import BoolOpUnit
from museflow.pyjs_compiler.pyjs_compiler_units.break_unit import BreakUnit
from museflow.pyjs_compiler.pyjs_compiler_units.call_unit import CallUnit
from museflow.pyjs_compiler.pyjs_compiler_units.compare_unit import CompareUnit
from museflow.pyjs_compiler.pyjs_compiler_units.constant_unit import ConstantUnit
from museflow.pyjs_compiler.pyjs_compiler_units.continue_unit import ContinueUnit
from museflow.pyjs_compiler.pyjs_compiler_units.dict_unit import DictUnit
from museflow.pyjs_compiler.pyjs_compiler_units.expr_unit import ExprUnit
from museflow.pyjs_compiler.pyjs_compiler_units.fstring_unit import FStringUnit
from museflow.pyjs_compiler.pyjs_compiler_units.function_unit import FunctionUnit
from museflow.pyjs_compiler.pyjs_compiler_units.get_attr_unit import GetAttrUnit
from museflow.pyjs_compiler.pyjs_compiler_units.get_item_unit import GetItemUnit
from museflow.pyjs_compiler.pyjs_compiler_units.global_unit import GlobalUnit
from museflow.pyjs_compiler.pyjs_compiler_units.if_unit import IfUnit
from museflow.pyjs_compiler.pyjs_compiler_units.list_unit import ListUnit
from museflow.pyjs_compiler.pyjs_compiler_units.loop_unit import LoopUnit
from museflow.pyjs_compiler.pyjs_compiler_units.name_unit import NameUnit
from museflow.pyjs_compiler.pyjs_compiler_units.return_unit import ReturnUnit
from museflow.pyjs_compiler.pyjs_compiler_units.set_unit import SetUnit
from museflow.pyjs_compiler.pyjs_compiler_units.try_unit import TryUnit
from museflow.pyjs_compiler.pyjs_compiler_units.tuple_unit import TupleUnit
from museflow.pyjs_compiler.pyjs_compiler_units.unaryop_unit import UnaryOpUnit


@dataclass(frozen=True)
class PYJSNexus:
    """ Nexus for Python-to-JavaScript compilers """

    ExprUnit = ExprUnit()
    ConstantUnit = ConstantUnit()
    AssignUnit = AssignUnit()
    NameUnit = NameUnit()
    CallUnit = CallUnit()
    ListUnit = ListUnit()
    TupleUnit = TupleUnit()
    SetUnit = SetUnit()
    DictUnit = DictUnit()
    BinOpUnit = BinOpUnit()
    FunctionUnit = FunctionUnit()
    IfUnit = IfUnit()
    LoopUnit = LoopUnit()
    FStringUnit = FStringUnit()
    BreakUnit = BreakUnit()
    ContinueUnit = ContinueUnit()
    GetAttrUnit = GetAttrUnit()
    GetItemUnit = GetItemUnit()
    ReturnUnit = ReturnUnit()
    AugAssignUnit = AugAssignUnit()
    TryUnit = TryUnit()
    CompareUnit = CompareUnit()
    BoolOpUnit = BoolOpUnit()
    GlobalUnit = GlobalUnit()
    UnaryOPUnit = UnaryOpUnit()

    @classmethod
    def to_dispatch_map(cls) -> dict:
        def is_unit(obj):
            return any(base.__name__ == 'PYJSCompilerUnit' for base in type(obj).__mro__)

        return {unit.variant: unit for unit in cls.__dict__.values() if is_unit(unit)}
