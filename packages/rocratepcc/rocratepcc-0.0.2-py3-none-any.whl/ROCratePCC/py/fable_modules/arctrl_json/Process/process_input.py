from __future__ import annotations
from typing import Any
from ...arctrl_core.data import Data
from ...arctrl_core.Process.material import Material
from ...arctrl_core.Process.process_input import ProcessInput
from ...arctrl_core.Process.sample import Sample
from ...arctrl_core.Process.source import Source
from ...fable_library.list import of_array
from ...thoth_json_core.decode import (one_of, map)
from ...thoth_json_core.types import (IEncodable, Decoder_1)
from ..data import (ROCrate_encoder as ROCrate_encoder_2, ROCrate_decoder as ROCrate_decoder_3, ISAJson_encoder as ISAJson_encoder_2, ISAJson_decoder as ISAJson_decoder_3)
from .material import (ROCrate_encoder as ROCrate_encoder_3, ROCrate_decoder as ROCrate_decoder_4, ISAJson_encoder as ISAJson_encoder_3, ISAJson_decoder as ISAJson_decoder_4)
from .sample import (ROCrate_encoder as ROCrate_encoder_1, ROCrate_decoder as ROCrate_decoder_1, ISAJson_encoder as ISAJson_encoder_1, ISAJson_decoder as ISAJson_decoder_2)
from .source import (ROCrate_encoder as ROCrate_encoder_4, ROCrate_decoder as ROCrate_decoder_2, ISAJson_encoder as ISAJson_encoder_4, ISAJson_decoder as ISAJson_decoder_1)

def ROCrate_encoder(value: ProcessInput) -> IEncodable:
    if value.tag == 1:
        return ROCrate_encoder_1(value.fields[0])

    elif value.tag == 2:
        return ROCrate_encoder_2(value.fields[0])

    elif value.tag == 3:
        return ROCrate_encoder_3(value.fields[0])

    else: 
        return ROCrate_encoder_4(value.fields[0])



def _arrow2116(Item: Sample) -> ProcessInput:
    return ProcessInput(1, Item)


def _arrow2117(Item_1: Source) -> ProcessInput:
    return ProcessInput(0, Item_1)


def _arrow2118(Item_2: Data) -> ProcessInput:
    return ProcessInput(2, Item_2)


def _arrow2119(Item_3: Material) -> ProcessInput:
    return ProcessInput(3, Item_3)


ROCrate_decoder: Decoder_1[ProcessInput] = one_of(of_array([map(_arrow2116, ROCrate_decoder_1), map(_arrow2117, ROCrate_decoder_2), map(_arrow2118, ROCrate_decoder_3), map(_arrow2119, ROCrate_decoder_4)]))

def ISAJson_encoder(id_map: Any | None, value: ProcessInput) -> IEncodable:
    if value.tag == 1:
        return ISAJson_encoder_1(id_map, value.fields[0])

    elif value.tag == 2:
        return ISAJson_encoder_2(id_map, value.fields[0])

    elif value.tag == 3:
        return ISAJson_encoder_3(id_map, value.fields[0])

    else: 
        return ISAJson_encoder_4(id_map, value.fields[0])



def _arrow2121(Item: Source) -> ProcessInput:
    return ProcessInput(0, Item)


def _arrow2122(Item_1: Sample) -> ProcessInput:
    return ProcessInput(1, Item_1)


def _arrow2123(Item_2: Data) -> ProcessInput:
    return ProcessInput(2, Item_2)


def _arrow2124(Item_3: Material) -> ProcessInput:
    return ProcessInput(3, Item_3)


ISAJson_decoder: Decoder_1[ProcessInput] = one_of(of_array([map(_arrow2121, ISAJson_decoder_1), map(_arrow2122, ISAJson_decoder_2), map(_arrow2123, ISAJson_decoder_3), map(_arrow2124, ISAJson_decoder_4)]))

__all__ = ["ROCrate_encoder", "ROCrate_decoder", "ISAJson_encoder", "ISAJson_decoder"]

