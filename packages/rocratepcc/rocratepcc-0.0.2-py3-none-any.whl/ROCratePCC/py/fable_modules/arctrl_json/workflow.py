from __future__ import annotations
from typing import (Any, TypeVar)
from ..arctrl_core.arc_types import ArcWorkflow
from ..arctrl_core.comment import Comment
from ..arctrl_core.data_map import DataMap
from ..arctrl_core.ontology_annotation import OntologyAnnotation
from ..arctrl_core.person import Person
from ..arctrl_core.Process.component import Component
from ..arctrl_core.Process.protocol_parameter import ProtocolParameter
from ..arctrl_core.Table.composite_cell import CompositeCell
from ..fable_library.list import (choose, of_array, FSharpList)
from ..fable_library.option import map
from ..fable_library.seq import map as map_1
from ..fable_library.types import Array
from ..fable_library.util import IEnumerable_1
from ..thoth_json_core.decode import (object, IRequiredGetter, string, IOptionalGetter, resize_array, IGetters)
from ..thoth_json_core.types import (IEncodable, IEncoderHelpers_1, Decoder_1)
from .comment import (encoder as encoder_5, decoder as decoder_5)
from .DataMap.data_map import (encoder as encoder_1, decoder as decoder_3, encoder_compressed as encoder_compressed_1, decoder_compressed as decoder_compressed_1)
from .encode import (try_include, try_include_seq)
from .ontology_annotation import (OntologyAnnotation_encoder, OntologyAnnotation_decoder)
from .person import (encoder as encoder_4, decoder as decoder_4)
from .Process.component import (encoder as encoder_3, decoder as decoder_2)
from .Process.protocol_parameter import (encoder as encoder_2, decoder as decoder_1)

__A_ = TypeVar("__A_")

def encoder(workflow: ArcWorkflow) -> IEncodable:
    def chooser(tupled_arg: tuple[str, IEncodable | None], workflow: Any=workflow) -> tuple[str, IEncodable] | None:
        def mapping(v_1: IEncodable, tupled_arg: Any=tupled_arg) -> tuple[str, IEncodable]:
            return (tupled_arg[0], v_1)

        return map(mapping, tupled_arg[1])

    def _arrow2489(__unit: None=None, workflow: Any=workflow) -> IEncodable:
        value: str = workflow.Identifier
        class ObjectExpr2488(IEncodable):
            def Encode(self, helpers: IEncoderHelpers_1[Any]) -> Any:
                return helpers.encode_string(value)

        return ObjectExpr2488()

    def _arrow2490(oa: OntologyAnnotation, workflow: Any=workflow) -> IEncodable:
        return OntologyAnnotation_encoder(oa)

    def _arrow2492(value_1: str, workflow: Any=workflow) -> IEncodable:
        class ObjectExpr2491(IEncodable):
            def Encode(self, helpers_1: IEncoderHelpers_1[Any]) -> Any:
                return helpers_1.encode_string(value_1)

        return ObjectExpr2491()

    def _arrow2494(value_3: str, workflow: Any=workflow) -> IEncodable:
        class ObjectExpr2493(IEncodable):
            def Encode(self, helpers_2: IEncoderHelpers_1[Any]) -> Any:
                return helpers_2.encode_string(value_3)

        return ObjectExpr2493()

    def _arrow2496(value_5: str, workflow: Any=workflow) -> IEncodable:
        class ObjectExpr2495(IEncodable):
            def Encode(self, helpers_3: IEncoderHelpers_1[Any]) -> Any:
                return helpers_3.encode_string(value_5)

        return ObjectExpr2495()

    def _arrow2498(value_7: str, workflow: Any=workflow) -> IEncodable:
        class ObjectExpr2497(IEncodable):
            def Encode(self, helpers_4: IEncoderHelpers_1[Any]) -> Any:
                return helpers_4.encode_string(value_7)

        return ObjectExpr2497()

    def _arrow2499(dm: DataMap, workflow: Any=workflow) -> IEncodable:
        return encoder_1(dm)

    def _arrow2501(value_9: str, workflow: Any=workflow) -> IEncodable:
        class ObjectExpr2500(IEncodable):
            def Encode(self, helpers_5: IEncoderHelpers_1[Any]) -> Any:
                return helpers_5.encode_string(value_9)

        return ObjectExpr2500()

    def _arrow2502(value_11: ProtocolParameter, workflow: Any=workflow) -> IEncodable:
        return encoder_2(value_11)

    def _arrow2503(value_12: Component, workflow: Any=workflow) -> IEncodable:
        return encoder_3(value_12)

    def _arrow2504(person: Person, workflow: Any=workflow) -> IEncodable:
        return encoder_4(person)

    def _arrow2505(comment: Comment, workflow: Any=workflow) -> IEncodable:
        return encoder_5(comment)

    values: FSharpList[tuple[str, IEncodable]] = choose(chooser, of_array([("Identifier", _arrow2489()), try_include("WorkflowType", _arrow2490, workflow.WorkflowType), try_include("Title", _arrow2492, workflow.Title), try_include("URI", _arrow2494, workflow.URI), try_include("Description", _arrow2496, workflow.Description), try_include("Version", _arrow2498, workflow.Version), try_include("DataMap", _arrow2499, workflow.DataMap), try_include_seq("SubWorkflowIdentifiers", _arrow2501, workflow.SubWorkflowIdentifiers), try_include_seq("Parameters", _arrow2502, workflow.Parameters), try_include_seq("Components", _arrow2503, workflow.Components), try_include_seq("Contacts", _arrow2504, workflow.Contacts), try_include_seq("Comments", _arrow2505, workflow.Comments)]))
    class ObjectExpr2506(IEncodable):
        def Encode(self, helpers_6: IEncoderHelpers_1[Any], workflow: Any=workflow) -> Any:
            def mapping_1(tupled_arg_1: tuple[str, IEncodable]) -> tuple[str, __A_]:
                return (tupled_arg_1[0], tupled_arg_1[1].Encode(helpers_6))

            arg: IEnumerable_1[tuple[str, __A_]] = map_1(mapping_1, values)
            return helpers_6.encode_object(arg)

    return ObjectExpr2506()


