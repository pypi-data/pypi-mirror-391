from __future__ import annotations
from collections.abc import Callable
from typing import Any
from ....arctrl_core.Process.protocol_parameter import ProtocolParameter
from ....arctrl_json.encode import default_spaces
from ....arctrl_json.Process.protocol_parameter import (ISAJson_decoder, ISAJson_encoder)
from ....fable_library.result import FSharpResult_2
from ....fable_library.string_ import (to_text, printf)
from ....thoth_json_core.types import IEncodable
from ....thoth_json_python.decode import Decode_fromString
from ....thoth_json_python.encode import to_string

def ARCtrl_Process_ProtocolParameter__ProtocolParameter_fromISAJsonString_Static_Z721C83C5(s: str) -> ProtocolParameter:
    match_value: FSharpResult_2[ProtocolParameter, str] = Decode_fromString(ISAJson_decoder, s)
    if match_value.tag == 1:
        raise Exception(to_text(printf("Error decoding string: %O"))(match_value.fields[0]))

    else: 
        return match_value.fields[0]



def ARCtrl_Process_ProtocolParameter__ProtocolParameter_toISAJsonString_Static_71136F3F(spaces: int | None=None) -> Callable[[ProtocolParameter], str]:
    def _arrow3746(v: ProtocolParameter, spaces: Any=spaces) -> str:
        value: IEncodable = ISAJson_encoder(None, v)
        return to_string(default_spaces(spaces), value)

    return _arrow3746


def ARCtrl_Process_ProtocolParameter__ProtocolParameter_ToISAJsonString_71136F3F(this: ProtocolParameter, spaces: int | None=None) -> str:
    return ARCtrl_Process_ProtocolParameter__ProtocolParameter_toISAJsonString_Static_71136F3F(spaces)(this)


__all__ = ["ARCtrl_Process_ProtocolParameter__ProtocolParameter_fromISAJsonString_Static_Z721C83C5", "ARCtrl_Process_ProtocolParameter__ProtocolParameter_toISAJsonString_Static_71136F3F", "ARCtrl_Process_ProtocolParameter__ProtocolParameter_ToISAJsonString_71136F3F"]

