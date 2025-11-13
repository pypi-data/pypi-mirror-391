from __future__ import annotations
from typing import (Any, TypeVar)
from ..arctrl_core.comment import Comment
from ..arctrl_core.ontology_source_reference import OntologySourceReference
from ..fable_library.list import (choose, of_array, FSharpList)
from ..fable_library.option import map
from ..fable_library.seq import map as map_1
from ..fable_library.string_ import replace
from ..fable_library.types import Array
from ..fable_library.util import IEnumerable_1
from ..thoth_json_core.decode import (object, IOptionalGetter, string, resize_array, IGetters)
from ..thoth_json_core.types import (IEncodable, IEncoderHelpers_1, Decoder_1)
from .comment import (encoder as encoder_1, decoder as decoder_1, ISAJson_encoder as ISAJson_encoder_1)
from .context.rocrate.isa_ontology_source_reference_context import context_jsonvalue
from .decode import Decode_uri
from .encode import (try_include, try_include_seq)

__A_ = TypeVar("__A_")

def encoder(osr: OntologySourceReference) -> IEncodable:
    def chooser(tupled_arg: tuple[str, IEncodable | None], osr: Any=osr) -> tuple[str, IEncodable] | None:
        def mapping(v_1: IEncodable, tupled_arg: Any=tupled_arg) -> tuple[str, IEncodable]:
            return (tupled_arg[0], v_1)

        return map(mapping, tupled_arg[1])

    def _arrow1608(value: str, osr: Any=osr) -> IEncodable:
        class ObjectExpr1607(IEncodable):
            def Encode(self, helpers: IEncoderHelpers_1[Any]) -> Any:
                return helpers.encode_string(value)

        return ObjectExpr1607()

    def _arrow1610(value_2: str, osr: Any=osr) -> IEncodable:
        class ObjectExpr1609(IEncodable):
            def Encode(self, helpers_1: IEncoderHelpers_1[Any]) -> Any:
                return helpers_1.encode_string(value_2)

        return ObjectExpr1609()

    def _arrow1612(value_4: str, osr: Any=osr) -> IEncodable:
        class ObjectExpr1611(IEncodable):
            def Encode(self, helpers_2: IEncoderHelpers_1[Any]) -> Any:
                return helpers_2.encode_string(value_4)

        return ObjectExpr1611()

    def _arrow1614(value_6: str, osr: Any=osr) -> IEncodable:
        class ObjectExpr1613(IEncodable):
            def Encode(self, helpers_3: IEncoderHelpers_1[Any]) -> Any:
                return helpers_3.encode_string(value_6)

        return ObjectExpr1613()

    def _arrow1615(comment: Comment, osr: Any=osr) -> IEncodable:
        return encoder_1(comment)

    values: FSharpList[tuple[str, IEncodable]] = choose(chooser, of_array([try_include("description", _arrow1608, osr.Description), try_include("file", _arrow1610, osr.File), try_include("name", _arrow1612, osr.Name), try_include("version", _arrow1614, osr.Version), try_include_seq("comments", _arrow1615, osr.Comments)]))
    class ObjectExpr1616(IEncodable):
        def Encode(self, helpers_4: IEncoderHelpers_1[Any], osr: Any=osr) -> Any:
            def mapping_1(tupled_arg_1: tuple[str, IEncodable]) -> tuple[str, __A_]:
                return (tupled_arg_1[0], tupled_arg_1[1].Encode(helpers_4))

            arg: IEnumerable_1[tuple[str, __A_]] = map_1(mapping_1, values)
            return helpers_4.encode_object(arg)

    return ObjectExpr1616()


def _arrow1622(get: IGetters) -> OntologySourceReference:
    def _arrow1617(__unit: None=None) -> str | None:
        object_arg: IOptionalGetter = get.Optional
        return object_arg.Field("description", Decode_uri)

    def _arrow1618(__unit: None=None) -> str | None:
        object_arg_1: IOptionalGetter = get.Optional
        return object_arg_1.Field("file", string)

    def _arrow1619(__unit: None=None) -> str | None:
        object_arg_2: IOptionalGetter = get.Optional
        return object_arg_2.Field("name", string)

    def _arrow1620(__unit: None=None) -> str | None:
        object_arg_3: IOptionalGetter = get.Optional
        return object_arg_3.Field("version", string)

    def _arrow1621(__unit: None=None) -> Array[Comment] | None:
        arg_9: Decoder_1[Array[Comment]] = resize_array(decoder_1)
        object_arg_4: IOptionalGetter = get.Optional
        return object_arg_4.Field("comments", arg_9)

    return OntologySourceReference(_arrow1617(), _arrow1618(), _arrow1619(), _arrow1620(), _arrow1621())


