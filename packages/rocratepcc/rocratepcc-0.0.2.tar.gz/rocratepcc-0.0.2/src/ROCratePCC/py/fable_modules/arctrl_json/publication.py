from __future__ import annotations
from typing import (Any, TypeVar)
from ..arctrl_core.comment import Comment
from ..arctrl_core.ontology_annotation import OntologyAnnotation
from ..arctrl_core.publication import Publication
from ..fable_library.list import (choose, of_array, FSharpList)
from ..fable_library.option import map
from ..fable_library.seq import map as map_1
from ..fable_library.string_ import replace
from ..fable_library.types import Array
from ..fable_library.util import IEnumerable_1
from ..thoth_json_core.decode import (object, IOptionalGetter, string, resize_array, IGetters)
from ..thoth_json_core.types import (IEncodable, IEncoderHelpers_1, Decoder_1)
from .comment import (encoder as encoder_1, decoder as decoder_2, ROCrate_encoderDisambiguatingDescription, ROCrate_decoderDisambiguatingDescription, ISAJson_encoder as ISAJson_encoder_1)
from .context.rocrate.isa_publication_context import context_jsonvalue
from .decode import (Decode_uri, Decode_noAdditionalProperties)
from .encode import (try_include, try_include_seq)
from .ontology_annotation import (OntologyAnnotation_encoder, OntologyAnnotation_decoder, OntologyAnnotation_ROCrate_encoderDefinedTerm, OntologyAnnotation_ROCrate_decoderDefinedTerm)
from .person import (ROCrate_encodeAuthorListString, ROCrate_decodeAuthorListString)

__A_ = TypeVar("__A_")

def encoder(oa: Publication) -> IEncodable:
    def chooser(tupled_arg: tuple[str, IEncodable | None], oa: Any=oa) -> tuple[str, IEncodable] | None:
        def mapping(v_1: IEncodable, tupled_arg: Any=tupled_arg) -> tuple[str, IEncodable]:
            return (tupled_arg[0], v_1)

        return map(mapping, tupled_arg[1])

    def _arrow1735(value: str, oa: Any=oa) -> IEncodable:
        class ObjectExpr1734(IEncodable):
            def Encode(self, helpers: IEncoderHelpers_1[Any]) -> Any:
                return helpers.encode_string(value)

        return ObjectExpr1734()

    def _arrow1737(value_2: str, oa: Any=oa) -> IEncodable:
        class ObjectExpr1736(IEncodable):
            def Encode(self, helpers_1: IEncoderHelpers_1[Any]) -> Any:
                return helpers_1.encode_string(value_2)

        return ObjectExpr1736()

    def _arrow1739(value_4: str, oa: Any=oa) -> IEncodable:
        class ObjectExpr1738(IEncodable):
            def Encode(self, helpers_2: IEncoderHelpers_1[Any]) -> Any:
                return helpers_2.encode_string(value_4)

        return ObjectExpr1738()

    def _arrow1741(value_6: str, oa: Any=oa) -> IEncodable:
        class ObjectExpr1740(IEncodable):
            def Encode(self, helpers_3: IEncoderHelpers_1[Any]) -> Any:
                return helpers_3.encode_string(value_6)

        return ObjectExpr1740()

    def _arrow1742(oa_1: OntologyAnnotation, oa: Any=oa) -> IEncodable:
        return OntologyAnnotation_encoder(oa_1)

    def _arrow1743(comment: Comment, oa: Any=oa) -> IEncodable:
        return encoder_1(comment)

    values: FSharpList[tuple[str, IEncodable]] = choose(chooser, of_array([try_include("pubMedID", _arrow1735, oa.PubMedID), try_include("doi", _arrow1737, oa.DOI), try_include("authorList", _arrow1739, oa.Authors), try_include("title", _arrow1741, oa.Title), try_include("status", _arrow1742, oa.Status), try_include_seq("comments", _arrow1743, oa.Comments)]))
    class ObjectExpr1744(IEncodable):
        def Encode(self, helpers_4: IEncoderHelpers_1[Any], oa: Any=oa) -> Any:
            def mapping_1(tupled_arg_1: tuple[str, IEncodable]) -> tuple[str, __A_]:
                return (tupled_arg_1[0], tupled_arg_1[1].Encode(helpers_4))

            arg: IEnumerable_1[tuple[str, __A_]] = map_1(mapping_1, values)
            return helpers_4.encode_object(arg)

    return ObjectExpr1744()