def _arrow2519(get: IGetters) -> ArcWorkflow:
    def _arrow2507(__unit: None=None) -> str:
        object_arg: IRequiredGetter = get.Required
        return object_arg.Field("Identifier", string)

    def _arrow2508(__unit: None=None) -> str | None:
        object_arg_1: IOptionalGetter = get.Optional
        return object_arg_1.Field("Title", string)

    def _arrow2509(__unit: None=None) -> str | None:
        object_arg_2: IOptionalGetter = get.Optional
        return object_arg_2.Field("Description", string)

    def _arrow2510(__unit: None=None) -> OntologyAnnotation | None:
        object_arg_3: IOptionalGetter = get.Optional
        return object_arg_3.Field("WorkflowType", OntologyAnnotation_decoder)

    def _arrow2511(__unit: None=None) -> str | None:
        object_arg_4: IOptionalGetter = get.Optional
        return object_arg_4.Field("URI", string)

    def _arrow2512(__unit: None=None) -> str | None:
        object_arg_5: IOptionalGetter = get.Optional
        return object_arg_5.Field("Version", string)

    def _arrow2513(__unit: None=None) -> Array[str] | None:
        arg_13: Decoder_1[Array[str]] = resize_array(string)
        object_arg_6: IOptionalGetter = get.Optional
        return object_arg_6.Field("SubWorkflowIdentifiers", arg_13)

    def _arrow2514(__unit: None=None) -> Array[ProtocolParameter] | None:
        arg_15: Decoder_1[Array[ProtocolParameter]] = resize_array(decoder_1)
        object_arg_7: IOptionalGetter = get.Optional
        return object_arg_7.Field("Parameters", arg_15)

    def _arrow2515(__unit: None=None) -> Array[Component] | None:
        arg_17: Decoder_1[Array[Component]] = resize_array(decoder_2)
        object_arg_8: IOptionalGetter = get.Optional
        return object_arg_8.Field("Components", arg_17)

    def _arrow2516(__unit: None=None) -> DataMap | None:
        object_arg_9: IOptionalGetter = get.Optional
        return object_arg_9.Field("DataMap", decoder_3)

    def _arrow2517(__unit: None=None) -> Array[Person] | None:
        arg_21: Decoder_1[Array[Person]] = resize_array(decoder_4)
        object_arg_10: IOptionalGetter = get.Optional
        return object_arg_10.Field("Contacts", arg_21)

    def _arrow2518(__unit: None=None) -> Array[Comment] | None:
        arg_23: Decoder_1[Array[Comment]] = resize_array(decoder_5)
        object_arg_11: IOptionalGetter = get.Optional
        return object_arg_11.Field("Comments", arg_23)

    return ArcWorkflow.create(_arrow2507(), _arrow2508(), _arrow2509(), _arrow2510(), _arrow2511(), _arrow2512(), _arrow2513(), _arrow2514(), _arrow2515(), _arrow2516(), _arrow2517(), _arrow2518())


decoder: Decoder_1[ArcWorkflow] = object(_arrow2519)

