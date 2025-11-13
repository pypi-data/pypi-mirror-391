from __future__ import annotations
from dataclasses import dataclass
from typing import (Any, TypeVar)
from ....fable_library.reflection import (TypeInfo, string_type, record_type)
from ....fable_library.seq import map
from ....fable_library.types import Record
from ....fable_library.util import (to_enumerable, IEnumerable_1)
from ....thoth_json_core.types import (IEncodable, IEncoderHelpers_1)

__A_ = TypeVar("__A_")

def _expr1136() -> TypeInfo:
    return record_type("ARCtrl.Json.ROCrateContext.Factor.IContext", [], IContext, lambda: [("sdo", string_type), ("arc", string_type), ("Factor", string_type), ("ArcFactor", string_type), ("factor_name", string_type), ("factor_type", string_type), ("comments", string_type)])


@dataclass(eq = False, repr = False, slots = True)
class IContext(Record):
    sdo: str
    arc: str
    Factor: str
    ArcFactor: str
    factor_name: str
    factor_type: str
    comments: str

IContext_reflection = _expr1136

def _arrow1145(__unit: None=None) -> IEncodable:
    class ObjectExpr1137(IEncodable):
        def Encode(self, helpers: IEncoderHelpers_1[Any]) -> Any:
            return helpers.encode_string("http://schema.org/")

    class ObjectExpr1138(IEncodable):
        def Encode(self, helpers_1: IEncoderHelpers_1[Any]) -> Any:
            return helpers_1.encode_string("sdo:DefinedTerm")

    class ObjectExpr1139(IEncodable):
        def Encode(self, helpers_2: IEncoderHelpers_1[Any]) -> Any:
            return helpers_2.encode_string("sdo:name")

    class ObjectExpr1140(IEncodable):
        def Encode(self, helpers_3: IEncoderHelpers_1[Any]) -> Any:
            return helpers_3.encode_string("sdo:name")

    class ObjectExpr1141(IEncodable):
        def Encode(self, helpers_4: IEncoderHelpers_1[Any]) -> Any:
            return helpers_4.encode_string("sdo:inDefinedTermSet")

    class ObjectExpr1142(IEncodable):
        def Encode(self, helpers_5: IEncoderHelpers_1[Any]) -> Any:
            return helpers_5.encode_string("sdo:termCode")

    class ObjectExpr1143(IEncodable):
        def Encode(self, helpers_6: IEncoderHelpers_1[Any]) -> Any:
            return helpers_6.encode_string("sdo:disambiguatingDescription")

    values: IEnumerable_1[tuple[str, IEncodable]] = to_enumerable([("sdo", ObjectExpr1137()), ("Factor", ObjectExpr1138()), ("factorName", ObjectExpr1139()), ("annotationValue", ObjectExpr1140()), ("termSource", ObjectExpr1141()), ("termAccession", ObjectExpr1142()), ("comments", ObjectExpr1143())])
    class ObjectExpr1144(IEncodable):
        def Encode(self, helpers_7: IEncoderHelpers_1[Any]) -> Any:
            def mapping(tupled_arg: tuple[str, IEncodable]) -> tuple[str, __A_]:
                return (tupled_arg[0], tupled_arg[1].Encode(helpers_7))

            arg: IEnumerable_1[tuple[str, __A_]] = map(mapping, values)
            return helpers_7.encode_object(arg)

    return ObjectExpr1144()


context_jsonvalue: IEncodable = _arrow1145()

context_str: str = "\r\n{\r\n  \"@context\": {\r\n    \"sdo\": \"http://schema.org/\",\r\n    \"arc\": \"http://purl.org/nfdi4plants/ontology/\",\r\n\r\n    \"Factor\": \"sdo:Thing\",\r\n    \"ArcFactor\": \"arc:ARC#ARC_00000044\",\r\n\r\n    \"factorName\": \"arc:ARC#ARC_00000019\",\r\n    \"factorType\": \"arc:ARC#ARC_00000078\",\r\n\r\n    \"comments\": \"sdo:disambiguatingDescription\"\r\n  }\r\n}\r\n    "

__all__ = ["IContext_reflection", "context_jsonvalue", "context_str"]

