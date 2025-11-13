from __future__ import annotations
from typing import Any
from ...arctrl_core.ontology_annotation import OntologyAnnotation
from ...arctrl_core.value import Value
from ...fable_library.list import of_array
from ...thoth_json_core.decode import (one_of, map, int_1, float_1, string)
from ...thoth_json_core.types import (IEncodable, IEncoderHelpers_1, Decoder_1)
from ..ontology_annotation import (OntologyAnnotation_ISAJson_encoder, OntologyAnnotation_ISAJson_decoder)

def encoder(id_map: Any | None, value: Value) -> IEncodable:
    if value.tag == 1:
        class ObjectExpr1724(IEncodable):
            def Encode(self, helpers_1: IEncoderHelpers_1[Any], id_map: Any=id_map, value: Any=value) -> Any:
                return helpers_1.encode_signed_integral_number(value.fields[0])

        return ObjectExpr1724()

    elif value.tag == 3:
        class ObjectExpr1725(IEncodable):
            def Encode(self, helpers_2: IEncoderHelpers_1[Any], id_map: Any=id_map, value: Any=value) -> Any:
                return helpers_2.encode_string(value.fields[0])

        return ObjectExpr1725()

    elif value.tag == 0:
        return OntologyAnnotation_ISAJson_encoder(id_map, value.fields[0])

    else: 
        class ObjectExpr1726(IEncodable):
            def Encode(self, helpers: IEncoderHelpers_1[Any], id_map: Any=id_map, value: Any=value) -> Any:
                return helpers.encode_decimal_number(value.fields[0])

        return ObjectExpr1726()



def _arrow1728(Item: int) -> Value:
    return Value(1, Item)


def _arrow1729(Item_1: float) -> Value:
    return Value(2, Item_1)


def _arrow1730(Item_2: OntologyAnnotation) -> Value:
    return Value(0, Item_2)


def _arrow1731(Item_3: str) -> Value:
    return Value(3, Item_3)


decoder: Decoder_1[Value] = one_of(of_array([map(_arrow1728, int_1), map(_arrow1729, float_1), map(_arrow1730, OntologyAnnotation_ISAJson_decoder), map(_arrow1731, string)]))

__all__ = ["encoder", "decoder"]

