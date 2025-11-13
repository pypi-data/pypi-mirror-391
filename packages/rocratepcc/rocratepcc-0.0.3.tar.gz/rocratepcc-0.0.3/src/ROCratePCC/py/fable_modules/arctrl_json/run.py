from __future__ import annotations
from typing import (Any, TypeVar)
from ..arctrl_core.arc_types import ArcRun
from ..arctrl_core.comment import Comment
from ..arctrl_core.data_map import DataMap
from ..arctrl_core.ontology_annotation import OntologyAnnotation
from ..arctrl_core.person import Person
from ..arctrl_core.Table.arc_table import ArcTable
from ..arctrl_core.Table.composite_cell import CompositeCell
from ..fable_library.list import (choose, of_array, FSharpList)
from ..fable_library.option import map
from ..fable_library.seq import map as map_1
from ..fable_library.types import Array
from ..fable_library.util import IEnumerable_1
from ..thoth_json_core.decode import (object, IRequiredGetter, string, IOptionalGetter, resize_array, IGetters)
from ..thoth_json_core.types import (IEncodable, IEncoderHelpers_1, Decoder_1)
from .comment import (encoder as encoder_4, decoder as decoder_4)
from .DataMap.data_map import (encoder as encoder_1, decoder as decoder_2, encoder_compressed as encoder_compressed_1, decoder_compressed as decoder_compressed_2)
from .encode import (try_include, try_include_seq)
from .ontology_annotation import (OntologyAnnotation_encoder, OntologyAnnotation_decoder)
from .person import (encoder as encoder_3, decoder as decoder_3)
from .Table.arc_table import (encoder as encoder_2, decoder as decoder_1, encoder_compressed as encoder_compressed_2, decoder_compressed as decoder_compressed_1)

__A_ = TypeVar("__A_")

def encoder(run: ArcRun) -> IEncodable:
    def chooser(tupled_arg: tuple[str, IEncodable | None], run: Any=run) -> tuple[str, IEncodable] | None:
        def mapping(v_1: IEncodable, tupled_arg: Any=tupled_arg) -> tuple[str, IEncodable]:
            return (tupled_arg[0], v_1)

        return map(mapping, tupled_arg[1])

    def _arrow2556(__unit: None=None, run: Any=run) -> IEncodable:
        value: str = run.Identifier
        class ObjectExpr2555(IEncodable):
            def Encode(self, helpers: IEncoderHelpers_1[Any]) -> Any:
                return helpers.encode_string(value)

        return ObjectExpr2555()

    def _arrow2558(value_1: str, run: Any=run) -> IEncodable:
        class ObjectExpr2557(IEncodable):
            def Encode(self, helpers_1: IEncoderHelpers_1[Any]) -> Any:
                return helpers_1.encode_string(value_1)

        return ObjectExpr2557()

    def _arrow2560(value_3: str, run: Any=run) -> IEncodable:
        class ObjectExpr2559(IEncodable):
            def Encode(self, helpers_2: IEncoderHelpers_1[Any]) -> Any:
                return helpers_2.encode_string(value_3)

        return ObjectExpr2559()

    def _arrow2561(oa: OntologyAnnotation, run: Any=run) -> IEncodable:
        return OntologyAnnotation_encoder(oa)

    def _arrow2562(oa_1: OntologyAnnotation, run: Any=run) -> IEncodable:
        return OntologyAnnotation_encoder(oa_1)

    def _arrow2563(oa_2: OntologyAnnotation, run: Any=run) -> IEncodable:
        return OntologyAnnotation_encoder(oa_2)

    def _arrow2564(dm: DataMap, run: Any=run) -> IEncodable:
        return encoder_1(dm)

    def _arrow2566(value_5: str, run: Any=run) -> IEncodable:
        class ObjectExpr2565(IEncodable):
            def Encode(self, helpers_3: IEncoderHelpers_1[Any]) -> Any:
                return helpers_3.encode_string(value_5)

        return ObjectExpr2565()

    def _arrow2567(table: ArcTable, run: Any=run) -> IEncodable:
        return encoder_2(table)

    def _arrow2568(person: Person, run: Any=run) -> IEncodable:
        return encoder_3(person)

    def _arrow2569(comment: Comment, run: Any=run) -> IEncodable:
        return encoder_4(comment)

    values: FSharpList[tuple[str, IEncodable]] = choose(chooser, of_array([("Identifier", _arrow2556()), try_include("Title", _arrow2558, run.Title), try_include("Description", _arrow2560, run.Description), try_include("MeasurementType", _arrow2561, run.MeasurementType), try_include("TechnologyType", _arrow2562, run.TechnologyType), try_include("TechnologyPlatform", _arrow2563, run.TechnologyPlatform), try_include("DataMap", _arrow2564, run.DataMap), try_include_seq("WorkflowIdentifiers", _arrow2566, run.WorkflowIdentifiers), try_include_seq("Tables", _arrow2567, run.Tables), try_include_seq("Performers", _arrow2568, run.Performers), try_include_seq("Comments", _arrow2569, run.Comments)]))
    class ObjectExpr2570(IEncodable):
        def Encode(self, helpers_4: IEncoderHelpers_1[Any], run: Any=run) -> Any:
            def mapping_1(tupled_arg_1: tuple[str, IEncodable]) -> tuple[str, __A_]:
                return (tupled_arg_1[0], tupled_arg_1[1].Encode(helpers_4))

            arg: IEnumerable_1[tuple[str, __A_]] = map_1(mapping_1, values)
            return helpers_4.encode_object(arg)

    return ObjectExpr2570()


