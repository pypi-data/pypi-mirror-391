from __future__ import annotations
from collections.abc import Callable
from typing import (Any, TypeVar)
from ..arctrl_core.arc_types import (ArcAssay, ArcStudy)
from ..arctrl_core.comment import Comment
from ..arctrl_core.conversion import (ARCtrl_ArcTables__ArcTables_GetProcesses, ARCtrl_ArcTables__ArcTables_fromProcesses_Static_62A3309D, Person_setSourceAssayComment, Person_getSourceAssayIdentifiersFromComments, Person_removeSourceAssayComments)
from ..arctrl_core.data import Data
from ..arctrl_core.data_map import DataMap
from ..arctrl_core.Helper.collections_ import (ResizeArray_map, Option_fromValueWithDefault)
from ..arctrl_core.Helper.identifier import (Study_tryFileNameFromIdentifier, Study_tryIdentifierFromFileName, create_missing_identifier, Study_fileNameFromIdentifier)
from ..arctrl_core.ontology_annotation import OntologyAnnotation
from ..arctrl_core.person import Person
from ..arctrl_core.Process.factor import Factor
from ..arctrl_core.Process.material_attribute import MaterialAttribute
from ..arctrl_core.Process.process import Process
from ..arctrl_core.Process.process_sequence import (get_data, get_units, get_factors, get_characteristics, get_protocols)
from ..arctrl_core.Process.protocol import Protocol
from ..arctrl_core.publication import Publication
from ..arctrl_core.Table.arc_table import ArcTable
from ..arctrl_core.Table.arc_tables import ArcTables
from ..arctrl_core.Table.composite_cell import CompositeCell
from ..fable_library.list import (try_find, FSharpList, choose, of_array, singleton, map as map_2, empty)
from ..fable_library.option import (default_arg, value as value_17, map, bind, default_arg_with)
from ..fable_library.seq import (map as map_1, is_empty)
from ..fable_library.string_ import replace
from ..fable_library.types import Array
from ..fable_library.util import (IEnumerable_1, get_enumerator, dispose)
from ..thoth_json_core.decode import (object, IRequiredGetter, string, IOptionalGetter, resize_array, IGetters, list_1 as list_1_2)
from ..thoth_json_core.encode import list_1 as list_1_1
from ..thoth_json_core.types import (IEncodable, IEncoderHelpers_1, Decoder_1)
from .assay import (ROCrate_encoder as ROCrate_encoder_4, ROCrate_decoder as ROCrate_decoder_1, ISAJson_encoder as ISAJson_encoder_5, ISAJson_decoder as ISAJson_decoder_2)
from .comment import (encoder as encoder_9, decoder as decoder_6, ROCrate_encoder as ROCrate_encoder_6, ROCrate_decoder as ROCrate_decoder_5, ISAJson_encoder as ISAJson_encoder_6, ISAJson_decoder as ISAJson_decoder_5)
from .context.rocrate.isa_study_context import context_jsonvalue
from .data import ROCrate_encoder as ROCrate_encoder_5
from .DataMap.data_map import (encoder as encoder_8, decoder as decoder_5, encoder_compressed as encoder_compressed_2, decoder_compressed as decoder_compressed_2)
from .decode import Decode_objectNoAdditionalProperties
from .encode import (try_include, try_include_seq, try_include_list)
from .idtable import encode
from .ontology_annotation import (OntologyAnnotation_encoder, OntologyAnnotation_decoder, OntologyAnnotation_ROCrate_encoderDefinedTerm, OntologyAnnotation_ROCrate_decoderDefinedTerm, OntologyAnnotation_ISAJson_encoder, OntologyAnnotation_ISAJson_decoder)
from .person import (encoder as encoder_6, decoder as decoder_3, ROCrate_encoder as ROCrate_encoder_2, ROCrate_decoder as ROCrate_decoder_4, ISAJson_encoder as ISAJson_encoder_3, ISAJson_decoder as ISAJson_decoder_3)
from .Process.factor import encoder as encoder_10
from .Process.material_attribute import encoder as encoder_11
from .Process.process import (ROCrate_encoder as ROCrate_encoder_3, ROCrate_decoder as ROCrate_decoder_2, ISAJson_encoder as ISAJson_encoder_4, ISAJson_decoder as ISAJson_decoder_1)
from .Process.protocol import ISAJson_encoder as ISAJson_encoder_1
from .Process.study_materials import encoder as encoder_12
from .publication import (encoder as encoder_5, decoder as decoder_2, ROCrate_encoder as ROCrate_encoder_1, ROCrate_decoder as ROCrate_decoder_3, ISAJson_encoder as ISAJson_encoder_2, ISAJson_decoder as ISAJson_decoder_4)
from .Table.arc_table import (encoder as encoder_7, decoder as decoder_4, encoder_compressed as encoder_compressed_1, decoder_compressed as decoder_compressed_1)

__A_ = TypeVar("__A_")

def Helper_getAssayInformation(assays: FSharpList[ArcAssay] | None, study: ArcStudy) -> Array[ArcAssay]:
    if assays is not None:
        def f(assay_id: str, assays: Any=assays, study: Any=study) -> ArcAssay:
            def predicate(a: ArcAssay, assay_id: Any=assay_id) -> bool:
                return a.Identifier == assay_id

            return default_arg(try_find(predicate, value_17(assays)), ArcAssay.init(assay_id))

        return ResizeArray_map(f, study.RegisteredAssayIdentifiers)

    else: 
        return study.GetRegisteredAssaysOrIdentifier()



