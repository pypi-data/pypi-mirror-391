from __future__ import annotations
from collections.abc import Callable
from typing import (Any, TypeVar)
from ..arctrl_core.arc_types import ArcAssay
from ..arctrl_core.comment import Comment
from ..arctrl_core.conversion import (ARCtrl_ArcTables__ArcTables_GetProcesses, ARCtrl_ArcTables__ArcTables_fromProcesses_Static_62A3309D, JsonTypes_composeTechnologyPlatform, JsonTypes_decomposeTechnologyPlatform)
from ..arctrl_core.data import Data
from ..arctrl_core.data_map import DataMap
from ..arctrl_core.Helper.collections_ import (Option_fromValueWithDefault, ResizeArray_filter)
from ..arctrl_core.Helper.identifier import (Assay_fileNameFromIdentifier, create_missing_identifier, Assay_tryIdentifierFromFileName)
from ..arctrl_core.ontology_annotation import OntologyAnnotation
from ..arctrl_core.person import Person
from ..arctrl_core.Process.material_attribute import MaterialAttribute
from ..arctrl_core.Process.process import Process
from ..arctrl_core.Process.process_sequence import (get_data, get_units, get_characteristics)
from ..arctrl_core.Table.arc_table import ArcTable
from ..arctrl_core.Table.arc_tables import ArcTables
from ..arctrl_core.Table.composite_cell import CompositeCell
from ..fable_library.list import (choose, of_array, FSharpList, singleton, empty)
from ..fable_library.option import (map, default_arg, value as value_9, bind)
from ..fable_library.seq import (map as map_1, to_list, delay, append, empty as empty_1, singleton as singleton_1, try_pick, length)
from ..fable_library.string_ import replace
from ..fable_library.types import Array
from ..fable_library.util import IEnumerable_1
from ..thoth_json_core.decode import (object, IRequiredGetter, string, IOptionalGetter, resize_array, IGetters, list_1 as list_1_2, map as map_2)
from ..thoth_json_core.encode import list_1 as list_1_1
from ..thoth_json_core.types import (IEncodable, IEncoderHelpers_1, Decoder_1)
from .comment import (encoder as encoder_7, decoder as decoder_4, ROCrate_encoder as ROCrate_encoder_4, ROCrate_decoder as ROCrate_decoder_3, ISAJson_encoder as ISAJson_encoder_3, ISAJson_decoder as ISAJson_decoder_2)
from .context.rocrate.isa_assay_context import context_jsonvalue
from .data import (ROCrate_encoder as ROCrate_encoder_2, ISAJson_encoder as ISAJson_encoder_1)
from .DataMap.data_map import (encoder as encoder_4, decoder as decoder_2, encoder_compressed as encoder_compressed_2, decoder_compressed as decoder_compressed_2)
from .decode import Decode_objectNoAdditionalProperties
from .encode import (try_include, try_include_seq, try_include_list)
from .idtable import encode
from .ontology_annotation import (OntologyAnnotation_encoder, OntologyAnnotation_decoder, OntologyAnnotation_ROCrate_encoderPropertyValue, OntologyAnnotation_ROCrate_encoderDefinedTerm, OntologyAnnotation_ROCrate_decoderPropertyValue, OntologyAnnotation_ROCrate_decoderDefinedTerm, OntologyAnnotation_ISAJson_encoder, OntologyAnnotation_ISAJson_decoder)
from .person import (encoder as encoder_6, decoder as decoder_3, ROCrate_encoder as ROCrate_encoder_1, ROCrate_decoder as ROCrate_decoder_2)
from .Process.assay_materials import encoder as encoder_9
from .Process.material_attribute import encoder as encoder_8
from .Process.process import (ROCrate_encoder as ROCrate_encoder_3, ROCrate_decoder as ROCrate_decoder_1, ISAJson_encoder as ISAJson_encoder_2, ISAJson_decoder as ISAJson_decoder_1)
from .Table.arc_table import (encoder as encoder_5, decoder as decoder_1, encoder_compressed as encoder_compressed_1, decoder_compressed as decoder_compressed_1)

__A_ = TypeVar("__A_")