def encoder_compressed(string_table: Any, oa_table: Any, cell_table: Any, workflow: ArcWorkflow) -> IEncodable:
    def chooser(tupled_arg: tuple[str, IEncodable | None], string_table: Any=string_table, oa_table: Any=oa_table, cell_table: Any=cell_table, workflow: Any=workflow) -> tuple[str, IEncodable] | None:
        def mapping(v_1: IEncodable, tupled_arg: Any=tupled_arg) -> tuple[str, IEncodable]:
            return (tupled_arg[0], v_1)

        return map(mapping, tupled_arg[1])

    def _arrow2523(__unit: None=None, string_table: Any=string_table, oa_table: Any=oa_table, cell_table: Any=cell_table, workflow: Any=workflow) -> IEncodable:
        value: str = workflow.Identifier
        class ObjectExpr2522(IEncodable):
            def Encode(self, helpers: IEncoderHelpers_1[Any]) -> Any:
                return helpers.encode_string(value)

        return ObjectExpr2522()

    def _arrow2524(oa: OntologyAnnotation, string_table: Any=string_table, oa_table: Any=oa_table, cell_table: Any=cell_table, workflow: Any=workflow) -> IEncodable:
        return OntologyAnnotation_encoder(oa)

    def _arrow2526(value_1: str, string_table: Any=string_table, oa_table: Any=oa_table, cell_table: Any=cell_table, workflow: Any=workflow) -> IEncodable:
        class ObjectExpr2525(IEncodable):
            def Encode(self, helpers_1: IEncoderHelpers_1[Any]) -> Any:
                return helpers_1.encode_string(value_1)

        return ObjectExpr2525()

    def _arrow2528(value_3: str, string_table: Any=string_table, oa_table: Any=oa_table, cell_table: Any=cell_table, workflow: Any=workflow) -> IEncodable:
        class ObjectExpr2527(IEncodable):
            def Encode(self, helpers_2: IEncoderHelpers_1[Any]) -> Any:
                return helpers_2.encode_string(value_3)

        return ObjectExpr2527()

    def _arrow2530(value_5: str, string_table: Any=string_table, oa_table: Any=oa_table, cell_table: Any=cell_table, workflow: Any=workflow) -> IEncodable:
        class ObjectExpr2529(IEncodable):
            def Encode(self, helpers_3: IEncoderHelpers_1[Any]) -> Any:
                return helpers_3.encode_string(value_5)

        return ObjectExpr2529()

    def _arrow2532(value_7: str, string_table: Any=string_table, oa_table: Any=oa_table, cell_table: Any=cell_table, workflow: Any=workflow) -> IEncodable:
        class ObjectExpr2531(IEncodable):
            def Encode(self, helpers_4: IEncoderHelpers_1[Any]) -> Any:
                return helpers_4.encode_string(value_7)

        return ObjectExpr2531()

    def _arrow2533(dm: DataMap, string_table: Any=string_table, oa_table: Any=oa_table, cell_table: Any=cell_table, workflow: Any=workflow) -> IEncodable:
        return encoder_compressed_1(string_table, oa_table, cell_table, dm)

    def _arrow2535(value_9: str, string_table: Any=string_table, oa_table: Any=oa_table, cell_table: Any=cell_table, workflow: Any=workflow) -> IEncodable:
        class ObjectExpr2534(IEncodable):
            def Encode(self, helpers_5: IEncoderHelpers_1[Any]) -> Any:
                return helpers_5.encode_string(value_9)

        return ObjectExpr2534()

    def _arrow2536(value_11: ProtocolParameter, string_table: Any=string_table, oa_table: Any=oa_table, cell_table: Any=cell_table, workflow: Any=workflow) -> IEncodable:
        return encoder_2(value_11)

    def _arrow2537(value_12: Component, string_table: Any=string_table, oa_table: Any=oa_table, cell_table: Any=cell_table, workflow: Any=workflow) -> IEncodable:
        return encoder_3(value_12)

    def _arrow2538(person: Person, string_table: Any=string_table, oa_table: Any=oa_table, cell_table: Any=cell_table, workflow: Any=workflow) -> IEncodable:
        return encoder_4(person)

    def _arrow2539(comment: Comment, string_table: Any=string_table, oa_table: Any=oa_table, cell_table: Any=cell_table, workflow: Any=workflow) -> IEncodable:
        return encoder_5(comment)

    values: FSharpList[tuple[str, IEncodable]] = choose(chooser, of_array([("Identifier", _arrow2523()), try_include("WorkflowType", _arrow2524, workflow.WorkflowType), try_include("Title", _arrow2526, workflow.Title), try_include("URI", _arrow2528, workflow.URI), try_include("Description", _arrow2530, workflow.Description), try_include("Version", _arrow2532, workflow.Version), try_include("DataMap", _arrow2533, workflow.DataMap), try_include_seq("SubWorkflowIdentifiers", _arrow2535, workflow.SubWorkflowIdentifiers), try_include_seq("Parameters", _arrow2536, workflow.Parameters), try_include_seq("Components", _arrow2537, workflow.Components), try_include_seq("Contacts", _arrow2538, workflow.Contacts), try_include_seq("Comments", _arrow2539, workflow.Comments)]))
    class ObjectExpr2540(IEncodable):
        def Encode(self, helpers_6: IEncoderHelpers_1[Any], string_table: Any=string_table, oa_table: Any=oa_table, cell_table: Any=cell_table, workflow: Any=workflow) -> Any:
            def mapping_1(tupled_arg_1: tuple[str, IEncodable]) -> tuple[str, __A_]:
                return (tupled_arg_1[0], tupled_arg_1[1].Encode(helpers_6))

            arg: IEnumerable_1[tuple[str, __A_]] = map_1(mapping_1, values)
            return helpers_6.encode_object(arg)

    return ObjectExpr2540()