def encoder(study: ArcStudy) -> IEncodable:
    def chooser(tupled_arg: tuple[str, IEncodable | None], study: Any=study) -> tuple[str, IEncodable] | None:
        def mapping(v_1: IEncodable, tupled_arg: Any=tupled_arg) -> tuple[str, IEncodable]:
            return (tupled_arg[0], v_1)

        return map(mapping, tupled_arg[1])

    def _arrow2616(__unit: None=None, study: Any=study) -> IEncodable:
        value: str = study.Identifier
        class ObjectExpr2615(IEncodable):
            def Encode(self, helpers: IEncoderHelpers_1[Any]) -> Any:
                return helpers.encode_string(value)

        return ObjectExpr2615()

    def _arrow2618(value_1: str, study: Any=study) -> IEncodable:
        class ObjectExpr2617(IEncodable):
            def Encode(self, helpers_1: IEncoderHelpers_1[Any]) -> Any:
                return helpers_1.encode_string(value_1)

        return ObjectExpr2617()

    def _arrow2620(value_3: str, study: Any=study) -> IEncodable:
        class ObjectExpr2619(IEncodable):
            def Encode(self, helpers_2: IEncoderHelpers_1[Any]) -> Any:
                return helpers_2.encode_string(value_3)

        return ObjectExpr2619()

    def _arrow2622(value_5: str, study: Any=study) -> IEncodable:
        class ObjectExpr2621(IEncodable):
            def Encode(self, helpers_3: IEncoderHelpers_1[Any]) -> Any:
                return helpers_3.encode_string(value_5)

        return ObjectExpr2621()

    def _arrow2624(value_7: str, study: Any=study) -> IEncodable:
        class ObjectExpr2623(IEncodable):
            def Encode(self, helpers_4: IEncoderHelpers_1[Any]) -> Any:
                return helpers_4.encode_string(value_7)

        return ObjectExpr2623()

    def _arrow2625(oa: Publication, study: Any=study) -> IEncodable:
        return encoder_5(oa)

    def _arrow2626(person: Person, study: Any=study) -> IEncodable:
        return encoder_6(person)

    def _arrow2627(oa_1: OntologyAnnotation, study: Any=study) -> IEncodable:
        return OntologyAnnotation_encoder(oa_1)

    def _arrow2628(table: ArcTable, study: Any=study) -> IEncodable:
        return encoder_7(table)

    def _arrow2629(dm: DataMap, study: Any=study) -> IEncodable:
        return encoder_8(dm)

    def _arrow2631(value_9: str, study: Any=study) -> IEncodable:
        class ObjectExpr2630(IEncodable):
            def Encode(self, helpers_5: IEncoderHelpers_1[Any]) -> Any:
                return helpers_5.encode_string(value_9)

        return ObjectExpr2630()

    def _arrow2632(comment: Comment, study: Any=study) -> IEncodable:
        return encoder_9(comment)

    values: FSharpList[tuple[str, IEncodable]] = choose(chooser, of_array([("Identifier", _arrow2616()), try_include("Title", _arrow2618, study.Title), try_include("Description", _arrow2620, study.Description), try_include("SubmissionDate", _arrow2622, study.SubmissionDate), try_include("PublicReleaseDate", _arrow2624, study.PublicReleaseDate), try_include_seq("Publications", _arrow2625, study.Publications), try_include_seq("Contacts", _arrow2626, study.Contacts), try_include_seq("StudyDesignDescriptors", _arrow2627, study.StudyDesignDescriptors), try_include_seq("Tables", _arrow2628, study.Tables), try_include("DataMap", _arrow2629, study.DataMap), try_include_seq("RegisteredAssayIdentifiers", _arrow2631, study.RegisteredAssayIdentifiers), try_include_seq("Comments", _arrow2632, study.Comments)]))
    class ObjectExpr2633(IEncodable):
        def Encode(self, helpers_6: IEncoderHelpers_1[Any], study: Any=study) -> Any:
            def mapping_1(tupled_arg_1: tuple[str, IEncodable]) -> tuple[str, __A_]:
                return (tupled_arg_1[0], tupled_arg_1[1].Encode(helpers_6))

            arg: IEnumerable_1[tuple[str, __A_]] = map_1(mapping_1, values)
            return helpers_6.encode_object(arg)

    return ObjectExpr2633()


def _arrow2646(get: IGetters) -> ArcStudy:
    def _arrow2634(__unit: None=None) -> str:
        object_arg: IRequiredGetter = get.Required
        return object_arg.Field("Identifier", string)

    def _arrow2635(__unit: None=None) -> str | None:
        object_arg_1: IOptionalGetter = get.Optional
        return object_arg_1.Field("Title", string)

    def _arrow2636(__unit: None=None) -> str | None:
        object_arg_2: IOptionalGetter = get.Optional
        return object_arg_2.Field("Description", string)

    def _arrow2637(__unit: None=None) -> str | None:
        object_arg_3: IOptionalGetter = get.Optional
        return object_arg_3.Field("SubmissionDate", string)

    def _arrow2638(__unit: None=None) -> str | None:
        object_arg_4: IOptionalGetter = get.Optional
        return object_arg_4.Field("PublicReleaseDate", string)

    def _arrow2639(__unit: None=None) -> Array[Publication] | None:
        arg_11: Decoder_1[Array[Publication]] = resize_array(decoder_2)
        object_arg_5: IOptionalGetter = get.Optional
        return object_arg_5.Field("Publications", arg_11)

    def _arrow2640(__unit: None=None) -> Array[Person] | None:
        arg_13: Decoder_1[Array[Person]] = resize_array(decoder_3)
        object_arg_6: IOptionalGetter = get.Optional
        return object_arg_6.Field("Contacts", arg_13)

    def _arrow2641(__unit: None=None) -> Array[OntologyAnnotation] | None:
        arg_15: Decoder_1[Array[OntologyAnnotation]] = resize_array(OntologyAnnotation_decoder)
        object_arg_7: IOptionalGetter = get.Optional
        return object_arg_7.Field("StudyDesignDescriptors", arg_15)

    def _arrow2642(__unit: None=None) -> Array[ArcTable] | None:
        arg_17: Decoder_1[Array[ArcTable]] = resize_array(decoder_4)
        object_arg_8: IOptionalGetter = get.Optional
        return object_arg_8.Field("Tables", arg_17)

    def _arrow2643(__unit: None=None) -> DataMap | None:
        object_arg_9: IOptionalGetter = get.Optional
        return object_arg_9.Field("DataMap", decoder_5)

    def _arrow2644(__unit: None=None) -> Array[str] | None:
        arg_21: Decoder_1[Array[str]] = resize_array(string)
        object_arg_10: IOptionalGetter = get.Optional
        return object_arg_10.Field("RegisteredAssayIdentifiers", arg_21)

    def _arrow2645(__unit: None=None) -> Array[Comment] | None:
        arg_23: Decoder_1[Array[Comment]] = resize_array(decoder_6)
        object_arg_11: IOptionalGetter = get.Optional
        return object_arg_11.Field("Comments", arg_23)

    return ArcStudy(_arrow2634(), _arrow2635(), _arrow2636(), _arrow2637(), _arrow2638(), _arrow2639(), _arrow2640(), _arrow2641(), _arrow2642(), _arrow2643(), _arrow2644(), _arrow2645())


