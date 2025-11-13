from __future__ import annotations
from collections.abc import Callable
from typing import (Any, TypeVar)
from ...arctrl_core.comment import Comment
from ...arctrl_core.Process.process import Process
from ...arctrl_core.Process.process_input import ProcessInput
from ...arctrl_core.Process.process_output import ProcessOutput
from ...arctrl_core.Process.process_parameter_value import ProcessParameterValue
from ...arctrl_core.Process.protocol import Protocol
from ...arctrl_core.uri import URIModule_toString
from ...fable_library.list import (choose, singleton, of_array, FSharpList)
from ...fable_library.option import map
from ...fable_library.seq import map as map_1
from ...fable_library.string_ import replace
from ...fable_library.util import IEnumerable_1
from ...thoth_json_core.decode import (object, IOptionalGetter, string, list_1 as list_1_2, IGetters)
from ...thoth_json_core.encode import list_1 as list_1_1
from ...thoth_json_core.types import (IEncodable, IEncoderHelpers_1, Decoder_1)
from ..comment import (ROCrate_encoder as ROCrate_encoder_5, ROCrate_decoder as ROCrate_decoder_5, ISAJson_encoder as ISAJson_encoder_5, ISAJson_decoder as ISAJson_decoder_5)
from ..context.rocrate.isa_process_context import context_jsonvalue
from ..decode import Decode_uri
from ..encode import (try_include, try_include_list_opt)
from ..idtable import encode
from ..person import (ROCrate_encodeAuthorListString, ROCrate_decodeAuthorListString)
from .process_input import (ROCrate_encoder as ROCrate_encoder_3, ROCrate_decoder as ROCrate_decoder_3, ISAJson_encoder as ISAJson_encoder_3, ISAJson_decoder as ISAJson_decoder_3)
from .process_output import (ROCrate_encoder as ROCrate_encoder_4, ROCrate_decoder as ROCrate_decoder_4, ISAJson_encoder as ISAJson_encoder_4, ISAJson_decoder as ISAJson_decoder_4)
from .process_parameter_value import (ROCrate_encoder as ROCrate_encoder_2, ROCrate_decoder as ROCrate_decoder_2, ISAJson_encoder as ISAJson_encoder_2, ISAJson_decoder as ISAJson_decoder_2)
from .protocol import (ROCrate_encoder as ROCrate_encoder_1, ROCrate_decoder as ROCrate_decoder_1, ISAJson_encoder as ISAJson_encoder_1, ISAJson_decoder as ISAJson_decoder_1)

__A_ = TypeVar("__A_")

def ROCrate_genID(p: Process) -> str:
    match_value: str | None = p.ID
    if match_value is None:
        match_value_1: str | None = p.Name
        if match_value_1 is None:
            return "#EmptyProcess"

        else: 
            return "#Process_" + replace(match_value_1, " ", "_")


    else: 
        return URIModule_toString(match_value)