def _arrow2582(get: IGetters) -> ArcRun:
    def _arrow2571(__unit: None=None) -> str:
        object_arg: IRequiredGetter = get.Required
        return object_arg.Field("Identifier", string)

    def _arrow2572(__unit: None=None) -> str | None:
        object_arg_1: IOptionalGetter = get.Optional
        return object_arg_1.Field("Title", string)

    def _arrow2573(__unit: None=None) -> str | None:
        object_arg_2: IOptionalGetter = get.Optional
        return object_arg_2.Field("Description", string)

    def _arrow2574(__unit: None=None) -> OntologyAnnotation | None:
        object_arg_3: IOptionalGetter = get.Optional
        return object_arg_3.Field("MeasurementType", OntologyAnnotation_decoder)

    def _arrow2575(__unit: None=None) -> OntologyAnnotation | None:
        object_arg_4: IOptionalGetter = get.Optional
        return object_arg_4.Field("TechnologyType", OntologyAnnotation_decoder)

    def _arrow2576(__unit: None=None) -> OntologyAnnotation | None:
        object_arg_5: IOptionalGetter = get.Optional
        return object_arg_5.Field("TechnologyPlatform", OntologyAnnotation_decoder)

    def _arrow2577(__unit: None=None) -> Array[str] | None:
        arg_13: Decoder_1[Array[str]] = resize_array(string)
        object_arg_6: IOptionalGetter = get.Optional
        return object_arg_6.Field("WorkflowIdentifiers", arg_13)

    def _arrow2578(__unit: None=None) -> Array[ArcTable] | None:
        arg_15: Decoder_1[Array[ArcTable]] = resize_array(decoder_1)
        object_arg_7: IOptionalGetter = get.Optional
        return object_arg_7.Field("Tables", arg_15)

    def _arrow2579(__unit: None=None) -> DataMap | None:
        object_arg_8: IOptionalGetter = get.Optional
        return object_arg_8.Field("DataMap", decoder_2)

    def _arrow2580(__unit: None=None) -> Array[Person] | None:
        arg_19: Decoder_1[Array[Person]] = resize_array(decoder_3)
        object_arg_9: IOptionalGetter = get.Optional
        return object_arg_9.Field("Performers", arg_19)

    def _arrow2581(__unit: None=None) -> Array[Comment] | None:
        arg_21: Decoder_1[Array[Comment]] = resize_array(decoder_4)
        object_arg_10: IOptionalGetter = get.Optional
        return object_arg_10.Field("Comments", arg_21)

    return ArcRun.create(_arrow2571(), _arrow2572(), _arrow2573(), _arrow2574(), _arrow2575(), _arrow2576(), _arrow2577(), _arrow2578(), _arrow2579(), _arrow2580(), _arrow2581())


decoder: Decoder_1[ArcRun] = object(_arrow2582)