def _arrow1751(get: IGetters) -> Publication:
    def _arrow1745(__unit: None=None) -> str | None:
        object_arg: IOptionalGetter = get.Optional
        return object_arg.Field("pubMedID", Decode_uri)

    def _arrow1746(__unit: None=None) -> str | None:
        object_arg_1: IOptionalGetter = get.Optional
        return object_arg_1.Field("doi", string)

    def _arrow1747(__unit: None=None) -> str | None:
        object_arg_2: IOptionalGetter = get.Optional
        return object_arg_2.Field("authorList", string)

    def _arrow1748(__unit: None=None) -> str | None:
        object_arg_3: IOptionalGetter = get.Optional
        return object_arg_3.Field("title", string)

    def _arrow1749(__unit: None=None) -> OntologyAnnotation | None:
        object_arg_4: IOptionalGetter = get.Optional
        return object_arg_4.Field("status", OntologyAnnotation_decoder)

    def _arrow1750(__unit: None=None) -> Array[Comment] | None:
        arg_11: Decoder_1[Array[Comment]] = resize_array(decoder_2)
        object_arg_5: IOptionalGetter = get.Optional
        return object_arg_5.Field("comments", arg_11)

    return Publication(_arrow1745(), _arrow1746(), _arrow1747(), _arrow1748(), _arrow1749(), _arrow1750())


decoder: Decoder_1[Publication] = object(_arrow1751)

def ROCrate_genID(p: Publication) -> str:
    match_value: str | None = p.DOI
    if match_value is None:
        match_value_1: str | None = p.PubMedID
        if match_value_1 is None:
            match_value_2: str | None = p.Title
            if match_value_2 is None:
                return "#EmptyPublication"

            else: 
                return "#Pub_" + replace(match_value_2, " ", "_")


        else: 
            return match_value_1


    else: 
        return match_value



def ROCrate_encoder(oa: Publication) -> IEncodable:
    def chooser(tupled_arg: tuple[str, IEncodable | None], oa: Any=oa) -> tuple[str, IEncodable] | None:
        def mapping(v_1: IEncodable, tupled_arg: Any=tupled_arg) -> tuple[str, IEncodable]:
            return (tupled_arg[0], v_1)

        return map(mapping, tupled_arg[1])

    def _arrow1755(__unit: None=None, oa: Any=oa) -> IEncodable:
        value: str = ROCrate_genID(oa)
        class ObjectExpr1754(IEncodable):
            def Encode(self, helpers: IEncoderHelpers_1[Any]) -> Any:
                return helpers.encode_string(value)

        return ObjectExpr1754()

    class ObjectExpr1756(IEncodable):
        def Encode(self, helpers_1: IEncoderHelpers_1[Any], oa: Any=oa) -> Any:
            return helpers_1.encode_string("Publication")

    def _arrow1758(value_2: str, oa: Any=oa) -> IEncodable:
        class ObjectExpr1757(IEncodable):
            def Encode(self, helpers_2: IEncoderHelpers_1[Any]) -> Any:
                return helpers_2.encode_string(value_2)

        return ObjectExpr1757()

    def _arrow1760(value_4: str, oa: Any=oa) -> IEncodable:
        class ObjectExpr1759(IEncodable):
            def Encode(self, helpers_3: IEncoderHelpers_1[Any]) -> Any:
                return helpers_3.encode_string(value_4)

        return ObjectExpr1759()

    def _arrow1761(author_list: str, oa: Any=oa) -> IEncodable:
        return ROCrate_encodeAuthorListString(author_list)

    def _arrow1763(value_6: str, oa: Any=oa) -> IEncodable:
        class ObjectExpr1762(IEncodable):
            def Encode(self, helpers_4: IEncoderHelpers_1[Any]) -> Any:
                return helpers_4.encode_string(value_6)

        return ObjectExpr1762()

    def _arrow1764(oa_1: OntologyAnnotation, oa: Any=oa) -> IEncodable:
        return OntologyAnnotation_ROCrate_encoderDefinedTerm(oa_1)

    def _arrow1765(comment: Comment, oa: Any=oa) -> IEncodable:
        return ROCrate_encoderDisambiguatingDescription(comment)

    values: FSharpList[tuple[str, IEncodable]] = choose(chooser, of_array([("@id", _arrow1755()), ("@type", ObjectExpr1756()), try_include("pubMedID", _arrow1758, oa.PubMedID), try_include("doi", _arrow1760, oa.DOI), try_include("authorList", _arrow1761, oa.Authors), try_include("title", _arrow1763, oa.Title), try_include("status", _arrow1764, oa.Status), try_include_seq("comments", _arrow1765, oa.Comments), ("@context", context_jsonvalue)]))
    class ObjectExpr1766(IEncodable):
        def Encode(self, helpers_5: IEncoderHelpers_1[Any], oa: Any=oa) -> Any:
            def mapping_1(tupled_arg_1: tuple[str, IEncodable]) -> tuple[str, __A_]:
                return (tupled_arg_1[0], tupled_arg_1[1].Encode(helpers_5))

            arg: IEnumerable_1[tuple[str, __A_]] = map_1(mapping_1, values)
            return helpers_5.encode_object(arg)

    return ObjectExpr1766()