decoder: Decoder_1[ArcStudy] = object(_arrow2646)

def encoder_compressed(string_table: Any, oa_table: Any, cell_table: Any, study: ArcStudy) -> IEncodable:
    def chooser(tupled_arg: tuple[str, IEncodable | None], string_table: Any=string_table, oa_table: Any=oa_table, cell_table: Any=cell_table, study: Any=study) -> tuple[str, IEncodable] | None:
        def mapping(v_1: IEncodable, tupled_arg: Any=tupled_arg) -> tuple[str, IEncodable]:
            return (tupled_arg[0], v_1)

        return map(mapping, tupled_arg[1])

    def _arrow2650(__unit: None=None, string_table: Any=string_table, oa_table: Any=oa_table, cell_table: Any=cell_table, study: Any=study) -> IEncodable:
        value: str = study.Identifier
        class ObjectExpr2649(IEncodable):
            def Encode(self, helpers: IEncoderHelpers_1[Any]) -> Any:
                return helpers.encode_string(value)

        return ObjectExpr2649()

    def _arrow2652(value_1: str, string_table: Any=string_table, oa_table: Any=oa_table, cell_table: Any=cell_table, study: Any=study) -> IEncodable:
        class ObjectExpr2651(IEncodable):
            def Encode(self, helpers_1: IEncoderHelpers_1[Any]) -> Any:
                return helpers_1.encode_string(value_1)

        return ObjectExpr2651()

    def _arrow2654(value_3: str, string_table: Any=string_table, oa_table: Any=oa_table, cell_table: Any=cell_table, study: Any=study) -> IEncodable:
        class ObjectExpr2653(IEncodable):
            def Encode(self, helpers_2: IEncoderHelpers_1[Any]) -> Any:
                return helpers_2.encode_string(value_3)

        return ObjectExpr2653()

    def _arrow2656(value_5: str, string_table: Any=string_table, oa_table: Any=oa_table, cell_table: Any=cell_table, study: Any=study) -> IEncodable:
        class ObjectExpr2655(IEncodable):
            def Encode(self, helpers_3: IEncoderHelpers_1[Any]) -> Any:
                return helpers_3.encode_string(value_5)

        return ObjectExpr2655()

    def _arrow2658(value_7: str, string_table: Any=string_table, oa_table: Any=oa_table, cell_table: Any=cell_table, study: Any=study) -> IEncodable:
        class ObjectExpr2657(IEncodable):
            def Encode(self, helpers_4: IEncoderHelpers_1[Any]) -> Any:
                return helpers_4.encode_string(value_7)

        return ObjectExpr2657()

    def _arrow2659(oa: Publication, string_table: Any=string_table, oa_table: Any=oa_table, cell_table: Any=cell_table, study: Any=study) -> IEncodable:
        return encoder_5(oa)

    def _arrow2660(person: Person, string_table: Any=string_table, oa_table: Any=oa_table, cell_table: Any=cell_table, study: Any=study) -> IEncodable:
        return encoder_6(person)

    def _arrow2661(oa_1: OntologyAnnotation, string_table: Any=string_table, oa_table: Any=oa_table, cell_table: Any=cell_table, study: Any=study) -> IEncodable:
        return OntologyAnnotation_encoder(oa_1)

    def _arrow2662(table: ArcTable, string_table: Any=string_table, oa_table: Any=oa_table, cell_table: Any=cell_table, study: Any=study) -> IEncodable:
        return encoder_compressed_1(string_table, oa_table, cell_table, table)

    def _arrow2663(dm: DataMap, string_table: Any=string_table, oa_table: Any=oa_table, cell_table: Any=cell_table, study: Any=study) -> IEncodable:
        return encoder_compressed_2(string_table, oa_table, cell_table, dm)

    def _arrow2665(value_9: str, string_table: Any=string_table, oa_table: Any=oa_table, cell_table: Any=cell_table, study: Any=study) -> IEncodable:
        class ObjectExpr2664(IEncodable):
            def Encode(self, helpers_5: IEncoderHelpers_1[Any]) -> Any:
                return helpers_5.encode_string(value_9)

        return ObjectExpr2664()

    def _arrow2666(comment: Comment, string_table: Any=string_table, oa_table: Any=oa_table, cell_table: Any=cell_table, study: Any=study) -> IEncodable:
        return encoder_9(comment)

    values: FSharpList[tuple[str, IEncodable]] = choose(chooser, of_array([("Identifier", _arrow2650()), try_include("Title", _arrow2652, study.Title), try_include("Description", _arrow2654, study.Description), try_include("SubmissionDate", _arrow2656, study.SubmissionDate), try_include("PublicReleaseDate", _arrow2658, study.PublicReleaseDate), try_include_seq("Publications", _arrow2659, study.Publications), try_include_seq("Contacts", _arrow2660, study.Contacts), try_include_seq("StudyDesignDescriptors", _arrow2661, study.StudyDesignDescriptors), try_include_seq("Tables", _arrow2662, study.Tables), try_include("DataMap", _arrow2663, study.DataMap), try_include_seq("RegisteredAssayIdentifiers", _arrow2665, study.RegisteredAssayIdentifiers), try_include_seq("Comments", _arrow2666, study.Comments)]))
    class ObjectExpr2667(IEncodable):
        def Encode(self, helpers_6: IEncoderHelpers_1[Any], string_table: Any=string_table, oa_table: Any=oa_table, cell_table: Any=cell_table, study: Any=study) -> Any:
            def mapping_1(tupled_arg_1: tuple[str, IEncodable]) -> tuple[str, __A_]:
                return (tupled_arg_1[0], tupled_arg_1[1].Encode(helpers_6))

            arg: IEnumerable_1[tuple[str, __A_]] = map_1(mapping_1, values)
            return helpers_6.encode_object(arg)

    return ObjectExpr2667()