def encoder(assay: ArcAssay) -> IEncodable:
    def chooser(tupled_arg: tuple[str, IEncodable | None], assay: Any=assay) -> tuple[str, IEncodable] | None:
        def mapping(v_1: IEncodable, tupled_arg: Any=tupled_arg) -> tuple[str, IEncodable]:
            return (tupled_arg[0], v_1)

        return map(mapping, tupled_arg[1])

    def _arrow2379(__unit: None=None, assay: Any=assay) -> IEncodable:
        value: str = assay.Identifier
        class ObjectExpr2378(IEncodable):
            def Encode(self, helpers: IEncoderHelpers_1[Any]) -> Any:
                return helpers.encode_string(value)

        return ObjectExpr2378()

    def _arrow2381(value_1: str, assay: Any=assay) -> IEncodable:
        class ObjectExpr2380(IEncodable):
            def Encode(self, helpers_1: IEncoderHelpers_1[Any]) -> Any:
                return helpers_1.encode_string(value_1)

        return ObjectExpr2380()

    def _arrow2383(value_3: str, assay: Any=assay) -> IEncodable:
        class ObjectExpr2382(IEncodable):
            def Encode(self, helpers_2: IEncoderHelpers_1[Any]) -> Any:
                return helpers_2.encode_string(value_3)

        return ObjectExpr2382()

    def _arrow2384(oa: OntologyAnnotation, assay: Any=assay) -> IEncodable:
        return OntologyAnnotation_encoder(oa)

    def _arrow2385(oa_1: OntologyAnnotation, assay: Any=assay) -> IEncodable:
        return OntologyAnnotation_encoder(oa_1)

    def _arrow2386(oa_2: OntologyAnnotation, assay: Any=assay) -> IEncodable:
        return OntologyAnnotation_encoder(oa_2)

    def _arrow2387(dm: DataMap, assay: Any=assay) -> IEncodable:
        return encoder_4(dm)

    def _arrow2388(table: ArcTable, assay: Any=assay) -> IEncodable:
        return encoder_5(table)

    def _arrow2389(person: Person, assay: Any=assay) -> IEncodable:
        return encoder_6(person)

    def _arrow2390(comment: Comment, assay: Any=assay) -> IEncodable:
        return encoder_7(comment)

    values: FSharpList[tuple[str, IEncodable]] = choose(chooser, of_array([("Identifier", _arrow2379()), try_include("Title", _arrow2381, assay.Title), try_include("Description", _arrow2383, assay.Description), try_include("MeasurementType", _arrow2384, assay.MeasurementType), try_include("TechnologyType", _arrow2385, assay.TechnologyType), try_include("TechnologyPlatform", _arrow2386, assay.TechnologyPlatform), try_include("DataMap", _arrow2387, assay.DataMap), try_include_seq("Tables", _arrow2388, assay.Tables), try_include_seq("Performers", _arrow2389, assay.Performers), try_include_seq("Comments", _arrow2390, assay.Comments)]))
    class ObjectExpr2391(IEncodable):
        def Encode(self, helpers_3: IEncoderHelpers_1[Any], assay: Any=assay) -> Any:
            def mapping_1(tupled_arg_1: tuple[str, IEncodable]) -> tuple[str, __A_]:
                return (tupled_arg_1[0], tupled_arg_1[1].Encode(helpers_3))

            arg: IEnumerable_1[tuple[str, __A_]] = map_1(mapping_1, values)
            return helpers_3.encode_object(arg)

    return ObjectExpr2391()


def _arrow2402(get: IGetters) -> ArcAssay:
    def _arrow2392(__unit: None=None) -> str:
        object_arg: IRequiredGetter = get.Required
        return object_arg.Field("Identifier", string)

    def _arrow2393(__unit: None=None) -> str | None:
        object_arg_1: IOptionalGetter = get.Optional
        return object_arg_1.Field("Title", string)

    def _arrow2394(__unit: None=None) -> str | None:
        object_arg_2: IOptionalGetter = get.Optional
        return object_arg_2.Field("Description", string)

    def _arrow2395(__unit: None=None) -> OntologyAnnotation | None:
        object_arg_3: IOptionalGetter = get.Optional
        return object_arg_3.Field("MeasurementType", OntologyAnnotation_decoder)

    def _arrow2396(__unit: None=None) -> OntologyAnnotation | None:
        object_arg_4: IOptionalGetter = get.Optional
        return object_arg_4.Field("TechnologyType", OntologyAnnotation_decoder)

    def _arrow2397(__unit: None=None) -> OntologyAnnotation | None:
        object_arg_5: IOptionalGetter = get.Optional
        return object_arg_5.Field("TechnologyPlatform", OntologyAnnotation_decoder)

    def _arrow2398(__unit: None=None) -> Array[ArcTable] | None:
        arg_13: Decoder_1[Array[ArcTable]] = resize_array(decoder_1)
        object_arg_6: IOptionalGetter = get.Optional
        return object_arg_6.Field("Tables", arg_13)

    def _arrow2399(__unit: None=None) -> DataMap | None:
        object_arg_7: IOptionalGetter = get.Optional
        return object_arg_7.Field("DataMap", decoder_2)

    def _arrow2400(__unit: None=None) -> Array[Person] | None:
        arg_17: Decoder_1[Array[Person]] = resize_array(decoder_3)
        object_arg_8: IOptionalGetter = get.Optional
        return object_arg_8.Field("Performers", arg_17)

    def _arrow2401(__unit: None=None) -> Array[Comment] | None:
        arg_19: Decoder_1[Array[Comment]] = resize_array(decoder_4)
        object_arg_9: IOptionalGetter = get.Optional
        return object_arg_9.Field("Comments", arg_19)

    return ArcAssay.create(_arrow2392(), _arrow2393(), _arrow2394(), _arrow2395(), _arrow2396(), _arrow2397(), _arrow2398(), _arrow2399(), _arrow2400(), _arrow2401())