def ROCrate_encoder(study_name: str | None, assay_name: str | None, oa: Process) -> IEncodable:
    def chooser(tupled_arg: tuple[str, IEncodable | None], study_name: Any=study_name, assay_name: Any=assay_name, oa: Any=oa) -> tuple[str, IEncodable] | None:
        def mapping(v_1: IEncodable, tupled_arg: Any=tupled_arg) -> tuple[str, IEncodable]:
            return (tupled_arg[0], v_1)

        return map(mapping, tupled_arg[1])

    def _arrow2178(__unit: None=None, study_name: Any=study_name, assay_name: Any=assay_name, oa: Any=oa) -> IEncodable:
        value: str = ROCrate_genID(oa)
        class ObjectExpr2177(IEncodable):
            def Encode(self, helpers: IEncoderHelpers_1[Any]) -> Any:
                return helpers.encode_string(value)

        return ObjectExpr2177()

    class ObjectExpr2179(IEncodable):
        def Encode(self, helpers_1: IEncoderHelpers_1[Any], study_name: Any=study_name, assay_name: Any=assay_name, oa: Any=oa) -> Any:
            return helpers_1.encode_string("Process")

    def _arrow2181(value_2: str, study_name: Any=study_name, assay_name: Any=assay_name, oa: Any=oa) -> IEncodable:
        class ObjectExpr2180(IEncodable):
            def Encode(self, helpers_2: IEncoderHelpers_1[Any]) -> Any:
                return helpers_2.encode_string(value_2)

        return ObjectExpr2180()

    def _arrow2182(oa_1: Protocol, study_name: Any=study_name, assay_name: Any=assay_name, oa: Any=oa) -> IEncodable:
        return ROCrate_encoder_1(study_name, assay_name, oa.Name, oa_1)

    def _arrow2183(author_list: str, study_name: Any=study_name, assay_name: Any=assay_name, oa: Any=oa) -> IEncodable:
        return ROCrate_encodeAuthorListString(author_list)

    def _arrow2185(value_4: str, study_name: Any=study_name, assay_name: Any=assay_name, oa: Any=oa) -> IEncodable:
        class ObjectExpr2184(IEncodable):
            def Encode(self, helpers_3: IEncoderHelpers_1[Any]) -> Any:
                return helpers_3.encode_string(value_4)

        return ObjectExpr2184()

    def _arrow2186(value_6: ProcessInput, study_name: Any=study_name, assay_name: Any=assay_name, oa: Any=oa) -> IEncodable:
        return ROCrate_encoder_3(value_6)

    def _arrow2187(value_7: ProcessOutput, study_name: Any=study_name, assay_name: Any=assay_name, oa: Any=oa) -> IEncodable:
        return ROCrate_encoder_4(value_7)

    def _arrow2188(comment: Comment, study_name: Any=study_name, assay_name: Any=assay_name, oa: Any=oa) -> IEncodable:
        return ROCrate_encoder_5(comment)

    values: FSharpList[tuple[str, IEncodable]] = choose(chooser, of_array([("@id", _arrow2178()), ("@type", list_1_1(singleton(ObjectExpr2179()))), try_include("name", _arrow2181, oa.Name), try_include("executesProtocol", _arrow2182, oa.ExecutesProtocol), try_include_list_opt("parameterValues", ROCrate_encoder_2, oa.ParameterValues), try_include("performer", _arrow2183, oa.Performer), try_include("date", _arrow2185, oa.Date), try_include_list_opt("inputs", _arrow2186, oa.Inputs), try_include_list_opt("outputs", _arrow2187, oa.Outputs), try_include_list_opt("comments", _arrow2188, oa.Comments), ("@context", context_jsonvalue)]))
    class ObjectExpr2189(IEncodable):
        def Encode(self, helpers_4: IEncoderHelpers_1[Any], study_name: Any=study_name, assay_name: Any=assay_name, oa: Any=oa) -> Any:
            def mapping_1(tupled_arg_1: tuple[str, IEncodable]) -> tuple[str, __A_]:
                return (tupled_arg_1[0], tupled_arg_1[1].Encode(helpers_4))

            arg: IEnumerable_1[tuple[str, __A_]] = map_1(mapping_1, values)
            return helpers_4.encode_object(arg)

    return ObjectExpr2189()


def _arrow2199(get: IGetters) -> Process:
    def _arrow2190(__unit: None=None) -> str | None:
        object_arg: IOptionalGetter = get.Optional
        return object_arg.Field("@id", Decode_uri)

    def _arrow2191(__unit: None=None) -> str | None:
        object_arg_1: IOptionalGetter = get.Optional
        return object_arg_1.Field("name", string)

    def _arrow2192(__unit: None=None) -> Protocol | None:
        object_arg_2: IOptionalGetter = get.Optional
        return object_arg_2.Field("executesProtocol", ROCrate_decoder_1)

    def _arrow2193(__unit: None=None) -> FSharpList[ProcessParameterValue] | None:
        arg_7: Decoder_1[FSharpList[ProcessParameterValue]] = list_1_2(ROCrate_decoder_2)
        object_arg_3: IOptionalGetter = get.Optional
        return object_arg_3.Field("parameterValues", arg_7)

    def _arrow2194(__unit: None=None) -> str | None:
        object_arg_4: IOptionalGetter = get.Optional
        return object_arg_4.Field("performer", ROCrate_decodeAuthorListString)

    def _arrow2195(__unit: None=None) -> str | None:
        object_arg_5: IOptionalGetter = get.Optional
        return object_arg_5.Field("date", string)

    def _arrow2196(__unit: None=None) -> FSharpList[ProcessInput] | None:
        arg_13: Decoder_1[FSharpList[ProcessInput]] = list_1_2(ROCrate_decoder_3)
        object_arg_6: IOptionalGetter = get.Optional
        return object_arg_6.Field("inputs", arg_13)

    def _arrow2197(__unit: None=None) -> FSharpList[ProcessOutput] | None:
        arg_15: Decoder_1[FSharpList[ProcessOutput]] = list_1_2(ROCrate_decoder_4)
        object_arg_7: IOptionalGetter = get.Optional
        return object_arg_7.Field("outputs", arg_15)

    def _arrow2198(__unit: None=None) -> FSharpList[Comment] | None:
        arg_17: Decoder_1[FSharpList[Comment]] = list_1_2(ROCrate_decoder_5)
        object_arg_8: IOptionalGetter = get.Optional
        return object_arg_8.Field("comments", arg_17)

    return Process(_arrow2190(), _arrow2191(), _arrow2192(), _arrow2193(), _arrow2194(), _arrow2195(), None, None, _arrow2196(), _arrow2197(), _arrow2198())


