from __future__ import annotations
from collections.abc import Callable
from typing import (Any, TypeVar)
from ..arctrl_core.data_file import DataFile
from ..fable_library.result import FSharpResult_2
from ..thoth_json_core.decode import string
from ..thoth_json_core.types import (IEncodable, IEncoderHelpers_1, Decoder_1, ErrorReason_1, IDecoderHelpers_1)

__A_ = TypeVar("__A_")

def ROCrate_encoder(value: DataFile) -> IEncodable:
    if value.tag == 1:
        class ObjectExpr1577(IEncodable):
            def Encode(self, helpers_1: IEncoderHelpers_1[Any], value: Any=value) -> Any:
                return helpers_1.encode_string("Derived Data File")

        return ObjectExpr1577()

    elif value.tag == 2:
        class ObjectExpr1580(IEncodable):
            def Encode(self, helpers_2: IEncoderHelpers_1[Any], value: Any=value) -> Any:
                return helpers_2.encode_string("Image File")

        return ObjectExpr1580()

    else: 
        class ObjectExpr1582(IEncodable):
            def Encode(self, helpers: IEncoderHelpers_1[Any], value: Any=value) -> Any:
                return helpers.encode_string("Raw Data File")

        return ObjectExpr1582()



class ObjectExpr1591(Decoder_1[DataFile]):
    def Decode(self, s: IDecoderHelpers_1[Any], json: Any) -> FSharpResult_2[DataFile, tuple[str, ErrorReason_1[__A_]]]:
        match_value: FSharpResult_2[str, tuple[str, ErrorReason_1[__A_]]] = string.Decode(s, json)
        if match_value.tag == 1:
            return FSharpResult_2(1, match_value.fields[0])

        elif match_value.fields[0] == "Raw Data File":
            return FSharpResult_2(0, DataFile(0))

        elif match_value.fields[0] == "Derived Data File":
            return FSharpResult_2(0, DataFile(1))

        elif match_value.fields[0] == "Image File":
            return FSharpResult_2(0, DataFile(2))

        else: 
            s_1: str = match_value.fields[0]
            return FSharpResult_2(1, (("Could not parse " + s_1) + ".", ErrorReason_1(0, s_1, json)))



ROCrate_decoder: Decoder_1[DataFile] = ObjectExpr1591()

ISAJson_encoder: Callable[[DataFile], IEncodable] = ROCrate_encoder

ISAJson_decoder: Decoder_1[DataFile] = ROCrate_decoder

__all__ = ["ROCrate_encoder", "ROCrate_decoder", "ISAJson_encoder", "ISAJson_decoder"]