def decoder_compressed(string_table: Array[str], oa_table: Array[OntologyAnnotation], cell_table: Array[CompositeCell]) -> Decoder_1[ArcStudy]:
    def _arrow2680(get: IGetters, string_table: Any=string_table, oa_table: Any=oa_table, cell_table: Any=cell_table) -> ArcStudy:
        def _arrow2668(__unit: None=None) -> str:
            object_arg: IRequiredGetter = get.Required
            return object_arg.Field("Identifier", string)

        def _arrow2669(__unit: None=None) -> str | None:
            object_arg_1: IOptionalGetter = get.Optional
            return object_arg_1.Field("Title", string)

        def _arrow2670(__unit: None=None) -> str | None:
            object_arg_2: IOptionalGetter = get.Optional
            return object_arg_2.Field("Description", string)

        def _arrow2671(__unit: None=None) -> str | None:
            object_arg_3: IOptionalGetter = get.Optional
            return object_arg_3.Field("SubmissionDate", string)

        def _arrow2672(__unit: None=None) -> str | None:
            object_arg_4: IOptionalGetter = get.Optional
            return object_arg_4.Field("PublicReleaseDate", string)

        def _arrow2673(__unit: None=None) -> Array[Publication] | None:
            arg_11: Decoder_1[Array[Publication]] = resize_array(decoder_2)
            object_arg_5: IOptionalGetter = get.Optional
            return object_arg_5.Field("Publications", arg_11)

        def _arrow2674(__unit: None=None) -> Array[Person] | None:
            arg_13: Decoder_1[Array[Person]] = resize_array(decoder_3)
            object_arg_6: IOptionalGetter = get.Optional
            return object_arg_6.Field("Contacts", arg_13)

        def _arrow2675(__unit: None=None) -> Array[OntologyAnnotation] | None:
            arg_15: Decoder_1[Array[OntologyAnnotation]] = resize_array(OntologyAnnotation_decoder)
            object_arg_7: IOptionalGetter = get.Optional
            return object_arg_7.Field("StudyDesignDescriptors", arg_15)

        def _arrow2676(__unit: None=None) -> Array[ArcTable] | None:
            arg_17: Decoder_1[Array[ArcTable]] = resize_array(decoder_compressed_1(string_table, oa_table, cell_table))
            object_arg_8: IOptionalGetter = get.Optional
            return object_arg_8.Field("Tables", arg_17)

        def _arrow2677(__unit: None=None) -> DataMap | None:
            arg_19: Decoder_1[DataMap] = decoder_compressed_2(string_table, oa_table, cell_table)
            object_arg_9: IOptionalGetter = get.Optional
            return object_arg_9.Field("DataMap", arg_19)

        def _arrow2678(__unit: None=None) -> Array[str] | None:
            arg_21: Decoder_1[Array[str]] = resize_array(string)
            object_arg_10: IOptionalGetter = get.Optional
            return object_arg_10.Field("RegisteredAssayIdentifiers", arg_21)

        def _arrow2679(__unit: None=None) -> Array[Comment] | None:
            arg_23: Decoder_1[Array[Comment]] = resize_array(decoder_6)
            object_arg_11: IOptionalGetter = get.Optional
            return object_arg_11.Field("Comments", arg_23)

        return ArcStudy(_arrow2668(), _arrow2669(), _arrow2670(), _arrow2671(), _arrow2672(), _arrow2673(), _arrow2674(), _arrow2675(), _arrow2676(), _arrow2677(), _arrow2678(), _arrow2679())

    return object(_arrow2680)


def ROCrate_genID(a: ArcStudy) -> str:
    match_value: str = a.Identifier
    if match_value == "":
        return "#EmptyStudy"

    else: 
        return ("studies/" + replace(match_value, " ", "_")) + "/"