decoder: Decoder_1[OntologySourceReference] = object(_arrow1622)

def ROCrate_genID(o: OntologySourceReference) -> str:
    match_value: str | None = o.File
    if match_value is None:
        match_value_1: str | None = o.Name
        if match_value_1 is None:
            return "#DummyOntologySourceRef"

        else: 
            return "#OntologySourceRef_" + replace(match_value_1, " ", "_")


    else: 
        return match_value



def ROCrate_encoder(osr: OntologySourceReference) -> IEncodable:
    def chooser(tupled_arg: tuple[str, IEncodable | None], osr: Any=osr) -> tuple[str, IEncodable] | None:
        def mapping(v_1: IEncodable, tupled_arg: Any=tupled_arg) -> tuple[str, IEncodable]:
            return (tupled_arg[0], v_1)

        return map(mapping, tupled_arg[1])

    def _arrow1626(__unit: None=None, osr: Any=osr) -> IEncodable:
        value: str = ROCrate_genID(osr)
        class ObjectExpr1625(IEncodable):
            def Encode(self, helpers: IEncoderHelpers_1[Any]) -> Any:
                return helpers.encode_string(value)

        return ObjectExpr1625()

    class ObjectExpr1627(IEncodable):
        def Encode(self, helpers_1: IEncoderHelpers_1[Any], osr: Any=osr) -> Any:
            return helpers_1.encode_string("OntologySourceReference")

    def _arrow1629(value_2: str, osr: Any=osr) -> IEncodable:
        class ObjectExpr1628(IEncodable):
            def Encode(self, helpers_2: IEncoderHelpers_1[Any]) -> Any:
                return helpers_2.encode_string(value_2)

        return ObjectExpr1628()

    def _arrow1631(value_4: str, osr: Any=osr) -> IEncodable:
        class ObjectExpr1630(IEncodable):
            def Encode(self, helpers_3: IEncoderHelpers_1[Any]) -> Any:
                return helpers_3.encode_string(value_4)

        return ObjectExpr1630()

    def _arrow1633(value_6: str, osr: Any=osr) -> IEncodable:
        class ObjectExpr1632(IEncodable):
            def Encode(self, helpers_4: IEncoderHelpers_1[Any]) -> Any:
                return helpers_4.encode_string(value_6)

        return ObjectExpr1632()

    def _arrow1635(value_8: str, osr: Any=osr) -> IEncodable:
        class ObjectExpr1634(IEncodable):
            def Encode(self, helpers_5: IEncoderHelpers_1[Any]) -> Any:
                return helpers_5.encode_string(value_8)

        return ObjectExpr1634()

    def _arrow1636(comment: Comment, osr: Any=osr) -> IEncodable:
        return encoder_1(comment)

    values: FSharpList[tuple[str, IEncodable]] = choose(chooser, of_array([("@id", _arrow1626()), ("@type", ObjectExpr1627()), try_include("description", _arrow1629, osr.Description), try_include("file", _arrow1631, osr.File), try_include("name", _arrow1633, osr.Name), try_include("version", _arrow1635, osr.Version), try_include_seq("comments", _arrow1636, osr.Comments), ("@context", context_jsonvalue)]))
    class ObjectExpr1637(IEncodable):
        def Encode(self, helpers_6: IEncoderHelpers_1[Any], osr: Any=osr) -> Any:
            def mapping_1(tupled_arg_1: tuple[str, IEncodable]) -> tuple[str, __A_]:
                return (tupled_arg_1[0], tupled_arg_1[1].Encode(helpers_6))

            arg: IEnumerable_1[tuple[str, __A_]] = map_1(mapping_1, values)
            return helpers_6.encode_object(arg)

    return ObjectExpr1637()