decoder: Decoder_1[ArcAssay] = object(_arrow2402)

def encoder_compressed(string_table: Any, oa_table: Any, cell_table: Any, assay: ArcAssay) -> IEncodable:
    def chooser(tupled_arg: tuple[str, IEncodable | None], string_table: Any=string_table, oa_table: Any=oa_table, cell_table: Any=cell_table, assay: Any=assay) -> tuple[str, IEncodable] | None:
        def mapping(v_1: IEncodable, tupled_arg: Any=tupled_arg) -> tuple[str, IEncodable]:
            return (tupled_arg[0], v_1)

        return map(mapping, tupled_arg[1])

    def _arrow2406(__unit: None=None, string_table: Any=string_table, oa_table: Any=oa_table, cell_table: Any=cell_table, assay: Any=assay) -> IEncodable:
        value: str = assay.Identifier
        class ObjectExpr2405(IEncodable):
            def Encode(self, helpers: IEncoderHelpers_1[Any]) -> Any:
                return helpers.encode_string(value)

        return ObjectExpr2405()

    def _arrow2408(value_1: str, string_table: Any=string_table, oa_table: Any=oa_table, cell_table: Any=cell_table, assay: Any=assay) -> IEncodable:
        class ObjectExpr2407(IEncodable):
            def Encode(self, helpers_1: IEncoderHelpers_1[Any]) -> Any:
                return helpers_1.encode_string(value_1)

        return ObjectExpr2407()

    def _arrow2410(value_3: str, string_table: Any=string_table, oa_table: Any=oa_table, cell_table: Any=cell_table, assay: Any=assay) -> IEncodable:
        class ObjectExpr2409(IEncodable):
            def Encode(self, helpers_2: IEncoderHelpers_1[Any]) -> Any:
                return helpers_2.encode_string(value_3)

        return ObjectExpr2409()

    def _arrow2411(oa: OntologyAnnotation, string_table: Any=string_table, oa_table: Any=oa_table, cell_table: Any=cell_table, assay: Any=assay) -> IEncodable:
        return OntologyAnnotation_encoder(oa)

    def _arrow2412(oa_1: OntologyAnnotation, string_table: Any=string_table, oa_table: Any=oa_table, cell_table: Any=cell_table, assay: Any=assay) -> IEncodable:
        return OntologyAnnotation_encoder(oa_1)

    def _arrow2413(oa_2: OntologyAnnotation, string_table: Any=string_table, oa_table: Any=oa_table, cell_table: Any=cell_table, assay: Any=assay) -> IEncodable:
        return OntologyAnnotation_encoder(oa_2)

    def _arrow2414(table: ArcTable, string_table: Any=string_table, oa_table: Any=oa_table, cell_table: Any=cell_table, assay: Any=assay) -> IEncodable:
        return encoder_compressed_1(string_table, oa_table, cell_table, table)

    def _arrow2415(dm: DataMap, string_table: Any=string_table, oa_table: Any=oa_table, cell_table: Any=cell_table, assay: Any=assay) -> IEncodable:
        return encoder_compressed_2(string_table, oa_table, cell_table, dm)

    def _arrow2416(person: Person, string_table: Any=string_table, oa_table: Any=oa_table, cell_table: Any=cell_table, assay: Any=assay) -> IEncodable:
        return encoder_6(person)

    def _arrow2417(comment: Comment, string_table: Any=string_table, oa_table: Any=oa_table, cell_table: Any=cell_table, assay: Any=assay) -> IEncodable:
        return encoder_7(comment)

    values: FSharpList[tuple[str, IEncodable]] = choose(chooser, of_array([("Identifier", _arrow2406()), try_include("Title", _arrow2408, assay.Title), try_include("Description", _arrow2410, assay.Description), try_include("MeasurementType", _arrow2411, assay.MeasurementType), try_include("TechnologyType", _arrow2412, assay.TechnologyType), try_include("TechnologyPlatform", _arrow2413, assay.TechnologyPlatform), try_include_seq("Tables", _arrow2414, assay.Tables), try_include("DataMap", _arrow2415, assay.DataMap), try_include_seq("Performers", _arrow2416, assay.Performers), try_include_seq("Comments", _arrow2417, assay.Comments)]))
    class ObjectExpr2418(IEncodable):
        def Encode(self, helpers_3: IEncoderHelpers_1[Any], string_table: Any=string_table, oa_table: Any=oa_table, cell_table: Any=cell_table, assay: Any=assay) -> Any:
            def mapping_1(tupled_arg_1: tuple[str, IEncodable]) -> tuple[str, __A_]:
                return (tupled_arg_1[0], tupled_arg_1[1].Encode(helpers_3))

            arg: IEnumerable_1[tuple[str, __A_]] = map_1(mapping_1, values)
            return helpers_3.encode_object(arg)

    return ObjectExpr2418()


