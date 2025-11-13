from __future__ import annotations
from typing import (Any, TypeVar)
from ...arctrl_core.data_context import DataContext
from ...arctrl_core.data_map import DataMap
from ...arctrl_core.ontology_annotation import OntologyAnnotation
from ...arctrl_core.Table.composite_cell import CompositeCell
from ...fable_library.seq import map
from ...fable_library.types import Array
from ...fable_library.util import (to_enumerable, IEnumerable_1)
from ...thoth_json_core.decode import (object, resize_array, IRequiredGetter, IGetters)
from ...thoth_json_core.encode import seq
from ...thoth_json_core.types import (IEncodable, IEncoderHelpers_1, Decoder_1)
from .data_context import (encoder as encoder_1, decoder as decoder_1)

__A_ = TypeVar("__A_")

def encoder(dm: DataMap) -> IEncodable:
    def mapping(dc: DataContext, dm: Any=dm) -> IEncodable:
        return encoder_1(dc)

    values_1: IEnumerable_1[tuple[str, IEncodable]] = to_enumerable([("dataContexts", seq(map(mapping, dm.DataContexts)))])
    class ObjectExpr2299(IEncodable):
        def Encode(self, helpers: IEncoderHelpers_1[Any], dm: Any=dm) -> Any:
            def mapping_1(tupled_arg: tuple[str, IEncodable]) -> tuple[str, __A_]:
                return (tupled_arg[0], tupled_arg[1].Encode(helpers))

            arg: IEnumerable_1[tuple[str, __A_]] = map(mapping_1, values_1)
            return helpers.encode_object(arg)

    return ObjectExpr2299()


def _arrow2303(get: IGetters) -> DataMap:
    def _arrow2302(__unit: None=None) -> Array[DataContext]:
        arg_1: Decoder_1[Array[DataContext]] = resize_array(decoder_1)
        object_arg: IRequiredGetter = get.Required
        return object_arg.Field("dataContexts", arg_1)

    return DataMap(_arrow2302())


decoder: Decoder_1[DataMap] = object(_arrow2303)

def encoder_compressed(string_table: Any, oa_table: Any, cell_table: Any, dm: DataMap) -> IEncodable:
    return encoder(dm)


def decoder_compressed(string_table: Array[str], oa_table: Array[OntologyAnnotation], cell_table: Array[CompositeCell]) -> Decoder_1[DataMap]:
    return decoder


__all__ = ["encoder", "decoder", "encoder_compressed", "decoder_compressed"]

