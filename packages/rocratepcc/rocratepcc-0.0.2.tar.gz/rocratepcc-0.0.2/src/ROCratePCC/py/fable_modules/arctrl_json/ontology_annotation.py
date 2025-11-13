from __future__ import annotations
from collections.abc import Callable
from typing import (Any, TypeVar)
from ..arctrl_core.comment import Comment
from ..arctrl_core.ontology_annotation import OntologyAnnotation
from ..arctrl_core.Process.column_index import order_name
from ..arctrl_core.uri import URIModule_toString
from ..fable_library.list import (of_array, choose, FSharpList)
from ..fable_library.option import map as map_1
from ..fable_library.seq import (map as map_2, filter)
from ..fable_library.string_ import replace
from ..fable_library.types import (to_string, Array)
from ..fable_library.util import (int32_to_string, IEnumerable_1)
from ..thoth_json_core.decode import (one_of, map, int_1, float_1, string, object, IOptionalGetter, resize_array, IGetters)
from ..thoth_json_core.types import (Decoder_1, IEncodable, IEncoderHelpers_1)
from .comment import (encoder, decoder, ROCrate_encoderDisambiguatingDescription, ROCrate_decoderDisambiguatingDescription)
from .context.rocrate.isa_ontology_annotation_context import context_jsonvalue
from .context.rocrate.property_value_context import context_jsonvalue as context_jsonvalue_1
from .encode import (try_include, try_include_seq)
from .idtable import encode
from .string_table import (encode_string, decode_string)

__A_ = TypeVar("__A_")

AnnotationValue_decoder: Decoder_1[str] = one_of(of_array([map(int32_to_string, int_1), map(to_string, float_1), string]))

def OntologyAnnotation_encoder(oa: OntologyAnnotation) -> IEncodable:
    def chooser(tupled_arg: tuple[str, IEncodable | None], oa: Any=oa) -> tuple[str, IEncodable] | None:
        def mapping(v_1: IEncodable, tupled_arg: Any=tupled_arg) -> tuple[str, IEncodable]:
            return (tupled_arg[0], v_1)

        return map_1(mapping, tupled_arg[1])

    def _arrow1499(value: str, oa: Any=oa) -> IEncodable:
        class ObjectExpr1498(IEncodable):
            def Encode(self, helpers: IEncoderHelpers_1[Any]) -> Any:
                return helpers.encode_string(value)

        return ObjectExpr1498()

    def _arrow1501(value_2: str, oa: Any=oa) -> IEncodable:
        class ObjectExpr1500(IEncodable):
            def Encode(self, helpers_1: IEncoderHelpers_1[Any]) -> Any:
                return helpers_1.encode_string(value_2)

        return ObjectExpr1500()

    def _arrow1503(value_4: str, oa: Any=oa) -> IEncodable:
        class ObjectExpr1502(IEncodable):
            def Encode(self, helpers_2: IEncoderHelpers_1[Any]) -> Any:
                return helpers_2.encode_string(value_4)

        return ObjectExpr1502()

    def _arrow1504(comment: Comment, oa: Any=oa) -> IEncodable:
        return encoder(comment)

    values: FSharpList[tuple[str, IEncodable]] = choose(chooser, of_array([try_include("annotationValue", _arrow1499, oa.Name), try_include("termSource", _arrow1501, oa.TermSourceREF), try_include("termAccession", _arrow1503, oa.TermAccessionNumber), try_include_seq("comments", _arrow1504, oa.Comments)]))
    class ObjectExpr1505(IEncodable):
        def Encode(self, helpers_3: IEncoderHelpers_1[Any], oa: Any=oa) -> Any:
            def mapping_1(tupled_arg_1: tuple[str, IEncodable]) -> tuple[str, __A_]:
                return (tupled_arg_1[0], tupled_arg_1[1].Encode(helpers_3))

            arg: IEnumerable_1[tuple[str, __A_]] = map_2(mapping_1, values)
            return helpers_3.encode_object(arg)

    return ObjectExpr1505()