def decoder_compressed(string_table: Array[str], oa_table: Array[OntologyAnnotation], cell_table: Array[CompositeCell]) -> Decoder_1[ArcWorkflow]:
    def _arrow2553(get: IGetters, string_table: Any=string_table, oa_table: Any=oa_table, cell_table: Any=cell_table) -> ArcWorkflow:
        def _arrow2541(__unit: None=None) -> str:
            object_arg: IRequiredGetter = get.Required
            return object_arg.Field("Identifier", string)

        def _arrow2542(__unit: None=None) -> str | None:
            object_arg_1: IOptionalGetter = get.Optional
            return object_arg_1.Field("Title", string)

        def _arrow2543(__unit: None=None) -> str | None:
            object_arg_2: IOptionalGetter = get.Optional
            return object_arg_2.Field("Description", string)

        def _arrow2544(__unit: None=None) -> OntologyAnnotation | None:
            object_arg_3: IOptionalGetter = get.Optional
            return object_arg_3.Field("WorkflowType", OntologyAnnotation_decoder)

        def _arrow2545(__unit: None=None) -> str | None:
            object_arg_4: IOptionalGetter = get.Optional
            return object_arg_4.Field("URI", string)

        def _arrow2546(__unit: None=None) -> str | None:
            object_arg_5: IOptionalGetter = get.Optional
            return object_arg_5.Field("Version", string)

        def _arrow2547(__unit: None=None) -> Array[str] | None:
            arg_13: Decoder_1[Array[str]] = resize_array(string)
            object_arg_6: IOptionalGetter = get.Optional
            return object_arg_6.Field("SubWorkflowIdentifiers", arg_13)

        def _arrow2548(__unit: None=None) -> Array[ProtocolParameter] | None:
            arg_15: Decoder_1[Array[ProtocolParameter]] = resize_array(decoder_1)
            object_arg_7: IOptionalGetter = get.Optional
            return object_arg_7.Field("Parameters", arg_15)

        def _arrow2549(__unit: None=None) -> Array[Component] | None:
            arg_17: Decoder_1[Array[Component]] = resize_array(decoder_2)
            object_arg_8: IOptionalGetter = get.Optional
            return object_arg_8.Field("Components", arg_17)

        def _arrow2550(__unit: None=None) -> DataMap | None:
            arg_19: Decoder_1[DataMap] = decoder_compressed_1(string_table, oa_table, cell_table)
            object_arg_9: IOptionalGetter = get.Optional
            return object_arg_9.Field("DataMap", arg_19)

        def _arrow2551(__unit: None=None) -> Array[Person] | None:
            arg_21: Decoder_1[Array[Person]] = resize_array(decoder_4)
            object_arg_10: IOptionalGetter = get.Optional
            return object_arg_10.Field("Contacts", arg_21)

        def _arrow2552(__unit: None=None) -> Array[Comment] | None:
            arg_23: Decoder_1[Array[Comment]] = resize_array(decoder_5)
            object_arg_11: IOptionalGetter = get.Optional
            return object_arg_11.Field("Comments", arg_23)

        return ArcWorkflow.create(_arrow2541(), _arrow2542(), _arrow2543(), _arrow2544(), _arrow2545(), _arrow2546(), _arrow2547(), _arrow2548(), _arrow2549(), _arrow2550(), _arrow2551(), _arrow2552())

    return object(_arrow2553)


__all__ = ["encoder", "decoder", "encoder_compressed", "decoder_compressed"]