def ROCrate_encoder(assays: FSharpList[ArcAssay] | None, s: ArcStudy) -> IEncodable:
    file_name: str | None = Study_tryFileNameFromIdentifier(s.Identifier)
    processes: FSharpList[Process] = ARCtrl_ArcTables__ArcTables_GetProcesses(s)
    assays_1: Array[ArcAssay] = Helper_getAssayInformation(assays, s)
    def chooser(tupled_arg: tuple[str, IEncodable | None], assays: Any=assays, s: Any=s) -> tuple[str, IEncodable] | None:
        def mapping(v_1: IEncodable, tupled_arg: Any=tupled_arg) -> tuple[str, IEncodable]:
            return (tupled_arg[0], v_1)

        return map(mapping, tupled_arg[1])

    def _arrow2684(__unit: None=None, assays: Any=assays, s: Any=s) -> IEncodable:
        value: str = ROCrate_genID(s)
        class ObjectExpr2683(IEncodable):
            def Encode(self, helpers: IEncoderHelpers_1[Any]) -> Any:
                return helpers.encode_string(value)

        return ObjectExpr2683()

    class ObjectExpr2685(IEncodable):
        def Encode(self, helpers_1: IEncoderHelpers_1[Any], assays: Any=assays, s: Any=s) -> Any:
            return helpers_1.encode_string("Study")

    class ObjectExpr2686(IEncodable):
        def Encode(self, helpers_2: IEncoderHelpers_1[Any], assays: Any=assays, s: Any=s) -> Any:
            return helpers_2.encode_string("Study")

    def _arrow2688(__unit: None=None, assays: Any=assays, s: Any=s) -> IEncodable:
        value_3: str = s.Identifier
        class ObjectExpr2687(IEncodable):
            def Encode(self, helpers_3: IEncoderHelpers_1[Any]) -> Any:
                return helpers_3.encode_string(value_3)

        return ObjectExpr2687()

    def _arrow2690(value_4: str, assays: Any=assays, s: Any=s) -> IEncodable:
        class ObjectExpr2689(IEncodable):
            def Encode(self, helpers_4: IEncoderHelpers_1[Any]) -> Any:
                return helpers_4.encode_string(value_4)

        return ObjectExpr2689()

    def _arrow2692(value_6: str, assays: Any=assays, s: Any=s) -> IEncodable:
        class ObjectExpr2691(IEncodable):
            def Encode(self, helpers_5: IEncoderHelpers_1[Any]) -> Any:
                return helpers_5.encode_string(value_6)

        return ObjectExpr2691()

    def _arrow2694(value_8: str, assays: Any=assays, s: Any=s) -> IEncodable:
        class ObjectExpr2693(IEncodable):
            def Encode(self, helpers_6: IEncoderHelpers_1[Any]) -> Any:
                return helpers_6.encode_string(value_8)

        return ObjectExpr2693()

    def _arrow2695(oa: OntologyAnnotation, assays: Any=assays, s: Any=s) -> IEncodable:
        return OntologyAnnotation_ROCrate_encoderDefinedTerm(oa)

    def _arrow2697(value_10: str, assays: Any=assays, s: Any=s) -> IEncodable:
        class ObjectExpr2696(IEncodable):
            def Encode(self, helpers_7: IEncoderHelpers_1[Any]) -> Any:
                return helpers_7.encode_string(value_10)

        return ObjectExpr2696()

    def _arrow2699(value_12: str, assays: Any=assays, s: Any=s) -> IEncodable:
        class ObjectExpr2698(IEncodable):
            def Encode(self, helpers_8: IEncoderHelpers_1[Any]) -> Any:
                return helpers_8.encode_string(value_12)

        return ObjectExpr2698()

    def _arrow2700(oa_1: Publication, assays: Any=assays, s: Any=s) -> IEncodable:
        return ROCrate_encoder_1(oa_1)

    def _arrow2701(oa_2: Person, assays: Any=assays, s: Any=s) -> IEncodable:
        return ROCrate_encoder_2(oa_2)

    def _arrow2703(__unit: None=None, assays: Any=assays, s: Any=s) -> Callable[[Process], IEncodable]:
        study_name: str | None = s.Identifier
        def _arrow2702(oa_3: Process) -> IEncodable:
            return ROCrate_encoder_3(study_name, None, oa_3)

        return _arrow2702

    def _arrow2705(__unit: None=None, assays: Any=assays, s: Any=s) -> Callable[[ArcAssay], IEncodable]:
        assay_name_1: str | None = s.Identifier
        def _arrow2704(a_1: ArcAssay) -> IEncodable:
            return ROCrate_encoder_4(assay_name_1, a_1)

        return _arrow2704

    def _arrow2706(oa_4: Data, assays: Any=assays, s: Any=s) -> IEncodable:
        return ROCrate_encoder_5(oa_4)

    def _arrow2707(comment: Comment, assays: Any=assays, s: Any=s) -> IEncodable:
        return ROCrate_encoder_6(comment)

    values: FSharpList[tuple[str, IEncodable]] = choose(chooser, of_array([("@id", _arrow2684()), ("@type", list_1_1(singleton(ObjectExpr2685()))), ("additionalType", ObjectExpr2686()), ("identifier", _arrow2688()), try_include("filename", _arrow2690, file_name), try_include("title", _arrow2692, s.Title), try_include("description", _arrow2694, s.Description), try_include_seq("studyDesignDescriptors", _arrow2695, s.StudyDesignDescriptors), try_include("submissionDate", _arrow2697, s.SubmissionDate), try_include("publicReleaseDate", _arrow2699, s.PublicReleaseDate), try_include_seq("publications", _arrow2700, s.Publications), try_include_seq("people", _arrow2701, s.Contacts), try_include_list("processSequence", _arrow2703(), processes), try_include_seq("assays", _arrow2705(), assays_1), try_include_list("dataFiles", _arrow2706, get_data(processes)), try_include_seq("comments", _arrow2707, s.Comments), ("@context", context_jsonvalue)]))
    class ObjectExpr2708(IEncodable):
        def Encode(self, helpers_9: IEncoderHelpers_1[Any], assays: Any=assays, s: Any=s) -> Any:
            def mapping_1(tupled_arg_1: tuple[str, IEncodable]) -> tuple[str, __A_]:
                return (tupled_arg_1[0], tupled_arg_1[1].Encode(helpers_9))

            arg: IEnumerable_1[tuple[str, __A_]] = map_1(mapping_1, values)
            return helpers_9.encode_object(arg)

    return ObjectExpr2708()