def _arrow1510(get: IGetters) -> OntologyAnnotation:
    def _arrow1506(__unit: None=None) -> str | None:
        object_arg: IOptionalGetter = get.Optional
        return object_arg.Field("annotationValue", AnnotationValue_decoder)

    def _arrow1507(__unit: None=None) -> str | None:
        object_arg_1: IOptionalGetter = get.Optional
        return object_arg_1.Field("termSource", string)

    def _arrow1508(__unit: None=None) -> str | None:
        object_arg_2: IOptionalGetter = get.Optional
        return object_arg_2.Field("termAccession", string)

    def _arrow1509(__unit: None=None) -> Array[Comment] | None:
        arg_7: Decoder_1[Array[Comment]] = resize_array(decoder)
        object_arg_3: IOptionalGetter = get.Optional
        return object_arg_3.Field("comments", arg_7)

    return OntologyAnnotation.create(_arrow1506(), _arrow1507(), _arrow1508(), _arrow1509())


OntologyAnnotation_decoder: Decoder_1[OntologyAnnotation] = object(_arrow1510)

def OntologyAnnotation_compressedEncoder(string_table: Any, oa: OntologyAnnotation) -> IEncodable:
    def chooser(tupled_arg: tuple[str, IEncodable | None], string_table: Any=string_table, oa: Any=oa) -> tuple[str, IEncodable] | None:
        def mapping(v_1: IEncodable, tupled_arg: Any=tupled_arg) -> tuple[str, IEncodable]:
            return (tupled_arg[0], v_1)

        return map_1(mapping, tupled_arg[1])

    def _arrow1512(s: str, string_table: Any=string_table, oa: Any=oa) -> IEncodable:
        return encode_string(string_table, s)

    def _arrow1513(s_1: str, string_table: Any=string_table, oa: Any=oa) -> IEncodable:
        return encode_string(string_table, s_1)

    def _arrow1514(s_2: str, string_table: Any=string_table, oa: Any=oa) -> IEncodable:
        return encode_string(string_table, s_2)

    def _arrow1515(comment: Comment, string_table: Any=string_table, oa: Any=oa) -> IEncodable:
        return encoder(comment)

    values: FSharpList[tuple[str, IEncodable]] = choose(chooser, of_array([try_include("a", _arrow1512, oa.Name), try_include("ts", _arrow1513, oa.TermSourceREF), try_include("ta", _arrow1514, oa.TermAccessionNumber), try_include_seq("comments", _arrow1515, oa.Comments)]))
    class ObjectExpr1516(IEncodable):
        def Encode(self, helpers: IEncoderHelpers_1[Any], string_table: Any=string_table, oa: Any=oa) -> Any:
            def mapping_1(tupled_arg_1: tuple[str, IEncodable]) -> tuple[str, __A_]:
                return (tupled_arg_1[0], tupled_arg_1[1].Encode(helpers))

            arg: IEnumerable_1[tuple[str, __A_]] = map_2(mapping_1, values)
            return helpers.encode_object(arg)

    return ObjectExpr1516()


def OntologyAnnotation_compressedDecoder(string_table: Array[str]) -> Decoder_1[OntologyAnnotation]:
    def _arrow1521(get: IGetters, string_table: Any=string_table) -> OntologyAnnotation:
        def _arrow1517(__unit: None=None) -> str | None:
            arg_1: Decoder_1[str] = decode_string(string_table)
            object_arg: IOptionalGetter = get.Optional
            return object_arg.Field("a", arg_1)

        def _arrow1518(__unit: None=None) -> str | None:
            arg_3: Decoder_1[str] = decode_string(string_table)
            object_arg_1: IOptionalGetter = get.Optional
            return object_arg_1.Field("ts", arg_3)

        def _arrow1519(__unit: None=None) -> str | None:
            arg_5: Decoder_1[str] = decode_string(string_table)
            object_arg_2: IOptionalGetter = get.Optional
            return object_arg_2.Field("ta", arg_5)

        def _arrow1520(__unit: None=None) -> Array[Comment] | None:
            arg_7: Decoder_1[Array[Comment]] = resize_array(decoder)
            object_arg_3: IOptionalGetter = get.Optional
            return object_arg_3.Field("comments", arg_7)

        return OntologyAnnotation(_arrow1517(), _arrow1518(), _arrow1519(), _arrow1520())

    return object(_arrow1521)


