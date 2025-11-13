from __future__ import annotations
from dataclasses import dataclass
from typing import (Any, TypeVar)
from ....fable_library.reflection import (TypeInfo, string_type, record_type)
from ....fable_library.seq import map
from ....fable_library.types import Record
from ....fable_library.util import (to_enumerable, IEnumerable_1)
from ....thoth_json_core.types import (IEncodable, IEncoderHelpers_1)

__A_ = TypeVar("__A_")

def _expr1277() -> TypeInfo:
    return record_type("ARCtrl.Json.ROCrateContext.Protocol.IContext", [], IContext, lambda: [("sdo", string_type), ("arc", string_type), ("Protocol", string_type), ("ArcProtocol", string_type), ("name", string_type), ("protocol_type", string_type), ("description", string_type), ("version", string_type), ("components", string_type), ("parameters", string_type), ("uri", string_type), ("comments", string_type)])


@dataclass(eq = False, repr = False, slots = True)
class IContext(Record):
    sdo: str
    arc: str
    Protocol: str
    ArcProtocol: str
    name: str
    protocol_type: str
    description: str
    version: str
    components: str
    parameters: str
    uri: str
    comments: str

IContext_reflection = _expr1277

def _arrow1291(__unit: None=None) -> IEncodable:
    class ObjectExpr1278(IEncodable):
        def Encode(self, helpers: IEncoderHelpers_1[Any]) -> Any:
            return helpers.encode_string("http://schema.org/")

    class ObjectExpr1279(IEncodable):
        def Encode(self, helpers_1: IEncoderHelpers_1[Any]) -> Any:
            return helpers_1.encode_string("https://bioschemas.org/")

    class ObjectExpr1280(IEncodable):
        def Encode(self, helpers_2: IEncoderHelpers_1[Any]) -> Any:
            return helpers_2.encode_string("bio:LabProtocol")

    class ObjectExpr1281(IEncodable):
        def Encode(self, helpers_3: IEncoderHelpers_1[Any]) -> Any:
            return helpers_3.encode_string("sdo:name")

    class ObjectExpr1282(IEncodable):
        def Encode(self, helpers_4: IEncoderHelpers_1[Any]) -> Any:
            return helpers_4.encode_string("bio:intendedUse")

    class ObjectExpr1283(IEncodable):
        def Encode(self, helpers_5: IEncoderHelpers_1[Any]) -> Any:
            return helpers_5.encode_string("sdo:description")

    class ObjectExpr1284(IEncodable):
        def Encode(self, helpers_6: IEncoderHelpers_1[Any]) -> Any:
            return helpers_6.encode_string("sdo:version")

    class ObjectExpr1285(IEncodable):
        def Encode(self, helpers_7: IEncoderHelpers_1[Any]) -> Any:
            return helpers_7.encode_string("bio:labEquipment")

    class ObjectExpr1286(IEncodable):
        def Encode(self, helpers_8: IEncoderHelpers_1[Any]) -> Any:
            return helpers_8.encode_string("bio:reagent")

    class ObjectExpr1287(IEncodable):
        def Encode(self, helpers_9: IEncoderHelpers_1[Any]) -> Any:
            return helpers_9.encode_string("bio:computationalTool")

    class ObjectExpr1288(IEncodable):
        def Encode(self, helpers_10: IEncoderHelpers_1[Any]) -> Any:
            return helpers_10.encode_string("sdo:url")

    class ObjectExpr1289(IEncodable):
        def Encode(self, helpers_11: IEncoderHelpers_1[Any]) -> Any:
            return helpers_11.encode_string("sdo:comment")

    values: IEnumerable_1[tuple[str, IEncodable]] = to_enumerable([("sdo", ObjectExpr1278()), ("bio", ObjectExpr1279()), ("Protocol", ObjectExpr1280()), ("name", ObjectExpr1281()), ("protocolType", ObjectExpr1282()), ("description", ObjectExpr1283()), ("version", ObjectExpr1284()), ("components", ObjectExpr1285()), ("reagents", ObjectExpr1286()), ("computationalTools", ObjectExpr1287()), ("uri", ObjectExpr1288()), ("comments", ObjectExpr1289())])
    class ObjectExpr1290(IEncodable):
        def Encode(self, helpers_12: IEncoderHelpers_1[Any]) -> Any:
            def mapping(tupled_arg: tuple[str, IEncodable]) -> tuple[str, __A_]:
                return (tupled_arg[0], tupled_arg[1].Encode(helpers_12))

            arg: IEnumerable_1[tuple[str, __A_]] = map(mapping, values)
            return helpers_12.encode_object(arg)

    return ObjectExpr1290()


context_jsonvalue: IEncodable = _arrow1291()

__all__ = ["IContext_reflection", "context_jsonvalue"]

