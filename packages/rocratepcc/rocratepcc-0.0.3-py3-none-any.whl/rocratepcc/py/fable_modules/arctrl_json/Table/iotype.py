from __future__ import annotations
from typing import Any
from ...arctrl_core.Table.composite_header import IOType
from ...fable_library.types import to_string
from ...thoth_json_core.decode import (and_then, succeed, string)
from ...thoth_json_core.types import (IEncodable, IEncoderHelpers_1, Decoder_1)

def encoder(io: IOType) -> IEncodable:
    value: str = to_string(io)
    class ObjectExpr2246(IEncodable):
        def Encode(self, helpers: IEncoderHelpers_1[Any], io: Any=io) -> Any:
            return helpers.encode_string(value)

    return ObjectExpr2246()


def cb(s: str) -> Decoder_1[IOType]:
    return succeed(IOType.of_string(s))


decoder: Decoder_1[IOType] = and_then(cb, string)

__all__ = ["encoder", "decoder"]