def encoder_compressed(string_table: Any, oa_table: Any, cell_table: Any, run: ArcRun) -> IEncodable:
    def chooser(tupled_arg: tuple[str, IEncodable | None], string_table: Any=string_table, oa_table: Any=oa_table, cell_table: Any=cell_table, run: Any=run) -> tuple[str, IEncodable] | None:
        def mapping(v_1: IEncodable, tupled_arg: Any=tupled_arg) -> tuple[str, IEncodable]:
            return (tupled_arg[0], v_1)

        return map(mapping, tupled_arg[1])

    def _arrow2586(__unit: None=None, string_table: Any=string_table, oa_table: Any=oa_table, cell_table: Any=cell_table, run: Any=run) -> IEncodable:
        value: str = run.Identifier
        class ObjectExpr2585(IEncodable):
            def Encode(self, helpers: IEncoderHelpers_1[Any]) -> Any:
                return helpers.encode_string(value)

        return ObjectExpr2585()

    def _arrow2588(value_1: str, string_table: Any=string_table, oa_table: Any=oa_table, cell_table: Any=cell_table, run: Any=run) -> IEncodable:
        class ObjectExpr2587(IEncodable):
            def Encode(self, helpers_1: IEncoderHelpers_1[Any]) -> Any:
                return helpers_1.encode_string(value_1)

        return ObjectExpr2587()

    def _arrow2590(value_3: str, string_table: Any=string_table, oa_table: Any=oa_table, cell_table: Any=cell_table, run: Any=run) -> IEncodable:
        class ObjectExpr2589(IEncodable):
            def Encode(self, helpers_2: IEncoderHelpers_1[Any]) -> Any:
                return helpers_2.encode_string(value_3)

        return ObjectExpr2589()

    def _arrow2591(oa: OntologyAnnotation, string_table: Any=string_table, oa_table: Any=oa_table, cell_table: Any=cell_table, run: Any=run) -> IEncodable:
        return OntologyAnnotation_encoder(oa)

    def _arrow2592(oa_1: OntologyAnnotation, string_table: Any=string_table, oa_table: Any=oa_table, cell_table: Any=cell_table, run: Any=run) -> IEncodable:
        return OntologyAnnotation_encoder(oa_1)

    def _arrow2593(oa_2: OntologyAnnotation, string_table: Any=string_table, oa_table: Any=oa_table, cell_table: Any=cell_table, run: Any=run) -> IEncodable:
        return OntologyAnnotation_encoder(oa_2)

    def _arrow2594(dm: DataMap, string_table: Any=string_table, oa_table: Any=oa_table, cell_table: Any=cell_table, run: Any=run) -> IEncodable:
        return encoder_compressed_1(string_table, oa_table, cell_table, dm)

    def _arrow2596(value_5: str, string_table: Any=string_table, oa_table: Any=oa_table, cell_table: Any=cell_table, run: Any=run) -> IEncodable:
        class ObjectExpr2595(IEncodable):
            def Encode(self, helpers_3: IEncoderHelpers_1[Any]) -> Any:
                return helpers_3.encode_string(value_5)

        return ObjectExpr2595()

    def _arrow2597(table: ArcTable, string_table: Any=string_table, oa_table: Any=oa_table, cell_table: Any=cell_table, run: Any=run) -> IEncodable:
        return encoder_compressed_2(string_table, oa_table, cell_table, table)

    def _arrow2598(person: Person, string_table: Any=string_table, oa_table: Any=oa_table, cell_table: Any=cell_table, run: Any=run) -> IEncodable:
        return encoder_3(person)

    def _arrow2599(comment: Comment, string_table: Any=string_table, oa_table: Any=oa_table, cell_table: Any=cell_table, run: Any=run) -> IEncodable:
        return encoder_4(comment)

    values: FSharpList[tuple[str, IEncodable]] = choose(chooser, of_array([("Identifier", _arrow2586()), try_include("Title", _arrow2588, run.Title), try_include("Description", _arrow2590, run.Description), try_include("MeasurementType", _arrow2591, run.MeasurementType), try_include("TechnologyType", _arrow2592, run.TechnologyType), try_include("TechnologyPlatform", _arrow2593, run.TechnologyPlatform), try_include("DataMap", _arrow2594, run.DataMap), try_include_seq("WorkflowIdentifiers", _arrow2596, run.WorkflowIdentifiers), try_include_seq("Tables", _arrow2597, run.Tables), try_include_seq("Performers", _arrow2598, run.Performers), try_include_seq("Comments", _arrow2599, run.Comments)]))
    class ObjectExpr2600(IEncodable):
        def Encode(self, helpers_4: IEncoderHelpers_1[Any], string_table: Any=string_table, oa_table: Any=oa_table, cell_table: Any=cell_table, run: Any=run) -> Any:
            def mapping_1(tupled_arg_1: tuple[str, IEncodable]) -> tuple[str, __A_]:
                return (tupled_arg_1[0], tupled_arg_1[1].Encode(helpers_4))

            arg: IEnumerable_1[tuple[str, __A_]] = map_1(mapping_1, values)
            return helpers_4.encode_object(arg)

    return ObjectExpr2600()


