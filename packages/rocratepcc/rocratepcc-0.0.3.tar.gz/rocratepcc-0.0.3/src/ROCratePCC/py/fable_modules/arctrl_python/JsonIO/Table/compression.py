from __future__ import annotations
from collections.abc import Callable
from typing import (Any, TypeVar)
from ....arctrl_core.Helper.collections_ import Dictionary_init
from ....arctrl_core.ontology_annotation import OntologyAnnotation
from ....arctrl_core.Table.composite_cell import CompositeCell
from ....arctrl_json.string_table import (encoder as encoder_3, array_from_map as array_from_map_2, decoder as decoder_1)
from ....arctrl_json.Table.cell_table import (encoder as encoder_1, array_from_map, decoder as decoder_3)
from ....arctrl_json.Table.oatable import (encoder as encoder_2, array_from_map as array_from_map_1, decoder as decoder_2)
from ....fable_library.seq import map
from ....fable_library.types import Array
from ....fable_library.util import (ignore, to_enumerable, IEnumerable_1)
from ....thoth_json_core.decode import (object as object_1, IRequiredGetter, IGetters)
from ....thoth_json_core.types import (IEncodable, IEncoderHelpers_1, Decoder_1)
from ....thoth_json_python.encode import to_string

__A_ = TypeVar("__A_")

_A = TypeVar("_A")

__A = TypeVar("__A")

__B = TypeVar("__B")

def encode(encoder: Callable[[Any, Any, Any, _A], IEncodable], obj: Any) -> IEncodable:
    string_table: Any = Dictionary_init()
    oa_table: Any = Dictionary_init()
    cell_table: Any = Dictionary_init()
    object: IEncodable = encoder(string_table, oa_table, cell_table, obj)
    ignore(to_string(0, object))
    encoded_cell_table: IEncodable = encoder_1(string_table, oa_table, array_from_map(cell_table))
    encoded_oatable: IEncodable = encoder_2(string_table, array_from_map_1(oa_table))
    encoded_string_table: IEncodable = encoder_3(array_from_map_2(string_table))
    class ObjectExpr3776(IEncodable):
        def Encode(self, helpers: IEncoderHelpers_1[Any], encoder: Any=encoder, obj: Any=obj) -> Any:
            def mapping(tupled_arg: tuple[str, IEncodable]) -> tuple[str, __A_]:
                return (tupled_arg[0], tupled_arg[1].Encode(helpers))

            arg: IEnumerable_1[tuple[str, __A_]] = map(mapping, to_enumerable([("cellTable", encoded_cell_table), ("oaTable", encoded_oatable), ("stringTable", encoded_string_table), ("object", object)]))
            return helpers.encode_object(arg)

    return ObjectExpr3776()


def decode(decoder: Callable[[Array[str], Array[OntologyAnnotation], Array[CompositeCell]], __A]) -> Decoder_1[Any]:
    def _arrow3778(get: IGetters, decoder: Any=decoder) -> __B:
        string_table: Array[str]
        object_arg: IRequiredGetter = get.Required
        string_table = object_arg.Field("stringTable", decoder_1)
        oa_table: Array[OntologyAnnotation]
        arg_3: Decoder_1[Array[OntologyAnnotation]] = decoder_2(string_table)
        object_arg_1: IRequiredGetter = get.Required
        oa_table = object_arg_1.Field("oaTable", arg_3)
        def _arrow3777(__unit: None=None) -> Array[CompositeCell]:
            arg_5: Decoder_1[Array[CompositeCell]] = decoder_3(string_table, oa_table)
            object_arg_2: IRequiredGetter = get.Required
            return object_arg_2.Field("cellTable", arg_5)

        arg_7: __A = decoder(string_table, oa_table, _arrow3777())
        object_arg_3: IRequiredGetter = get.Required
        return object_arg_3.Field("object", arg_7)

    return object_1(_arrow3778)


__all__ = ["encode", "decode"]