def _arrow2719(get: IGetters) -> tuple[ArcStudy, FSharpList[ArcAssay]]:
    def _arrow2709(__unit: None=None) -> str | None:
        object_arg: IOptionalGetter = get.Optional
        return object_arg.Field("filename", string)

    identifier: str = default_arg(bind(Study_tryIdentifierFromFileName, _arrow2709()), create_missing_identifier())
    assays: FSharpList[ArcAssay] | None
    arg_3: Decoder_1[FSharpList[ArcAssay]] = list_1_2(ROCrate_decoder_1)
    object_arg_1: IOptionalGetter = get.Optional
    assays = object_arg_1.Field("assays", arg_3)
    def mapping_1(arg_4: FSharpList[ArcAssay]) -> Array[str]:
        def mapping(a: ArcAssay, arg_4: Any=arg_4) -> str:
            return a.Identifier

        return list(map_2(mapping, arg_4))

    assay_identifiers: Array[str] | None = map(mapping_1, assays)
    def mapping_2(ps: FSharpList[Process]) -> Array[ArcTable]:
        return ARCtrl_ArcTables__ArcTables_fromProcesses_Static_62A3309D(ps).Tables

    def _arrow2710(__unit: None=None) -> FSharpList[Process] | None:
        arg_6: Decoder_1[FSharpList[Process]] = list_1_2(ROCrate_decoder_2)
        object_arg_2: IOptionalGetter = get.Optional
        return object_arg_2.Field("processSequence", arg_6)

    tables: Array[ArcTable] | None = map(mapping_2, _arrow2710())
    def _arrow2711(__unit: None=None) -> str | None:
        object_arg_3: IOptionalGetter = get.Optional
        return object_arg_3.Field("title", string)

    def _arrow2712(__unit: None=None) -> str | None:
        object_arg_4: IOptionalGetter = get.Optional
        return object_arg_4.Field("description", string)

    def _arrow2713(__unit: None=None) -> str | None:
        object_arg_5: IOptionalGetter = get.Optional
        return object_arg_5.Field("submissionDate", string)

    def _arrow2714(__unit: None=None) -> str | None:
        object_arg_6: IOptionalGetter = get.Optional
        return object_arg_6.Field("publicReleaseDate", string)

    def _arrow2715(__unit: None=None) -> Array[Publication] | None:
        arg_16: Decoder_1[Array[Publication]] = resize_array(ROCrate_decoder_3)
        object_arg_7: IOptionalGetter = get.Optional
        return object_arg_7.Field("publications", arg_16)

    def _arrow2716(__unit: None=None) -> Array[Person] | None:
        arg_18: Decoder_1[Array[Person]] = resize_array(ROCrate_decoder_4)
        object_arg_8: IOptionalGetter = get.Optional
        return object_arg_8.Field("people", arg_18)

    def _arrow2717(__unit: None=None) -> Array[OntologyAnnotation] | None:
        arg_20: Decoder_1[Array[OntologyAnnotation]] = resize_array(OntologyAnnotation_ROCrate_decoderDefinedTerm)
        object_arg_9: IOptionalGetter = get.Optional
        return object_arg_9.Field("studyDesignDescriptors", arg_20)

    def _arrow2718(__unit: None=None) -> Array[Comment] | None:
        arg_22: Decoder_1[Array[Comment]] = resize_array(ROCrate_decoder_5)
        object_arg_10: IOptionalGetter = get.Optional
        return object_arg_10.Field("comments", arg_22)

    return (ArcStudy(identifier, _arrow2711(), _arrow2712(), _arrow2713(), _arrow2714(), _arrow2715(), _arrow2716(), _arrow2717(), tables, None, assay_identifiers, _arrow2718()), default_arg(assays, empty()))


ROCrate_decoder: Decoder_1[tuple[ArcStudy, FSharpList[ArcAssay]]] = object(_arrow2719)