def _arrow1643(get: IGetters) -> OntologySourceReference:
    def _arrow1638(__unit: None=None) -> str | None:
        object_arg: IOptionalGetter = get.Optional
        return object_arg.Field("description", Decode_uri)

    def _arrow1639(__unit: None=None) -> str | None:
        object_arg_1: IOptionalGetter = get.Optional
        return object_arg_1.Field("file", string)

    def _arrow1640(__unit: None=None) -> str | None:
        object_arg_2: IOptionalGetter = get.Optional
        return object_arg_2.Field("name", string)

    def _arrow1641(__unit: None=None) -> str | None:
        object_arg_3: IOptionalGetter = get.Optional
        return object_arg_3.Field("version", string)

    def _arrow1642(__unit: None=None) -> Array[Comment] | None:
        arg_9: Decoder_1[Array[Comment]] = resize_array(decoder_1)
        object_arg_4: IOptionalGetter = get.Optional
        return object_arg_4.Field("comments", arg_9)

    return OntologySourceReference(_arrow1638(), _arrow1639(), _arrow1640(), _arrow1641(), _arrow1642())


ROCrate_decoder: Decoder_1[OntologySourceReference] = object(_arrow1643)

def ISAJson_encoder(id_map: Any | None, osr: OntologySourceReference) -> IEncodable:
    def chooser(tupled_arg: tuple[str, IEncodable | None], id_map: Any=id_map, osr: Any=osr) -> tuple[str, IEncodable] | None:
        def mapping(v_1: IEncodable, tupled_arg: Any=tupled_arg) -> tuple[str, IEncodable]:
            return (tupled_arg[0], v_1)

        return map(mapping, tupled_arg[1])

    def _arrow1647(value: str, id_map: Any=id_map, osr: Any=osr) -> IEncodable:
        class ObjectExpr1646(IEncodable):
            def Encode(self, helpers: IEncoderHelpers_1[Any]) -> Any:
                return helpers.encode_string(value)

        return ObjectExpr1646()

    def _arrow1649(value_2: str, id_map: Any=id_map, osr: Any=osr) -> IEncodable:
        class ObjectExpr1648(IEncodable):
            def Encode(self, helpers_1: IEncoderHelpers_1[Any]) -> Any:
                return helpers_1.encode_string(value_2)

        return ObjectExpr1648()

    def _arrow1651(value_4: str, id_map: Any=id_map, osr: Any=osr) -> IEncodable:
        class ObjectExpr1650(IEncodable):
            def Encode(self, helpers_2: IEncoderHelpers_1[Any]) -> Any:
                return helpers_2.encode_string(value_4)

        return ObjectExpr1650()

    def _arrow1653(value_6: str, id_map: Any=id_map, osr: Any=osr) -> IEncodable:
        class ObjectExpr1652(IEncodable):
            def Encode(self, helpers_3: IEncoderHelpers_1[Any]) -> Any:
                return helpers_3.encode_string(value_6)

        return ObjectExpr1652()

    def _arrow1654(comment: Comment, id_map: Any=id_map, osr: Any=osr) -> IEncodable:
        return ISAJson_encoder_1(id_map, comment)

    values: FSharpList[tuple[str, IEncodable]] = choose(chooser, of_array([try_include("description", _arrow1647, osr.Description), try_include("file", _arrow1649, osr.File), try_include("name", _arrow1651, osr.Name), try_include("version", _arrow1653, osr.Version), try_include_seq("comments", _arrow1654, osr.Comments)]))
    class ObjectExpr1655(IEncodable):
        def Encode(self, helpers_4: IEncoderHelpers_1[Any], id_map: Any=id_map, osr: Any=osr) -> Any:
            def mapping_1(tupled_arg_1: tuple[str, IEncodable]) -> tuple[str, __A_]:
                return (tupled_arg_1[0], tupled_arg_1[1].Encode(helpers_4))

            arg: IEnumerable_1[tuple[str, __A_]] = map_1(mapping_1, values)
            return helpers_4.encode_object(arg)

    return ObjectExpr1655()


ISAJson_decoder: Decoder_1[OntologySourceReference] = decoder

__all__ = ["encoder", "decoder", "ROCrate_genID", "ROCrate_encoder", "ROCrate_decoder", "ISAJson_encoder", "ISAJson_decoder"]

