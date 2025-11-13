from __future__ import annotations
from collections.abc import Callable
from typing import Any
from ...arctrl_core.data_map import DataMap
from ...arctrl_json.DataMap.data_map import (decoder as decoder_1, encoder)
from ...arctrl_json.encode import default_spaces
from ...fable_library.result import FSharpResult_2
from ...fable_library.string_ import (to_text, printf)
from ...thoth_json_core.types import IEncodable
from ...thoth_json_python.decode import Decode_fromString
from ...thoth_json_python.encode import to_string

def ARCtrl_DataMap__DataMap_fromJsonString_Static_Z721C83C5(s: str) -> DataMap:
    match_value: FSharpResult_2[DataMap, str] = Decode_fromString(decoder_1, s)
    if match_value.tag == 1:
        raise Exception(to_text(printf("Error decoding string: %O"))(match_value.fields[0]))

    else: 
        return match_value.fields[0]



def ARCtrl_DataMap__DataMap_toJsonString_Static_71136F3F(spaces: int | None=None) -> Callable[[DataMap], str]:
    def _arrow3736(obj: DataMap, spaces: Any=spaces) -> str:
        value: IEncodable = encoder(obj)
        return to_string(default_spaces(spaces), value)

    return _arrow3736


def ARCtrl_DataMap__DataMap_ToJsonString_71136F3F(this: DataMap, spaces: int | None=None) -> str:
    return ARCtrl_DataMap__DataMap_toJsonString_Static_71136F3F(spaces)(this)


__all__ = ["ARCtrl_DataMap__DataMap_fromJsonString_Static_Z721C83C5", "ARCtrl_DataMap__DataMap_toJsonString_Static_71136F3F", "ARCtrl_DataMap__DataMap_ToJsonString_71136F3F"]