def _arrow1773(get: IGetters) -> Publication:
    def _arrow1767(__unit: None=None) -> str | None:
        object_arg: IOptionalGetter = get.Optional
        return object_arg.Field("pubMedID", Decode_uri)

    def _arrow1768(__unit: None=None) -> str | None:
        object_arg_1: IOptionalGetter = get.Optional
        return object_arg_1.Field("doi", string)

    def _arrow1769(__unit: None=None) -> str | None:
        object_arg_2: IOptionalGetter = get.Optional
        return object_arg_2.Field("authorList", ROCrate_decodeAuthorListString)

    def _arrow1770(__unit: None=None) -> str | None:
        object_arg_3: IOptionalGetter = get.Optional
        return object_arg_3.Field("title", string)

    def _arrow1771(__unit: None=None) -> OntologyAnnotation | None:
        object_arg_4: IOptionalGetter = get.Optional
        return object_arg_4.Field("status", OntologyAnnotation_ROCrate_decoderDefinedTerm)

    def _arrow1772(__unit: None=None) -> Array[Comment] | None:
        arg_11: Decoder_1[Array[Comment]] = resize_array(ROCrate_decoderDisambiguatingDescription)
        object_arg_5: IOptionalGetter = get.Optional
        return object_arg_5.Field("comments", arg_11)

    return Publication(_arrow1767(), _arrow1768(), _arrow1769(), _arrow1770(), _arrow1771(), _arrow1772())


ROCrate_decoder: Decoder_1[Publication] = object(_arrow1773)

def ISAJson_encoder(id_map: Any | None, oa: Publication) -> IEncodable:
    def chooser(tupled_arg: tuple[str, IEncodable | None], id_map: Any=id_map, oa: Any=oa) -> tuple[str, IEncodable] | None:
        def mapping(v_1: IEncodable, tupled_arg: Any=tupled_arg) -> tuple[str, IEncodable]:
            return (tupled_arg[0], v_1)

        return map(mapping, tupled_arg[1])

    def _arrow1777(value: str, id_map: Any=id_map, oa: Any=oa) -> IEncodable:
        class ObjectExpr1776(IEncodable):
            def Encode(self, helpers: IEncoderHelpers_1[Any]) -> Any:
                return helpers.encode_string(value)

        return ObjectExpr1776()

    def _arrow1779(value_2: str, id_map: Any=id_map, oa: Any=oa) -> IEncodable:
        class ObjectExpr1778(IEncodable):
            def Encode(self, helpers_1: IEncoderHelpers_1[Any]) -> Any:
                return helpers_1.encode_string(value_2)

        return ObjectExpr1778()

    def _arrow1781(value_4: str, id_map: Any=id_map, oa: Any=oa) -> IEncodable:
        class ObjectExpr1780(IEncodable):
            def Encode(self, helpers_2: IEncoderHelpers_1[Any]) -> Any:
                return helpers_2.encode_string(value_4)

        return ObjectExpr1780()

    def _arrow1783(value_6: str, id_map: Any=id_map, oa: Any=oa) -> IEncodable:
        class ObjectExpr1782(IEncodable):
            def Encode(self, helpers_3: IEncoderHelpers_1[Any]) -> Any:
                return helpers_3.encode_string(value_6)

        return ObjectExpr1782()

    def _arrow1784(oa_1: OntologyAnnotation, id_map: Any=id_map, oa: Any=oa) -> IEncodable:
        return OntologyAnnotation_encoder(oa_1)

    def _arrow1785(comment: Comment, id_map: Any=id_map, oa: Any=oa) -> IEncodable:
        return ISAJson_encoder_1(id_map, comment)

    values: FSharpList[tuple[str, IEncodable]] = choose(chooser, of_array([try_include("pubMedID", _arrow1777, oa.PubMedID), try_include("doi", _arrow1779, oa.DOI), try_include("authorList", _arrow1781, oa.Authors), try_include("title", _arrow1783, oa.Title), try_include("status", _arrow1784, oa.Status), try_include_seq("comments", _arrow1785, oa.Comments)]))
    class ObjectExpr1786(IEncodable):
        def Encode(self, helpers_4: IEncoderHelpers_1[Any], id_map: Any=id_map, oa: Any=oa) -> Any:
            def mapping_1(tupled_arg_1: tuple[str, IEncodable]) -> tuple[str, __A_]:
                return (tupled_arg_1[0], tupled_arg_1[1].Encode(helpers_4))

            arg: IEnumerable_1[tuple[str, __A_]] = map_1(mapping_1, values)
            return helpers_4.encode_object(arg)

    return ObjectExpr1786()


ISAJson_allowedFields: FSharpList[str] = of_array(["pubMedID", "doi", "authorList", "title", "status", "comments"])

ISAJson_decoder: Decoder_1[Publication] = Decode_noAdditionalProperties(ISAJson_allowedFields, decoder)

__all__ = ["encoder", "decoder", "ROCrate_genID", "ROCrate_encoder", "ROCrate_decoder", "ISAJson_encoder", "ISAJson_allowedFields", "ISAJson_decoder"]