def ISAJson_encoder(id_map: Any | None, assays: FSharpList[ArcAssay] | None, s: ArcStudy) -> IEncodable:
    def f(s_1: ArcStudy, id_map: Any=id_map, assays: Any=assays, s: Any=s) -> IEncodable:
        study: ArcStudy = s_1.Copy(True)
        file_name: str = Study_fileNameFromIdentifier(study.Identifier)
        assays_1: Array[ArcAssay]
        n: Array[ArcAssay] = []
        enumerator: Any = get_enumerator(Helper_getAssayInformation(assays, study))
        try: 
            while enumerator.System_Collections_IEnumerator_MoveNext():
                a: ArcAssay = enumerator.System_Collections_Generic_IEnumerator_1_get_Current()
                assay: ArcAssay = a.Copy()
                enumerator_1: Any = get_enumerator(assay.Performers)
                try: 
                    while enumerator_1.System_Collections_IEnumerator_MoveNext():
                        person_1: Person = Person_setSourceAssayComment(enumerator_1.System_Collections_Generic_IEnumerator_1_get_Current(), assay.Identifier)
                        (study.Contacts.append(person_1))

                finally: 
                    dispose(enumerator_1)

                assay.Performers = []
                (n.append(assay))

        finally: 
            dispose(enumerator)

        assays_1 = n
        processes: FSharpList[Process] = ARCtrl_ArcTables__ArcTables_GetProcesses(study)
        def encoder_1(oa: OntologyAnnotation, s_1: Any=s_1) -> IEncodable:
            return OntologyAnnotation_ISAJson_encoder(id_map, oa)

        encoded_units: tuple[str, IEncodable | None] = try_include_list("unitCategories", encoder_1, get_units(processes))
        def encoder_2(value_1: Factor, s_1: Any=s_1) -> IEncodable:
            return encoder_10(id_map, value_1)

        encoded_factors: tuple[str, IEncodable | None] = try_include_list("factors", encoder_2, get_factors(processes))
        def encoder_3(value_3: MaterialAttribute, s_1: Any=s_1) -> IEncodable:
            return encoder_11(id_map, value_3)

        encoded_characteristics: tuple[str, IEncodable | None] = try_include_list("characteristicCategories", encoder_3, get_characteristics(processes))
        def _arrow2720(ps: FSharpList[Process], s_1: Any=s_1) -> IEncodable:
            return encoder_12(id_map, ps)

        encoded_materials: tuple[str, IEncodable | None] = try_include("materials", _arrow2720, Option_fromValueWithDefault(empty(), processes))
        encoded_protocols: tuple[str, IEncodable | None]
        value_5: FSharpList[Protocol] = get_protocols(processes)
        def _arrow2722(__unit: None=None, s_1: Any=s_1) -> Callable[[Protocol], IEncodable]:
            study_name: str | None = s_1.Identifier
            def _arrow2721(oa_1: Protocol) -> IEncodable:
                return ISAJson_encoder_1(study_name, None, None, id_map, oa_1)

            return _arrow2721

        encoded_protocols = try_include_list("protocols", _arrow2722(), value_5)
        def chooser(tupled_arg: tuple[str, IEncodable | None], s_1: Any=s_1) -> tuple[str, IEncodable] | None:
            def mapping(v_1: IEncodable, tupled_arg: Any=tupled_arg) -> tuple[str, IEncodable]:
                return (tupled_arg[0], v_1)

            return map(mapping, tupled_arg[1])

        def _arrow2726(__unit: None=None, s_1: Any=s_1) -> IEncodable:
            value_6: str = ROCrate_genID(study)
            class ObjectExpr2725(IEncodable):
                def Encode(self, helpers: IEncoderHelpers_1[Any]) -> Any:
                    return helpers.encode_string(value_6)

            return ObjectExpr2725()

        class ObjectExpr2727(IEncodable):
            def Encode(self, helpers_1: IEncoderHelpers_1[Any], s_1: Any=s_1) -> Any:
                return helpers_1.encode_string(file_name)

        def _arrow2729(__unit: None=None, s_1: Any=s_1) -> IEncodable:
            value_8: str = study.Identifier
            class ObjectExpr2728(IEncodable):
                def Encode(self, helpers_2: IEncoderHelpers_1[Any]) -> Any:
                    return helpers_2.encode_string(value_8)

            return ObjectExpr2728()

        def _arrow2731(value_9: str, s_1: Any=s_1) -> IEncodable:
            class ObjectExpr2730(IEncodable):
                def Encode(self, helpers_3: IEncoderHelpers_1[Any]) -> Any:
                    return helpers_3.encode_string(value_9)

            return ObjectExpr2730()

        def _arrow2733(value_11: str, s_1: Any=s_1) -> IEncodable:
            class ObjectExpr2732(IEncodable):
                def Encode(self, helpers_4: IEncoderHelpers_1[Any]) -> Any:
                    return helpers_4.encode_string(value_11)

            return ObjectExpr2732()

        def _arrow2735(value_13: str, s_1: Any=s_1) -> IEncodable:
            class ObjectExpr2734(IEncodable):
                def Encode(self, helpers_5: IEncoderHelpers_1[Any]) -> Any:
                    return helpers_5.encode_string(value_13)

            return ObjectExpr2734()

        def _arrow2737(value_15: str, s_1: Any=s_1) -> IEncodable:
            class ObjectExpr2736(IEncodable):
                def Encode(self, helpers_6: IEncoderHelpers_1[Any]) -> Any:
                    return helpers_6.encode_string(value_15)

            return ObjectExpr2736()

        def _arrow2738(oa_2: Publication, s_1: Any=s_1) -> IEncodable:
            return ISAJson_encoder_2(id_map, oa_2)

        def _arrow2739(person_2: Person, s_1: Any=s_1) -> IEncodable:
            return ISAJson_encoder_3(id_map, person_2)

        def _arrow2740(oa_3: OntologyAnnotation, s_1: Any=s_1) -> IEncodable:
            return OntologyAnnotation_ISAJson_encoder(id_map, oa_3)

        def _arrow2742(__unit: None=None, s_1: Any=s_1) -> Callable[[Process], IEncodable]:
            study_name_1: str | None = s_1.Identifier
            def _arrow2741(oa_4: Process) -> IEncodable:
                return ISAJson_encoder_4(study_name_1, None, id_map, oa_4)

            return _arrow2741

        def _arrow2744(__unit: None=None, s_1: Any=s_1) -> Callable[[ArcAssay], IEncodable]:
            study_name_2: str | None = s_1.Identifier
            def _arrow2743(a_2: ArcAssay) -> IEncodable:
                return ISAJson_encoder_5(study_name_2, id_map, a_2)

            return _arrow2743

        def _arrow2745(comment: Comment, s_1: Any=s_1) -> IEncodable:
            return ISAJson_encoder_6(id_map, comment)

        values: FSharpList[tuple[str, IEncodable]] = choose(chooser, of_array([("@id", _arrow2726()), ("filename", ObjectExpr2727()), ("identifier", _arrow2729()), try_include("title", _arrow2731, study.Title), try_include("description", _arrow2733, study.Description), try_include("submissionDate", _arrow2735, study.SubmissionDate), try_include("publicReleaseDate", _arrow2737, study.PublicReleaseDate), try_include_seq("publications", _arrow2738, study.Publications), try_include_seq("people", _arrow2739, study.Contacts), try_include_seq("studyDesignDescriptors", _arrow2740, study.StudyDesignDescriptors), encoded_protocols, encoded_materials, try_include_list("processSequence", _arrow2742(), processes), try_include_seq("assays", _arrow2744(), assays_1), encoded_factors, encoded_characteristics, encoded_units, try_include_seq("comments", _arrow2745, study.Comments)]))
        class ObjectExpr2746(IEncodable):
            def Encode(self, helpers_7: IEncoderHelpers_1[Any], s_1: Any=s_1) -> Any:
                def mapping_1(tupled_arg_1: tuple[str, IEncodable]) -> tuple[str, __A_]:
                    return (tupled_arg_1[0], tupled_arg_1[1].Encode(helpers_7))

                arg: IEnumerable_1[tuple[str, __A_]] = map_1(mapping_1, values)
                return helpers_7.encode_object(arg)

        return ObjectExpr2746()

    if id_map is not None:
        def _arrow2747(s_2: ArcStudy, id_map: Any=id_map, assays: Any=assays, s: Any=s) -> str:
            return ROCrate_genID(s_2)

        return encode(_arrow2747, f, s, id_map)

    else: 
        return f(s)