def decoder_compressed(string_table: Array[str], oa_table: Array[OntologyAnnotation], cell_table: Array[CompositeCell]) -> Decoder_1[ArcAssay]:
    def _arrow2429(get: IGetters, string_table: Any=string_table, oa_table: Any=oa_table, cell_table: Any=cell_table) -> ArcAssay:
        def _arrow2419(__unit: None=None) -> str:
            object_arg: IRequiredGetter = get.Required
            return object_arg.Field("Identifier", string)

        def _arrow2420(__unit: None=None) -> str | None:
            object_arg_1: IOptionalGetter = get.Optional
            return object_arg_1.Field("Title", string)

        def _arrow2421(__unit: None=None) -> str | None:
            object_arg_2: IOptionalGetter = get.Optional
            return object_arg_2.Field("Description", string)

        def _arrow2422(__unit: None=None) -> OntologyAnnotation | None:
            object_arg_3: IOptionalGetter = get.Optional
            return object_arg_3.Field("MeasurementType", OntologyAnnotation_decoder)

        def _arrow2423(__unit: None=None) -> OntologyAnnotation | None:
            object_arg_4: IOptionalGetter = get.Optional
            return object_arg_4.Field("TechnologyType", OntologyAnnotation_decoder)

        def _arrow2424(__unit: None=None) -> OntologyAnnotation | None:
            object_arg_5: IOptionalGetter = get.Optional
            return object_arg_5.Field("TechnologyPlatform", OntologyAnnotation_decoder)

        def _arrow2425(__unit: None=None) -> Array[ArcTable] | None:
            arg_13: Decoder_1[Array[ArcTable]] = resize_array(decoder_compressed_1(string_table, oa_table, cell_table))
            object_arg_6: IOptionalGetter = get.Optional
            return object_arg_6.Field("Tables", arg_13)

        def _arrow2426(__unit: None=None) -> DataMap | None:
            arg_15: Decoder_1[DataMap] = decoder_compressed_2(string_table, oa_table, cell_table)
            object_arg_7: IOptionalGetter = get.Optional
            return object_arg_7.Field("DataMap", arg_15)

        def _arrow2427(__unit: None=None) -> Array[Person] | None:
            arg_17: Decoder_1[Array[Person]] = resize_array(decoder_3)
            object_arg_8: IOptionalGetter = get.Optional
            return object_arg_8.Field("Performers", arg_17)

        def _arrow2428(__unit: None=None) -> Array[Comment] | None:
            arg_19: Decoder_1[Array[Comment]] = resize_array(decoder_4)
            object_arg_9: IOptionalGetter = get.Optional
            return object_arg_9.Field("Comments", arg_19)

        return ArcAssay.create(_arrow2419(), _arrow2420(), _arrow2421(), _arrow2422(), _arrow2423(), _arrow2424(), _arrow2425(), _arrow2426(), _arrow2427(), _arrow2428())

    return object(_arrow2429)


def ROCrate_genID(a: ArcAssay) -> str:
    match_value: str = a.Identifier
    if match_value == "":
        return "#EmptyAssay"

    else: 
        return ("assays/" + replace(match_value, " ", "_")) + "/"



