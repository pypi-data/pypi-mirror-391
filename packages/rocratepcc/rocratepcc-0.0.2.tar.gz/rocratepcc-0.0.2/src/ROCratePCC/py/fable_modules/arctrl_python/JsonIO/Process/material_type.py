from __future__ import annotations
from collections.abc import Callable
from typing import Any
from ....arctrl_core.Process.material_type import MaterialType
from ....arctrl_json.encode import default_spaces
from ....arctrl_json.Process.material_type import (ISAJson_decoder, ISAJson_encoder)
from ....fable_library.result import FSharpResult_2
from ....fable_library.string_ import (to_text, printf)
from ....thoth_json_core.types import IEncodable
from ....thoth_json_python.decode import Decode_fromString
from ....thoth_json_python.encode import to_string

def ARCtrl_Process_MaterialType__MaterialType_fromISAJsonString_Static_Z721C83C5(s: str) -> MaterialType:
    match_value: FSharpResult_2[MaterialType, str] = Decode_fromString(ISAJson_decoder, s)
    if match_value.tag == 1:
        raise Exception(to_text(printf("Error decoding string: %O"))(match_value.fields[0]))

    else: 
        return match_value.fields[0]



def ARCtrl_Process_MaterialType__MaterialType_toISAJsonString_Static_71136F3F(spaces: int | None=None) -> Callable[[MaterialType], str]:
    def _arrow3747(f: MaterialType, spaces: Any=spaces) -> str:
        value: IEncodable = ISAJson_encoder(f)
        return to_string(default_spaces(spaces), value)

    return _arrow3747


def ARCtrl_Process_MaterialType__MaterialType_ToISAJsonString_71136F3F(this: MaterialType, spaces: int | None=None) -> str:
    return ARCtrl_Process_MaterialType__MaterialType_toISAJsonString_Static_71136F3F(spaces)(this)


__all__ = ["ARCtrl_Process_MaterialType__MaterialType_fromISAJsonString_Static_Z721C83C5", "ARCtrl_Process_MaterialType__MaterialType_toISAJsonString_Static_71136F3F", "ARCtrl_Process_MaterialType__MaterialType_ToISAJsonString_71136F3F"]