ISAJson_allowedFields: FSharpList[str] = of_array(["@id", "filename", "identifier", "title", "description", "submissionDate", "publicReleaseDate", "publications", "people", "studyDesignDescriptors", "protocols", "materials", "assays", "factors", "characteristicCategories", "unitCategories", "processSequence", "comments", "@type", "@context"])

def _arrow2758(get: IGetters) -> tuple[ArcStudy, FSharpList[ArcAssay]]:
    def _arrow2748(__unit: None=None) -> str | None:
        object_arg: IOptionalGetter = get.Optional
        return object_arg.Field("identifier", string)

    def def_thunk(__unit: None=None) -> str:
        def _arrow2749(__unit: None=None) -> str | None:
            object_arg_1: IOptionalGetter = get.Optional
            return object_arg_1.Field("filename", string)

        return default_arg(bind(Study_tryIdentifierFromFileName, _arrow2749()), create_missing_identifier())

    identifier: str = default_arg_with(_arrow2748(), def_thunk)
    def mapping(arg_6: FSharpList[Process]) -> Array[ArcTable]:
        a: ArcTables = ARCtrl_ArcTables__ArcTables_fromProcesses_Static_62A3309D(arg_6)
        return a.Tables

    def _arrow2750(__unit: None=None) -> FSharpList[Process] | None:
        arg_5: Decoder_1[FSharpList[Process]] = list_1_2(ISAJson_decoder_1)
        object_arg_2: IOptionalGetter = get.Optional
        return object_arg_2.Field("processSequence", arg_5)

    tables: Array[ArcTable] | None = map(mapping, _arrow2750())
    assays: FSharpList[ArcAssay] | None
    arg_8: Decoder_1[FSharpList[ArcAssay]] = list_1_2(ISAJson_decoder_2)
    object_arg_3: IOptionalGetter = get.Optional
    assays = object_arg_3.Field("assays", arg_8)
    persons_raw: Array[Person] | None
    arg_10: Decoder_1[Array[Person]] = resize_array(ISAJson_decoder_3)
    object_arg_4: IOptionalGetter = get.Optional
    persons_raw = object_arg_4.Field("people", arg_10)
    persons: Array[Person] = []
    if persons_raw is not None:
        enumerator: Any = get_enumerator(value_17(persons_raw))
        try: 
            while enumerator.System_Collections_IEnumerator_MoveNext():
                person: Person = enumerator.System_Collections_Generic_IEnumerator_1_get_Current()
                source_assays: IEnumerable_1[str] = Person_getSourceAssayIdentifiersFromComments(person)
                with get_enumerator(source_assays) as enumerator_1:
                    while enumerator_1.System_Collections_IEnumerator_MoveNext():
                        assay_identifier: str = enumerator_1.System_Collections_Generic_IEnumerator_1_get_Current()
                        with get_enumerator(value_17(assays)) as enumerator_2:
                            while enumerator_2.System_Collections_IEnumerator_MoveNext():
                                assay: ArcAssay = enumerator_2.System_Collections_Generic_IEnumerator_1_get_Current()
                                if assay.Identifier == assay_identifier:
                                    (assay.Performers.append(person))

                person.Comments = Person_removeSourceAssayComments(person)
                if is_empty(source_assays):
                    (persons.append(person))


        finally: 
            dispose(enumerator)


    def mapping_2(arg_11: FSharpList[ArcAssay]) -> Array[str]:
        def mapping_1(a_1: ArcAssay, arg_11: Any=arg_11) -> str:
            return a_1.Identifier

        return list(map_2(mapping_1, arg_11))

    assay_identifiers: Array[str] | None = map(mapping_2, assays)
    def _arrow2751(__unit: None=None) -> str | None:
        object_arg_5: IOptionalGetter = get.Optional
        return object_arg_5.Field("title", string)

    def _arrow2752(__unit: None=None) -> str | None:
        object_arg_6: IOptionalGetter = get.Optional
        return object_arg_6.Field("description", string)

    def _arrow2753(__unit: None=None) -> str | None:
        object_arg_7: IOptionalGetter = get.Optional
        return object_arg_7.Field("submissionDate", string)

    def _arrow2754(__unit: None=None) -> str | None:
        object_arg_8: IOptionalGetter = get.Optional
        return object_arg_8.Field("publicReleaseDate", string)

    def _arrow2755(__unit: None=None) -> Array[Publication] | None:
        arg_21: Decoder_1[Array[Publication]] = resize_array(ISAJson_decoder_4)
        object_arg_9: IOptionalGetter = get.Optional
        return object_arg_9.Field("publications", arg_21)

    def _arrow2756(__unit: None=None) -> Array[OntologyAnnotation] | None:
        arg_23: Decoder_1[Array[OntologyAnnotation]] = resize_array(OntologyAnnotation_ISAJson_decoder)
        object_arg_10: IOptionalGetter = get.Optional
        return object_arg_10.Field("studyDesignDescriptors", arg_23)

    def _arrow2757(__unit: None=None) -> Array[Comment] | None:
        arg_25: Decoder_1[Array[Comment]] = resize_array(ISAJson_decoder_5)
        object_arg_11: IOptionalGetter = get.Optional
        return object_arg_11.Field("comments", arg_25)

    return (ArcStudy(identifier, _arrow2751(), _arrow2752(), _arrow2753(), _arrow2754(), _arrow2755(), None if (len(persons) == 0) else persons, _arrow2756(), tables, None, assay_identifiers, _arrow2757()), default_arg(assays, empty()))


ISAJson_decoder: Decoder_1[tuple[ArcStudy, FSharpList[ArcAssay]]] = Decode_objectNoAdditionalProperties(ISAJson_allowedFields, _arrow2758)

__all__ = ["Helper_getAssayInformation", "encoder", "decoder", "encoder_compressed", "decoder_compressed", "ROCrate_genID", "ROCrate_encoder", "ROCrate_decoder", "ISAJson_encoder", "ISAJson_allowedFields", "ISAJson_decoder"]