def ROCrate_encoder(assay_name: str | None, a: ArcAssay) -> IEncodable:
    file_name: str = Assay_fileNameFromIdentifier(a.Identifier)
    processes: FSharpList[Process] = ARCtrl_ArcTables__ArcTables_GetProcesses(a)
    data_files: FSharpList[Data] = get_data(processes)
    def chooser(tupled_arg: tuple[str, IEncodable | None], assay_name: Any=assay_name, a: Any=a) -> tuple[str, IEncodable] | None:
        def mapping(v_1: IEncodable, tupled_arg: Any=tupled_arg) -> tuple[str, IEncodable]:
            return (tupled_arg[0], v_1)

        return map(mapping, tupled_arg[1])

    def _arrow2433(__unit: None=None, assay_name: Any=assay_name, a: Any=a) -> IEncodable:
        value: str = ROCrate_genID(a)
        class ObjectExpr2432(IEncodable):
            def Encode(self, helpers: IEncoderHelpers_1[Any]) -> Any:
                return helpers.encode_string(value)

        return ObjectExpr2432()

    class ObjectExpr2434(IEncodable):
        def Encode(self, helpers_1: IEncoderHelpers_1[Any], assay_name: Any=assay_name, a: Any=a) -> Any:
            return helpers_1.encode_string("Assay")

    class ObjectExpr2435(IEncodable):
        def Encode(self, helpers_2: IEncoderHelpers_1[Any], assay_name: Any=assay_name, a: Any=a) -> Any:
            return helpers_2.encode_string("Assay")

    def _arrow2437(__unit: None=None, assay_name: Any=assay_name, a: Any=a) -> IEncodable:
        value_3: str = a.Identifier
        class ObjectExpr2436(IEncodable):
            def Encode(self, helpers_3: IEncoderHelpers_1[Any]) -> Any:
                return helpers_3.encode_string(value_3)

        return ObjectExpr2436()

    class ObjectExpr2438(IEncodable):
        def Encode(self, helpers_4: IEncoderHelpers_1[Any], assay_name: Any=assay_name, a: Any=a) -> Any:
            return helpers_4.encode_string(file_name)

    def _arrow2440(value_5: str, assay_name: Any=assay_name, a: Any=a) -> IEncodable:
        class ObjectExpr2439(IEncodable):
            def Encode(self, helpers_5: IEncoderHelpers_1[Any]) -> Any:
                return helpers_5.encode_string(value_5)

        return ObjectExpr2439()

    def _arrow2442(value_7: str, assay_name: Any=assay_name, a: Any=a) -> IEncodable:
        class ObjectExpr2441(IEncodable):
            def Encode(self, helpers_6: IEncoderHelpers_1[Any]) -> Any:
                return helpers_6.encode_string(value_7)

        return ObjectExpr2441()

    def _arrow2443(oa: OntologyAnnotation, assay_name: Any=assay_name, a: Any=a) -> IEncodable:
        return OntologyAnnotation_ROCrate_encoderPropertyValue(oa)

    def _arrow2444(oa_1: OntologyAnnotation, assay_name: Any=assay_name, a: Any=a) -> IEncodable:
        return OntologyAnnotation_ROCrate_encoderDefinedTerm(oa_1)

    def _arrow2445(oa_2: OntologyAnnotation, assay_name: Any=assay_name, a: Any=a) -> IEncodable:
        return OntologyAnnotation_ROCrate_encoderDefinedTerm(oa_2)

    def _arrow2446(oa_3: Person, assay_name: Any=assay_name, a: Any=a) -> IEncodable:
        return ROCrate_encoder_1(oa_3)

    def _arrow2447(oa_4: Data, assay_name: Any=assay_name, a: Any=a) -> IEncodable:
        return ROCrate_encoder_2(oa_4)

    def _arrow2449(__unit: None=None, assay_name: Any=assay_name, a: Any=a) -> Callable[[Process], IEncodable]:
        assay_name_1: str | None = a.Identifier
        def _arrow2448(oa_5: Process) -> IEncodable:
            return ROCrate_encoder_3(assay_name, assay_name_1, oa_5)

        return _arrow2448

    def _arrow2450(comment: Comment, assay_name: Any=assay_name, a: Any=a) -> IEncodable:
        return ROCrate_encoder_4(comment)

    values: FSharpList[tuple[str, IEncodable]] = choose(chooser, of_array([("@id", _arrow2433()), ("@type", list_1_1(singleton(ObjectExpr2434()))), ("additionalType", ObjectExpr2435()), ("identifier", _arrow2437()), ("filename", ObjectExpr2438()), try_include("title", _arrow2440, a.Title), try_include("description", _arrow2442, a.Description), try_include("measurementType", _arrow2443, a.MeasurementType), try_include("technologyType", _arrow2444, a.TechnologyType), try_include("technologyPlatform", _arrow2445, a.TechnologyPlatform), try_include_seq("performers", _arrow2446, a.Performers), try_include_list("dataFiles", _arrow2447, data_files), try_include_list("processSequence", _arrow2449(), processes), try_include_seq("comments", _arrow2450, a.Comments), ("@context", context_jsonvalue)]))
    class ObjectExpr2451(IEncodable):
        def Encode(self, helpers_7: IEncoderHelpers_1[Any], assay_name: Any=assay_name, a: Any=a) -> Any:
            def mapping_1(tupled_arg_1: tuple[str, IEncodable]) -> tuple[str, __A_]:
                return (tupled_arg_1[0], tupled_arg_1[1].Encode(helpers_7))

            arg: IEnumerable_1[tuple[str, __A_]] = map_1(mapping_1, values)
            return helpers_7.encode_object(arg)

    return ObjectExpr2451()