def OntologyAnnotation_ROCrate_genID(o: OntologyAnnotation) -> str:
    match_value: str | None = o.TermAccessionNumber
    if match_value is None:
        match_value_1: str | None = o.TermSourceREF
        if match_value_1 is None:
            match_value_2: str | None = o.Name
            if match_value_2 is None:
                return "#DummyOntologyAnnotation"

            else: 
                return "#UserTerm_" + replace(match_value_2, " ", "_")


        else: 
            return "#" + replace(match_value_1, " ", "_")


    else: 
        return URIModule_toString(match_value)



def OntologyAnnotation_ROCrate_encoderDefinedTerm(oa: OntologyAnnotation) -> IEncodable:
    def chooser(tupled_arg: tuple[str, IEncodable | None], oa: Any=oa) -> tuple[str, IEncodable] | None:
        def mapping(v_1: IEncodable, tupled_arg: Any=tupled_arg) -> tuple[str, IEncodable]:
            return (tupled_arg[0], v_1)

        return map_1(mapping, tupled_arg[1])

    def _arrow1525(__unit: None=None, oa: Any=oa) -> IEncodable:
        value: str = OntologyAnnotation_ROCrate_genID(oa)
        class ObjectExpr1524(IEncodable):
            def Encode(self, helpers: IEncoderHelpers_1[Any]) -> Any:
                return helpers.encode_string(value)

        return ObjectExpr1524()

    class ObjectExpr1526(IEncodable):
        def Encode(self, helpers_1: IEncoderHelpers_1[Any], oa: Any=oa) -> Any:
            return helpers_1.encode_string("OntologyAnnotation")

    def _arrow1528(value_2: str, oa: Any=oa) -> IEncodable:
        class ObjectExpr1527(IEncodable):
            def Encode(self, helpers_2: IEncoderHelpers_1[Any]) -> Any:
                return helpers_2.encode_string(value_2)

        return ObjectExpr1527()

    def _arrow1530(value_4: str, oa: Any=oa) -> IEncodable:
        class ObjectExpr1529(IEncodable):
            def Encode(self, helpers_3: IEncoderHelpers_1[Any]) -> Any:
                return helpers_3.encode_string(value_4)

        return ObjectExpr1529()

    def _arrow1532(value_6: str, oa: Any=oa) -> IEncodable:
        class ObjectExpr1531(IEncodable):
            def Encode(self, helpers_4: IEncoderHelpers_1[Any]) -> Any:
                return helpers_4.encode_string(value_6)

        return ObjectExpr1531()

    def _arrow1533(comment: Comment, oa: Any=oa) -> IEncodable:
        return ROCrate_encoderDisambiguatingDescription(comment)

    values: FSharpList[tuple[str, IEncodable]] = choose(chooser, of_array([("@id", _arrow1525()), ("@type", ObjectExpr1526()), try_include("annotationValue", _arrow1528, oa.Name), try_include("termSource", _arrow1530, oa.TermSourceREF), try_include("termAccession", _arrow1532, oa.TermAccessionNumber), try_include_seq("comments", _arrow1533, oa.Comments), ("@context", context_jsonvalue)]))
    class ObjectExpr1534(IEncodable):
        def Encode(self, helpers_5: IEncoderHelpers_1[Any], oa: Any=oa) -> Any:
            def mapping_1(tupled_arg_1: tuple[str, IEncodable]) -> tuple[str, __A_]:
                return (tupled_arg_1[0], tupled_arg_1[1].Encode(helpers_5))

            arg: IEnumerable_1[tuple[str, __A_]] = map_2(mapping_1, values)
            return helpers_5.encode_object(arg)

    return ObjectExpr1534()


def _arrow1539(get: IGetters) -> OntologyAnnotation:
    def _arrow1535(__unit: None=None) -> str | None:
        object_arg: IOptionalGetter = get.Optional
        return object_arg.Field("annotationValue", AnnotationValue_decoder)

    def _arrow1536(__unit: None=None) -> str | None:
        object_arg_1: IOptionalGetter = get.Optional
        return object_arg_1.Field("termSource", string)

    def _arrow1537(__unit: None=None) -> str | None:
        object_arg_2: IOptionalGetter = get.Optional
        return object_arg_2.Field("termAccession", string)

    def _arrow1538(__unit: None=None) -> Array[Comment] | None:
        arg_7: Decoder_1[Array[Comment]] = resize_array(ROCrate_decoderDisambiguatingDescription)
        object_arg_3: IOptionalGetter = get.Optional
        return object_arg_3.Field("comments", arg_7)

    return OntologyAnnotation.create(_arrow1535(), _arrow1536(), _arrow1537(), _arrow1538())


