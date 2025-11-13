from __future__ import annotations
from dataclasses import dataclass
from typing import (Any, TypeVar)
from ....fable_library.reflection import (TypeInfo, string_type, record_type)
from ....fable_library.seq import map
from ....fable_library.types import Record
from ....fable_library.util import (to_enumerable, IEnumerable_1)
from ....thoth_json_core.types import (IEncodable, IEncoderHelpers_1)

__A_ = TypeVar("__A_")

def _expr1265() -> TypeInfo:
    return record_type("ARCtrl.Json.ROCrateContext.ProcessParameterValue.IContext", [], IContext, lambda: [("sdo", string_type), ("arc", string_type), ("ProcessParameterValue", string_type), ("ArcProcessParameterValue", string_type), ("category", string_type), ("value", string_type), ("unit", string_type)])


@dataclass(eq = False, repr = False, slots = True)
class IContext(Record):
    sdo: str
    arc: str
    ProcessParameterValue: str
    ArcProcessParameterValue: str
    category: str
    value: str
    unit: str

IContext_reflection = _expr1265

def _arrow1276(__unit: None=None) -> IEncodable:
    class ObjectExpr1266(IEncodable):
        def Encode(self, helpers: IEncoderHelpers_1[Any]) -> Any:
            return helpers.encode_string("http://schema.org/")

    class ObjectExpr1267(IEncodable):
        def Encode(self, helpers_1: IEncoderHelpers_1[Any]) -> Any:
            return helpers_1.encode_string("sdo:additionalType")

    class ObjectExpr1268(IEncodable):
        def Encode(self, helpers_2: IEncoderHelpers_1[Any]) -> Any:
            return helpers_2.encode_string("sdo:PropertyValue")

    class ObjectExpr1269(IEncodable):
        def Encode(self, helpers_3: IEncoderHelpers_1[Any]) -> Any:
            return helpers_3.encode_string("sdo:name")

    class ObjectExpr1270(IEncodable):
        def Encode(self, helpers_4: IEncoderHelpers_1[Any]) -> Any:
            return helpers_4.encode_string("sdo:propertyID")

    class ObjectExpr1271(IEncodable):
        def Encode(self, helpers_5: IEncoderHelpers_1[Any]) -> Any:
            return helpers_5.encode_string("sdo:value")

    class ObjectExpr1272(IEncodable):
        def Encode(self, helpers_6: IEncoderHelpers_1[Any]) -> Any:
            return helpers_6.encode_string("sdo:valueReference")

    class ObjectExpr1273(IEncodable):
        def Encode(self, helpers_7: IEncoderHelpers_1[Any]) -> Any:
            return helpers_7.encode_string("sdo:unitText")

    class ObjectExpr1274(IEncodable):
        def Encode(self, helpers_8: IEncoderHelpers_1[Any]) -> Any:
            return helpers_8.encode_string("sdo:unitCode")

    values: IEnumerable_1[tuple[str, IEncodable]] = to_enumerable([("sdo", ObjectExpr1266()), ("additionalType", ObjectExpr1267()), ("ProcessParameterValue", ObjectExpr1268()), ("category", ObjectExpr1269()), ("categoryCode", ObjectExpr1270()), ("value", ObjectExpr1271()), ("valueCode", ObjectExpr1272()), ("unit", ObjectExpr1273()), ("unitCode", ObjectExpr1274())])
    class ObjectExpr1275(IEncodable):
        def Encode(self, helpers_9: IEncoderHelpers_1[Any]) -> Any:
            def mapping(tupled_arg: tuple[str, IEncodable]) -> tuple[str, __A_]:
                return (tupled_arg[0], tupled_arg[1].Encode(helpers_9))

            arg: IEnumerable_1[tuple[str, __A_]] = map(mapping, values)
            return helpers_9.encode_object(arg)

    return ObjectExpr1275()


context_jsonvalue: IEncodable = _arrow1276()

__all__ = ["IContext_reflection", "context_jsonvalue"]