def _arrow2461(get: IGetters) -> ArcAssay:
    def _arrow2452(__unit: None=None) -> str | None:
        object_arg: IOptionalGetter = get.Optional
        return object_arg.Field("identifier", string)

    identifier: str = default_arg(_arrow2452(), create_missing_identifier())
    def mapping(arg_4: FSharpList[Process]) -> Array[ArcTable]:
        a: ArcTables = ARCtrl_ArcTables__ArcTables_fromProcesses_Static_62A3309D(arg_4)
        return a.Tables

    def _arrow2453(__unit: None=None) -> FSharpList[Process] | None:
        arg_3: Decoder_1[FSharpList[Process]] = list_1_2(ROCrate_decoder_1)
        object_arg_1: IOptionalGetter = get.Optional
        return object_arg_1.Field("processSequence", arg_3)

    tables: Array[ArcTable] | None = map(mapping, _arrow2453())
    def _arrow2454(__unit: None=None) -> str | None:
        object_arg_2: IOptionalGetter = get.Optional
        return object_arg_2.Field("title", string)

    def _arrow2455(__unit: None=None) -> str | None:
        object_arg_3: IOptionalGetter = get.Optional
        return object_arg_3.Field("description", string)

    def _arrow2456(__unit: None=None) -> OntologyAnnotation | None:
        object_arg_4: IOptionalGetter = get.Optional
        return object_arg_4.Field("measurementType", OntologyAnnotation_ROCrate_decoderPropertyValue)

    def _arrow2457(__unit: None=None) -> OntologyAnnotation | None:
        object_arg_5: IOptionalGetter = get.Optional
        return object_arg_5.Field("technologyType", OntologyAnnotation_ROCrate_decoderDefinedTerm)

    def _arrow2458(__unit: None=None) -> OntologyAnnotation | None:
        object_arg_6: IOptionalGetter = get.Optional
        return object_arg_6.Field("technologyPlatform", OntologyAnnotation_ROCrate_decoderDefinedTerm)

    def _arrow2459(__unit: None=None) -> Array[Person] | None:
        arg_16: Decoder_1[Array[Person]] = resize_array(ROCrate_decoder_2)
        object_arg_7: IOptionalGetter = get.Optional
        return object_arg_7.Field("performers", arg_16)

    def _arrow2460(__unit: None=None) -> Array[Comment] | None:
        arg_18: Decoder_1[Array[Comment]] = resize_array(ROCrate_decoder_3)
        object_arg_8: IOptionalGetter = get.Optional
        return object_arg_8.Field("comments", arg_18)

    return ArcAssay(identifier, _arrow2454(), _arrow2455(), _arrow2456(), _arrow2457(), _arrow2458(), tables, None, _arrow2459(), _arrow2460())


ROCrate_decoder: Decoder_1[ArcAssay] = object(_arrow2461)