OntologyAnnotation_ROCrate_decoderDefinedTerm: Decoder_1[OntologyAnnotation] = object(_arrow1539)

def OntologyAnnotation_ROCrate_encoderPropertyValue(oa: OntologyAnnotation) -> IEncodable:
    def chooser(tupled_arg: tuple[str, IEncodable | None], oa: Any=oa) -> tuple[str, IEncodable] | None:
        def mapping(v_1: IEncodable, tupled_arg: Any=tupled_arg) -> tuple[str, IEncodable]:
            return (tupled_arg[0], v_1)

        return map_1(mapping, tupled_arg[1])

    def _arrow1543(__unit: None=None, oa: Any=oa) -> IEncodable:
        value: str = OntologyAnnotation_ROCrate_genID(oa)
        class ObjectExpr1542(IEncodable):
            def Encode(self, helpers: IEncoderHelpers_1[Any]) -> Any:
                return helpers.encode_string(value)

        return ObjectExpr1542()

    class ObjectExpr1544(IEncodable):
        def Encode(self, helpers_1: IEncoderHelpers_1[Any], oa: Any=oa) -> Any:
            return helpers_1.encode_string("PropertyValue")

    def _arrow1546(value_2: str, oa: Any=oa) -> IEncodable:
        class ObjectExpr1545(IEncodable):
            def Encode(self, helpers_2: IEncoderHelpers_1[Any]) -> Any:
                return helpers_2.encode_string(value_2)

        return ObjectExpr1545()

    def _arrow1548(value_4: str, oa: Any=oa) -> IEncodable:
        class ObjectExpr1547(IEncodable):
            def Encode(self, helpers_3: IEncoderHelpers_1[Any]) -> Any:
                return helpers_3.encode_string(value_4)

        return ObjectExpr1547()

    def _arrow1549(comment: Comment, oa: Any=oa) -> IEncodable:
        return ROCrate_encoderDisambiguatingDescription(comment)

    values: FSharpList[tuple[str, IEncodable]] = choose(chooser, of_array([("@id", _arrow1543()), ("@type", ObjectExpr1544()), try_include("category", _arrow1546, oa.Name), try_include("categoryCode", _arrow1548, oa.TermAccessionNumber), try_include_seq("comments", _arrow1549, oa.Comments), ("@context", context_jsonvalue_1)]))
    class ObjectExpr1550(IEncodable):
        def Encode(self, helpers_4: IEncoderHelpers_1[Any], oa: Any=oa) -> Any:
            def mapping_1(tupled_arg_1: tuple[str, IEncodable]) -> tuple[str, __A_]:
                return (tupled_arg_1[0], tupled_arg_1[1].Encode(helpers_4))

            arg: IEnumerable_1[tuple[str, __A_]] = map_2(mapping_1, values)
            return helpers_4.encode_object(arg)

    return ObjectExpr1550()


def _arrow1554(get: IGetters) -> OntologyAnnotation:
    def _arrow1551(__unit: None=None) -> str | None:
        object_arg: IOptionalGetter = get.Optional
        return object_arg.Field("category", string)

    def _arrow1552(__unit: None=None) -> str | None:
        object_arg_1: IOptionalGetter = get.Optional
        return object_arg_1.Field("categoryCode", string)

    def _arrow1553(__unit: None=None) -> Array[Comment] | None:
        arg_5: Decoder_1[Array[Comment]] = resize_array(ROCrate_decoderDisambiguatingDescription)
        object_arg_2: IOptionalGetter = get.Optional
        return object_arg_2.Field("comments", arg_5)

    return OntologyAnnotation.create(_arrow1551(), None, _arrow1552(), _arrow1553())


OntologyAnnotation_ROCrate_decoderPropertyValue: Decoder_1[OntologyAnnotation] = object(_arrow1554)

