from __future__ import annotations
from typing import (Any, TypeVar)
from ....fable_library.seq import map
from ....fable_library.util import (to_enumerable, IEnumerable_1)
from ....thoth_json_core.types import (IEncodable, IEncoderHelpers_1)

__A_ = TypeVar("__A_")

def _arrow1092(__unit: None=None) -> IEncodable:
    class ObjectExpr1079(IEncodable):
        def Encode(self, helpers: IEncoderHelpers_1[Any]) -> Any:
            return helpers.encode_string("http://schema.org/")

    class ObjectExpr1080(IEncodable):
        def Encode(self, helpers_1: IEncoderHelpers_1[Any]) -> Any:
            return helpers_1.encode_string("sdo:additionalType")

    class ObjectExpr1081(IEncodable):
        def Encode(self, helpers_2: IEncoderHelpers_1[Any]) -> Any:
            return helpers_2.encode_string("sdo:alternateName")

    class ObjectExpr1082(IEncodable):
        def Encode(self, helpers_3: IEncoderHelpers_1[Any]) -> Any:
            return helpers_3.encode_string("sdo:measurementMethod")

    class ObjectExpr1083(IEncodable):
        def Encode(self, helpers_4: IEncoderHelpers_1[Any]) -> Any:
            return helpers_4.encode_string("sdo:description")

    class ObjectExpr1084(IEncodable):
        def Encode(self, helpers_5: IEncoderHelpers_1[Any]) -> Any:
            return helpers_5.encode_string("sdo:name")

    class ObjectExpr1085(IEncodable):
        def Encode(self, helpers_6: IEncoderHelpers_1[Any]) -> Any:
            return helpers_6.encode_string("sdo:propertyID")

    class ObjectExpr1086(IEncodable):
        def Encode(self, helpers_7: IEncoderHelpers_1[Any]) -> Any:
            return helpers_7.encode_string("sdo:value")

    class ObjectExpr1087(IEncodable):
        def Encode(self, helpers_8: IEncoderHelpers_1[Any]) -> Any:
            return helpers_8.encode_string("sdo:valueReference")

    class ObjectExpr1088(IEncodable):
        def Encode(self, helpers_9: IEncoderHelpers_1[Any]) -> Any:
            return helpers_9.encode_string("sdo:unitText")

    class ObjectExpr1089(IEncodable):
        def Encode(self, helpers_10: IEncoderHelpers_1[Any]) -> Any:
            return helpers_10.encode_string("sdo:unitCode")

    class ObjectExpr1090(IEncodable):
        def Encode(self, helpers_11: IEncoderHelpers_1[Any]) -> Any:
            return helpers_11.encode_string("sdo:disambiguatingDescription")

    values: IEnumerable_1[tuple[str, IEncodable]] = to_enumerable([("sdo", ObjectExpr1079()), ("additionalType", ObjectExpr1080()), ("alternateName", ObjectExpr1081()), ("measurementMethod", ObjectExpr1082()), ("description", ObjectExpr1083()), ("category", ObjectExpr1084()), ("categoryCode", ObjectExpr1085()), ("value", ObjectExpr1086()), ("valueCode", ObjectExpr1087()), ("unit", ObjectExpr1088()), ("unitCode", ObjectExpr1089()), ("comments", ObjectExpr1090())])
    class ObjectExpr1091(IEncodable):
        def Encode(self, helpers_12: IEncoderHelpers_1[Any]) -> Any:
            def mapping(tupled_arg: tuple[str, IEncodable]) -> tuple[str, __A_]:
                return (tupled_arg[0], tupled_arg[1].Encode(helpers_12))

            arg: IEnumerable_1[tuple[str, __A_]] = map(mapping, values)
            return helpers_12.encode_object(arg)

    return ObjectExpr1091()


context_jsonvalue: IEncodable = _arrow1092()

__all__ = ["context_jsonvalue"]