def ISAJson_encoder(study_name: str | None, id_map: Any | None, a: ArcAssay) -> IEncodable:
    def f(a_1: ArcAssay, study_name: Any=study_name, id_map: Any=id_map, a: Any=a) -> IEncodable:
        file_name: str = Assay_fileNameFromIdentifier(a_1.Identifier)
        processes: FSharpList[Process] = ARCtrl_ArcTables__ArcTables_GetProcesses(a_1)
        def encoder_1(oa: OntologyAnnotation, a_1: Any=a_1) -> IEncodable:
            return OntologyAnnotation_ISAJson_encoder(id_map, oa)

        encoded_units: tuple[str, IEncodable | None] = try_include_list("unitCategories", encoder_1, get_units(processes))
        def encoder_2(value_1: MaterialAttribute, a_1: Any=a_1) -> IEncodable:
            return encoder_8(id_map, value_1)

        encoded_characteristics: tuple[str, IEncodable | None] = try_include_list("characteristicCategories", encoder_2, get_characteristics(processes))
        def _arrow2462(ps: FSharpList[Process], a_1: Any=a_1) -> IEncodable:
            return encoder_9(id_map, ps)

        encoded_materials: tuple[str, IEncodable | None] = try_include("materials", _arrow2462, Option_fromValueWithDefault(empty(), processes))
        def encoder_3(oa_1: Data, a_1: Any=a_1) -> IEncodable:
            return ISAJson_encoder_1(id_map, oa_1)

        encoced_data_files: tuple[str, IEncodable | None] = try_include_list("dataFiles", encoder_3, get_data(processes))
        units: FSharpList[OntologyAnnotation] = get_units(processes)
        def _arrow2465(__unit: None=None, a_1: Any=a_1) -> IEnumerable_1[Comment]:
            def _arrow2464(__unit: None=None) -> IEnumerable_1[Comment]:
                def _arrow2463(__unit: None=None) -> IEnumerable_1[Comment]:
                    return singleton_1(Comment.create("description", value_9(a_1.Description))) if (a_1.Description is not None) else empty_1()

                return append(singleton_1(Comment.create("title", value_9(a_1.Title))) if (a_1.Title is not None) else empty_1(), delay(_arrow2463))

            return append(a_1.Comments if (len(a_1.Comments) > 0) else empty_1(), delay(_arrow2464))

        comments: FSharpList[Comment] = to_list(delay(_arrow2465))
        def chooser(tupled_arg: tuple[str, IEncodable | None], a_1: Any=a_1) -> tuple[str, IEncodable] | None:
            def mapping_1(v_1: IEncodable, tupled_arg: Any=tupled_arg) -> tuple[str, IEncodable]:
                return (tupled_arg[0], v_1)

            return map(mapping_1, tupled_arg[1])

        class ObjectExpr2467(IEncodable):
            def Encode(self, helpers: IEncoderHelpers_1[Any], a_1: Any=a_1) -> Any:
                return helpers.encode_string(file_name)

        def _arrow2469(value_5: str, a_1: Any=a_1) -> IEncodable:
            class ObjectExpr2468(IEncodable):
                def Encode(self, helpers_1: IEncoderHelpers_1[Any]) -> Any:
                    return helpers_1.encode_string(value_5)

            return ObjectExpr2468()

        def _arrow2470(oa_2: OntologyAnnotation, a_1: Any=a_1) -> IEncodable:
            return OntologyAnnotation_ISAJson_encoder(id_map, oa_2)

        def _arrow2471(oa_3: OntologyAnnotation, a_1: Any=a_1) -> IEncodable:
            return OntologyAnnotation_ISAJson_encoder(id_map, oa_3)

        def _arrow2473(value_7: str, a_1: Any=a_1) -> IEncodable:
            class ObjectExpr2472(IEncodable):
                def Encode(self, helpers_2: IEncoderHelpers_1[Any]) -> Any:
                    return helpers_2.encode_string(value_7)

            return ObjectExpr2472()

        def mapping(tp: OntologyAnnotation, a_1: Any=a_1) -> str:
            return JsonTypes_composeTechnologyPlatform(tp)

        def _arrow2475(__unit: None=None, a_1: Any=a_1) -> Callable[[Process], IEncodable]:
            assay_name: str | None = a_1.Identifier
            def _arrow2474(oa_4: Process) -> IEncodable:
                return ISAJson_encoder_2(study_name, assay_name, id_map, oa_4)

            return _arrow2474

        def _arrow2476(comment: Comment, a_1: Any=a_1) -> IEncodable:
            return ISAJson_encoder_3(id_map, comment)

        values: FSharpList[tuple[str, IEncodable]] = choose(chooser, of_array([("filename", ObjectExpr2467()), try_include("@id", _arrow2469, ROCrate_genID(a_1)), try_include("measurementType", _arrow2470, a_1.MeasurementType), try_include("technologyType", _arrow2471, a_1.TechnologyType), try_include("technologyPlatform", _arrow2473, map(mapping, a_1.TechnologyPlatform)), encoced_data_files, encoded_materials, encoded_characteristics, encoded_units, try_include_list("processSequence", _arrow2475(), processes), try_include_seq("comments", _arrow2476, comments)]))
        class ObjectExpr2477(IEncodable):
            def Encode(self, helpers_3: IEncoderHelpers_1[Any], a_1: Any=a_1) -> Any:
                def mapping_2(tupled_arg_1: tuple[str, IEncodable]) -> tuple[str, __A_]:
                    return (tupled_arg_1[0], tupled_arg_1[1].Encode(helpers_3))

                arg: IEnumerable_1[tuple[str, __A_]] = map_1(mapping_2, values)
                return helpers_3.encode_object(arg)

        return ObjectExpr2477()

    if id_map is not None:
        def _arrow2478(a_2: ArcAssay, study_name: Any=study_name, id_map: Any=id_map, a: Any=a) -> str:
            return ROCrate_genID(a_2)

        return encode(_arrow2478, f, a, id_map)

    else: 
        return f(a)