def OntologyAnnotation_ISAJson_encoder(id_map: Any | None, oa: OntologyAnnotation) -> IEncodable:
    def f(oa_1: OntologyAnnotation, id_map: Any=id_map, oa: Any=oa) -> IEncodable:
        def predicate(c: Comment, oa_1: Any=oa_1) -> bool:
            match_value: str | None = c.Name
            (pattern_matching_result,) = (None,)
            if match_value is not None:
                if match_value == order_name:
                    pattern_matching_result = 0

                else: 
                    pattern_matching_result = 1


            else: 
                pattern_matching_result = 1

            if pattern_matching_result == 0:
                return False

            elif pattern_matching_result == 1:
                return True


        comments: IEnumerable_1[Comment] = filter(predicate, oa_1.Comments)
        def chooser(tupled_arg: tuple[str, IEncodable | None], oa_1: Any=oa_1) -> tuple[str, IEncodable] | None:
            def mapping(v_1: IEncodable, tupled_arg: Any=tupled_arg) -> tuple[str, IEncodable]:
                return (tupled_arg[0], v_1)

            return map_1(mapping, tupled_arg[1])

        def _arrow1558(value: str, oa_1: Any=oa_1) -> IEncodable:
            class ObjectExpr1557(IEncodable):
                def Encode(self, helpers: IEncoderHelpers_1[Any]) -> Any:
                    return helpers.encode_string(value)

            return ObjectExpr1557()

        def _arrow1561(value_2: str, oa_1: Any=oa_1) -> IEncodable:
            class ObjectExpr1560(IEncodable):
                def Encode(self, helpers_1: IEncoderHelpers_1[Any]) -> Any:
                    return helpers_1.encode_string(value_2)

            return ObjectExpr1560()

        def _arrow1564(value_4: str, oa_1: Any=oa_1) -> IEncodable:
            class ObjectExpr1563(IEncodable):
                def Encode(self, helpers_2: IEncoderHelpers_1[Any]) -> Any:
                    return helpers_2.encode_string(value_4)

            return ObjectExpr1563()

        def _arrow1568(value_6: str, oa_1: Any=oa_1) -> IEncodable:
            class ObjectExpr1567(IEncodable):
                def Encode(self, helpers_3: IEncoderHelpers_1[Any]) -> Any:
                    return helpers_3.encode_string(value_6)

            return ObjectExpr1567()

        def _arrow1571(comment: Comment, oa_1: Any=oa_1) -> IEncodable:
            return encoder(comment)

        values: FSharpList[tuple[str, IEncodable]] = choose(chooser, of_array([try_include("@id", _arrow1558, OntologyAnnotation_ROCrate_genID(oa_1)), try_include("annotationValue", _arrow1561, oa_1.Name), try_include("termSource", _arrow1564, oa_1.TermSourceREF), try_include("termAccession", _arrow1568, oa_1.TermAccessionNumber), try_include_seq("comments", _arrow1571, comments)]))
        class ObjectExpr1573(IEncodable):
            def Encode(self, helpers_4: IEncoderHelpers_1[Any], oa_1: Any=oa_1) -> Any:
                def mapping_1(tupled_arg_1: tuple[str, IEncodable]) -> tuple[str, __A_]:
                    return (tupled_arg_1[0], tupled_arg_1[1].Encode(helpers_4))

                arg: IEnumerable_1[tuple[str, __A_]] = map_2(mapping_1, values)
                return helpers_4.encode_object(arg)

        return ObjectExpr1573()

    if id_map is not None:
        def _arrow1574(o: OntologyAnnotation, id_map: Any=id_map, oa: Any=oa) -> str:
            return OntologyAnnotation_ROCrate_genID(o)

        return encode(_arrow1574, f, oa, id_map)

    else: 
        return f(oa)



OntologyAnnotation_ISAJson_decoder: Decoder_1[OntologyAnnotation] = OntologyAnnotation_decoder

__all__ = ["AnnotationValue_decoder", "OntologyAnnotation_encoder", "OntologyAnnotation_decoder", "OntologyAnnotation_compressedEncoder", "OntologyAnnotation_compressedDecoder", "OntologyAnnotation_ROCrate_genID", "OntologyAnnotation_ROCrate_encoderDefinedTerm", "OntologyAnnotation_ROCrate_decoderDefinedTerm", "OntologyAnnotation_ROCrate_encoderPropertyValue", "OntologyAnnotation_ROCrate_decoderPropertyValue", "OntologyAnnotation_ISAJson_encoder", "OntologyAnnotation_ISAJson_decoder"]