ROCrate_decoder: Decoder_1[Process] = object(_arrow2199)

def ISAJson_encoder(study_name: str | None, assay_name: str | None, id_map: Any | None, oa: Process) -> IEncodable:
    def f(oa_1: Process, study_name: Any=study_name, assay_name: Any=assay_name, id_map: Any=id_map, oa: Any=oa) -> IEncodable:
        def chooser(tupled_arg: tuple[str, IEncodable | None], oa_1: Any=oa_1) -> tuple[str, IEncodable] | None:
            def mapping(v_1: IEncodable, tupled_arg: Any=tupled_arg) -> tuple[str, IEncodable]:
                return (tupled_arg[0], v_1)

            return map(mapping, tupled_arg[1])

        def _arrow2203(value: str, oa_1: Any=oa_1) -> IEncodable:
            class ObjectExpr2202(IEncodable):
                def Encode(self, helpers: IEncoderHelpers_1[Any]) -> Any:
                    return helpers.encode_string(value)

            return ObjectExpr2202()

        def _arrow2205(value_2: str, oa_1: Any=oa_1) -> IEncodable:
            class ObjectExpr2204(IEncodable):
                def Encode(self, helpers_1: IEncoderHelpers_1[Any]) -> Any:
                    return helpers_1.encode_string(value_2)

            return ObjectExpr2204()

        def _arrow2206(oa_2: Protocol, oa_1: Any=oa_1) -> IEncodable:
            return ISAJson_encoder_1(study_name, assay_name, oa_1.Name, id_map, oa_2)

        def _arrow2207(oa_3: ProcessParameterValue, oa_1: Any=oa_1) -> IEncodable:
            return ISAJson_encoder_2(id_map, oa_3)

        def _arrow2209(value_4: str, oa_1: Any=oa_1) -> IEncodable:
            class ObjectExpr2208(IEncodable):
                def Encode(self, helpers_2: IEncoderHelpers_1[Any]) -> Any:
                    return helpers_2.encode_string(value_4)

            return ObjectExpr2208()

        def _arrow2211(value_6: str, oa_1: Any=oa_1) -> IEncodable:
            class ObjectExpr2210(IEncodable):
                def Encode(self, helpers_3: IEncoderHelpers_1[Any]) -> Any:
                    return helpers_3.encode_string(value_6)

            return ObjectExpr2210()

        def _arrow2212(oa_4: Process, oa_1: Any=oa_1) -> IEncodable:
            return ISAJson_encoder(study_name, assay_name, id_map, oa_4)

        def _arrow2213(oa_5: Process, oa_1: Any=oa_1) -> IEncodable:
            return ISAJson_encoder(study_name, assay_name, id_map, oa_5)

        def _arrow2214(value_8: ProcessInput, oa_1: Any=oa_1) -> IEncodable:
            return ISAJson_encoder_3(id_map, value_8)

        def _arrow2215(value_9: ProcessOutput, oa_1: Any=oa_1) -> IEncodable:
            return ISAJson_encoder_4(id_map, value_9)

        def _arrow2216(comment: Comment, oa_1: Any=oa_1) -> IEncodable:
            return ISAJson_encoder_5(id_map, comment)

        values: FSharpList[tuple[str, IEncodable]] = choose(chooser, of_array([try_include("@id", _arrow2203, ROCrate_genID(oa_1)), try_include("name", _arrow2205, oa_1.Name), try_include("executesProtocol", _arrow2206, oa_1.ExecutesProtocol), try_include_list_opt("parameterValues", _arrow2207, oa_1.ParameterValues), try_include("performer", _arrow2209, oa_1.Performer), try_include("date", _arrow2211, oa_1.Date), try_include("previousProcess", _arrow2212, oa_1.PreviousProcess), try_include("nextProcess", _arrow2213, oa_1.NextProcess), try_include_list_opt("inputs", _arrow2214, oa_1.Inputs), try_include_list_opt("outputs", _arrow2215, oa_1.Outputs), try_include_list_opt("comments", _arrow2216, oa_1.Comments)]))
        class ObjectExpr2217(IEncodable):
            def Encode(self, helpers_4: IEncoderHelpers_1[Any], oa_1: Any=oa_1) -> Any:
                def mapping_1(tupled_arg_1: tuple[str, IEncodable]) -> tuple[str, __A_]:
                    return (tupled_arg_1[0], tupled_arg_1[1].Encode(helpers_4))

                arg: IEnumerable_1[tuple[str, __A_]] = map_1(mapping_1, values)
                return helpers_4.encode_object(arg)

        return ObjectExpr2217()

    if id_map is not None:
        def _arrow2218(p: Process, study_name: Any=study_name, assay_name: Any=assay_name, id_map: Any=id_map, oa: Any=oa) -> str:
            return ROCrate_genID(p)

        return encode(_arrow2218, f, oa, id_map)

    else: 
        return f(oa)