ISAJson_allowedFields: FSharpList[str] = of_array(["@id", "filename", "measurementType", "technologyType", "technologyPlatform", "dataFiles", "materials", "characteristicCategories", "unitCategories", "processSequence", "comments", "@type", "@context"])

def _arrow2484(get: IGetters) -> ArcAssay:
    def _arrow2479(__unit: None=None) -> str | None:
        object_arg: IOptionalGetter = get.Optional
        return object_arg.Field("filename", string)

    identifier: str = default_arg(bind(Assay_tryIdentifierFromFileName, _arrow2479()), create_missing_identifier())
    def mapping(arg_4: FSharpList[Process]) -> Array[ArcTable]:
        a: ArcTables = ARCtrl_ArcTables__ArcTables_fromProcesses_Static_62A3309D(arg_4)
        return a.Tables

    def _arrow2480(__unit: None=None) -> FSharpList[Process] | None:
        arg_3: Decoder_1[FSharpList[Process]] = list_1_2(ISAJson_decoder_1)
        object_arg_1: IOptionalGetter = get.Optional
        return object_arg_1.Field("processSequence", arg_3)

    tables: Array[ArcTable] | None = map(mapping, _arrow2480())
    comments: Array[Comment] | None
    arg_6: Decoder_1[Array[Comment]] = resize_array(ISAJson_decoder_2)
    object_arg_2: IOptionalGetter = get.Optional
    comments = object_arg_2.Field("comments", arg_6)
    def binder(c: Array[Comment]) -> str | None:
        def chooser(x: Comment, c: Any=c) -> str | None:
            if (value_9(x.Name) == "title") if (x.Name is not None) else False:
                return x.Value

            else: 
                return None


        return try_pick(chooser, c)

    title: str | None = bind(binder, comments)
    def binder_1(c_1: Array[Comment]) -> str | None:
        def chooser_1(x_1: Comment, c_1: Any=c_1) -> str | None:
            if (value_9(x_1.Name) == "description") if (x_1.Name is not None) else False:
                return x_1.Value

            else: 
                return None


        return try_pick(chooser_1, c_1)

    description: str | None = bind(binder_1, comments)
    def binder_2(c_2: Array[Comment]) -> Array[Comment] | None:
        def f(x_2: Comment, c_2: Any=c_2) -> bool:
            if x_2.Name is None:
                return True

            elif value_9(x_2.Name) != "title":
                return value_9(x_2.Name) != "description"

            else: 
                return False


        match_value: Array[Comment] = ResizeArray_filter(f, c_2)
        if length(match_value) == 0:
            return None

        else: 
            return match_value


    comments_1: Array[Comment] | None = bind(binder_2, comments)
    def _arrow2481(__unit: None=None) -> OntologyAnnotation | None:
        object_arg_3: IOptionalGetter = get.Optional
        return object_arg_3.Field("measurementType", OntologyAnnotation_ISAJson_decoder)

    def _arrow2482(__unit: None=None) -> OntologyAnnotation | None:
        object_arg_4: IOptionalGetter = get.Optional
        return object_arg_4.Field("technologyType", OntologyAnnotation_ISAJson_decoder)

    def _arrow2483(__unit: None=None) -> OntologyAnnotation | None:
        arg_12: Decoder_1[OntologyAnnotation] = map_2(JsonTypes_decomposeTechnologyPlatform, string)
        object_arg_5: IOptionalGetter = get.Optional
        return object_arg_5.Field("technologyPlatform", arg_12)

    return ArcAssay(identifier, title, description, _arrow2481(), _arrow2482(), _arrow2483(), tables, None, None, comments_1)


ISAJson_decoder: Decoder_1[ArcAssay] = Decode_objectNoAdditionalProperties(ISAJson_allowedFields, _arrow2484)

__all__ = ["encoder", "decoder", "encoder_compressed", "decoder_compressed", "ROCrate_genID", "ROCrate_encoder", "ROCrate_decoder", "ISAJson_encoder", "ISAJson_allowedFields", "ISAJson_decoder"]

