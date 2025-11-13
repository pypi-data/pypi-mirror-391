from __future__ import annotations
from collections.abc import Callable
from typing import Any
from ....arctrl_core.Process.factor_value import FactorValue
from ....arctrl_json.encode import default_spaces
from ....arctrl_json.Process.factor_value import (ISAJson_decoder, ISAJson_encoder)
from ....fable_library.option import default_arg
from ....fable_library.result import FSharpResult_2
from ....fable_library.string_ import (to_text, printf)
from ....thoth_json_core.types import IEncodable
from ....thoth_json_python.decode import Decode_fromString
from ....thoth_json_python.encode import to_string

def ARCtrl_Process_FactorValue__FactorValue_fromISAJsonString_Static_Z721C83C5(s: str) -> FactorValue:
    match_value: FSharpResult_2[FactorValue, str] = Decode_fromString(ISAJson_decoder, s)
    if match_value.tag == 1:
        raise Exception(to_text(printf("Error decoding string: %O"))(match_value.fields[0]))

    else: 
        return match_value.fields[0]



def ARCtrl_Process_FactorValue__FactorValue_toISAJsonString_Static_Z3B036AA(spaces: int | None=None, use_idreferencing: bool | None=None) -> Callable[[FactorValue], str]:
    id_map: Any | None = dict([]) if default_arg(use_idreferencing, False) else None
    def _arrow3745(f: FactorValue, spaces: Any=spaces, use_idreferencing: Any=use_idreferencing) -> str:
        value: IEncodable = ISAJson_encoder(id_map, f)
        return to_string(default_spaces(spaces), value)

    return _arrow3745


def ARCtrl_Process_FactorValue__FactorValue_ToISAJsonString_Z3B036AA(this: FactorValue, spaces: int | None=None, use_idreferencing: bool | None=None) -> str:
    return ARCtrl_Process_FactorValue__FactorValue_toISAJsonString_Static_Z3B036AA(spaces, use_idreferencing)(this)


__all__ = ["ARCtrl_Process_FactorValue__FactorValue_fromISAJsonString_Static_Z721C83C5", "ARCtrl_Process_FactorValue__FactorValue_toISAJsonString_Static_Z3B036AA", "ARCtrl_Process_FactorValue__FactorValue_ToISAJsonString_Z3B036AA"]