def decoder_compressed(string_table: Array[str], oa_table: Array[OntologyAnnotation], cell_table: Array[CompositeCell]) -> Decoder_1[ArcRun]:
    def _arrow2612(get: IGetters, string_table: Any=string_table, oa_table: Any=oa_table, cell_table: Any=cell_table) -> ArcRun:
        def _arrow2601(__unit: None=None) -> str:
            object_arg: IRequiredGetter = get.Required
            return object_arg.Field("Identifier", string)

        def _arrow2602(__unit: None=None) -> str | None:
            object_arg_1: IOptionalGetter = get.Optional
            return object_arg_1.Field("Title", string)

        def _arrow2603(__unit: None=None) -> str | None:
            object_arg_2: IOptionalGetter = get.Optional
            return object_arg_2.Field("Description", string)

        def _arrow2604(__unit: None=None) -> OntologyAnnotation | None:
            object_arg_3: IOptionalGetter = get.Optional
            return object_arg_3.Field("MeasurementType", OntologyAnnotation_decoder)

        def _arrow2605(__unit: None=None) -> OntologyAnnotation | None:
            object_arg_4: IOptionalGetter = get.Optional
            return object_arg_4.Field("TechnologyType", OntologyAnnotation_decoder)

        def _arrow2606(__unit: None=None) -> OntologyAnnotation | None:
            object_arg_5: IOptionalGetter = get.Optional
            return object_arg_5.Field("TechnologyPlatform", OntologyAnnotation_decoder)

        def _arrow2607(__unit: None=None) -> Array[str] | None:
            arg_13: Decoder_1[Array[str]] = resize_array(string)
            object_arg_6: IOptionalGetter = get.Optional
            return object_arg_6.Field("WorkflowIdentifiers", arg_13)

        def _arrow2608(__unit: None=None) -> Array[ArcTable] | None:
            arg_15: Decoder_1[Array[ArcTable]] = resize_array(decoder_compressed_1(string_table, oa_table, cell_table))
            object_arg_7: IOptionalGetter = get.Optional
            return object_arg_7.Field("Tables", arg_15)

        def _arrow2609(__unit: None=None) -> DataMap | None:
            arg_17: Decoder_1[DataMap] = decoder_compressed_2(string_table, oa_table, cell_table)
            object_arg_8: IOptionalGetter = get.Optional
            return object_arg_8.Field("DataMap", arg_17)

        def _arrow2610(__unit: None=None) -> Array[Person] | None:
            arg_19: Decoder_1[Array[Person]] = resize_array(decoder_3)
            object_arg_9: IOptionalGetter = get.Optional
            return object_arg_9.Field("Performers", arg_19)

        def _arrow2611(__unit: None=None) -> Array[Comment] | None:
            arg_21: Decoder_1[Array[Comment]] = resize_array(decoder_4)
            object_arg_10: IOptionalGetter = get.Optional
            return object_arg_10.Field("Comments", arg_21)

        return ArcRun.create(_arrow2601(), _arrow2602(), _arrow2603(), _arrow2604(), _arrow2605(), _arrow2606(), _arrow2607(), _arrow2608(), _arrow2609(), _arrow2610(), _arrow2611())

    return object(_arrow2612)


__all__ = ["encoder", "decoder", "encoder_compressed", "decoder_compressed"]