def _arrow2233(__unit: None=None) -> Decoder_1[Process]:
    def decode(__unit: None=None) -> Decoder_1[Process]:
        def _arrow2232(get: IGetters) -> Process:
            def _arrow2219(__unit: None=None) -> str | None:
                object_arg: IOptionalGetter = get.Optional
                return object_arg.Field("@id", Decode_uri)

            def _arrow2220(__unit: None=None) -> str | None:
                object_arg_1: IOptionalGetter = get.Optional
                return object_arg_1.Field("name", string)

            def _arrow2221(__unit: None=None) -> Protocol | None:
                object_arg_2: IOptionalGetter = get.Optional
                return object_arg_2.Field("executesProtocol", ISAJson_decoder_1)

            def _arrow2222(__unit: None=None) -> FSharpList[ProcessParameterValue] | None:
                arg_7: Decoder_1[FSharpList[ProcessParameterValue]] = list_1_2(ISAJson_decoder_2)
                object_arg_3: IOptionalGetter = get.Optional
                return object_arg_3.Field("parameterValues", arg_7)

            def _arrow2224(__unit: None=None) -> str | None:
                object_arg_4: IOptionalGetter = get.Optional
                return object_arg_4.Field("performer", string)

            def _arrow2225(__unit: None=None) -> str | None:
                object_arg_5: IOptionalGetter = get.Optional
                return object_arg_5.Field("date", string)

            def _arrow2226(__unit: None=None) -> Process | None:
                arg_13: Decoder_1[Process] = decode(None)
                object_arg_6: IOptionalGetter = get.Optional
                return object_arg_6.Field("previousProcess", arg_13)

            def _arrow2227(__unit: None=None) -> Process | None:
                arg_15: Decoder_1[Process] = decode(None)
                object_arg_7: IOptionalGetter = get.Optional
                return object_arg_7.Field("nextProcess", arg_15)

            def _arrow2228(__unit: None=None) -> FSharpList[ProcessInput] | None:
                arg_17: Decoder_1[FSharpList[ProcessInput]] = list_1_2(ISAJson_decoder_3)
                object_arg_8: IOptionalGetter = get.Optional
                return object_arg_8.Field("inputs", arg_17)

            def _arrow2230(__unit: None=None) -> FSharpList[ProcessOutput] | None:
                arg_19: Decoder_1[FSharpList[ProcessOutput]] = list_1_2(ISAJson_decoder_4)
                object_arg_9: IOptionalGetter = get.Optional
                return object_arg_9.Field("outputs", arg_19)

            def _arrow2231(__unit: None=None) -> FSharpList[Comment] | None:
                arg_21: Decoder_1[FSharpList[Comment]] = list_1_2(ISAJson_decoder_5)
                object_arg_10: IOptionalGetter = get.Optional
                return object_arg_10.Field("comments", arg_21)

            return Process(_arrow2219(), _arrow2220(), _arrow2221(), _arrow2222(), _arrow2224(), _arrow2225(), _arrow2226(), _arrow2227(), _arrow2228(), _arrow2230(), _arrow2231())

        return object(_arrow2232)

    return decode(None)


ISAJson_decoder: Decoder_1[Process] = _arrow2233()

__all__ = ["ROCrate_genID", "ROCrate_encoder", "ROCrate_decoder", "ISAJson_encoder", "ISAJson_decoder"]

