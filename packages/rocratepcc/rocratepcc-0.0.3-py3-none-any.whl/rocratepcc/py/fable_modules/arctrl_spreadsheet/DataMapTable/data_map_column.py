from __future__ import annotations
from collections.abc import Callable
from typing import Any
from ...arctrl_core.comment import Comment
from ...arctrl_core.data_context import (DataContext, DataContext__get_Explication, DataContext__get_Unit, DataContext__get_ObjectType, DataContext__get_Description, DataContext__get_GeneratedBy, DataContext__get_Label)
from ...arctrl_core.ontology_annotation import OntologyAnnotation
from ...fable_library.list import (map, FSharpList, of_array, singleton, transpose)
from ...fable_library.option import (default_arg, bind)
from ...fable_library.seq import (to_list, collect, map as map_1, delay, append, singleton as singleton_1, try_find)
from ...fable_library.seq2 import distinct
from ...fable_library.types import Array
from ...fable_library.util import (ignore, IEnumerable_1, string_hash)
from ...fs_spreadsheet.Cells.fs_cell import FsCell
from ...fs_spreadsheet.fs_column import FsColumn
from .data_map_header import (from_fs_cells, to_fs_cells)

def set_from_fs_columns(dc: Array[DataContext], columns: FSharpList[FsColumn]) -> Array[DataContext]:
    def mapping(c: FsColumn, dc: Any=dc, columns: Any=columns) -> FsCell:
        return c.Item(1)

    cell_parser: Callable[[DataContext, FSharpList[FsCell]], DataContext] = from_fs_cells(map(mapping, columns))
    for i in range(0, (len(dc) - 1) + 1, 1):
        def mapping_1(c_1: FsColumn, dc: Any=dc, columns: Any=columns) -> FsCell:
            return c_1.Item(i + 2)

        ignore(cell_parser(dc[i])(map(mapping_1, columns)))
    return dc


def to_fs_columns(dc: Array[DataContext]) -> FSharpList[FSharpList[FsCell]]:
    def mapping_1(dc_1: DataContext, dc: Any=dc) -> IEnumerable_1[str]:
        def mapping(c: Comment, dc_1: Any=dc_1) -> str:
            return default_arg(c.Name, "")

        return map_1(mapping, dc_1.Comments)

    class ObjectExpr3287:
        @property
        def Equals(self) -> Callable[[str, str], bool]:
            def _arrow3286(x: str, y: str) -> bool:
                return x == y

            return _arrow3286

        @property
        def GetHashCode(self) -> Callable[[str], int]:
            return string_hash

    comment_keys: FSharpList[str] = to_list(distinct(collect(mapping_1, dc), ObjectExpr3287()))
    headers: FSharpList[FsCell] = to_fs_cells(comment_keys)
    def create_term(oa: OntologyAnnotation | None=None, dc: Any=dc) -> FSharpList[FsCell]:
        if oa is None:
            return of_array([FsCell(""), FsCell(""), FsCell("")])

        else: 
            oa_1: OntologyAnnotation = oa
            return of_array([FsCell(default_arg(oa_1.Name, "")), FsCell(default_arg(oa_1.TermSourceREF, "")), FsCell(default_arg(oa_1.TermAccessionNumber, ""))])


    def create_text(s: str | None=None, dc: Any=dc) -> FSharpList[FsCell]:
        return singleton(FsCell(default_arg(s, "")))

    def _arrow3299(__unit: None=None, dc: Any=dc) -> IEnumerable_1[FSharpList[FsCell]]:
        def _arrow3298(__unit: None=None) -> IEnumerable_1[FSharpList[FsCell]]:
            def _arrow3297(dc_4: DataContext) -> FSharpList[FsCell]:
                dc_3: DataContext = dc_4
                def _arrow3296(__unit: None=None) -> IEnumerable_1[FsCell]:
                    def _arrow3288(__unit: None=None) -> FSharpList[FsCell]:
                        dc_2: DataContext = dc_3
                        return of_array([FsCell(default_arg(dc_2.Name, "")), FsCell(default_arg(dc_2.Format, "")), FsCell(default_arg(dc_2.SelectorFormat, ""))])

                    def _arrow3295(__unit: None=None) -> IEnumerable_1[FsCell]:
                        def _arrow3294(__unit: None=None) -> IEnumerable_1[FsCell]:
                            def _arrow3293(__unit: None=None) -> IEnumerable_1[FsCell]:
                                def _arrow3292(__unit: None=None) -> IEnumerable_1[FsCell]:
                                    def _arrow3291(__unit: None=None) -> IEnumerable_1[FsCell]:
                                        def _arrow3290(__unit: None=None) -> IEnumerable_1[FsCell]:
                                            def _arrow3289(__unit: None=None) -> IEnumerable_1[FsCell]:
                                                def mapping_2(key: str) -> FsCell:
                                                    def binder(c_2: Comment, key: Any=key) -> str | None:
                                                        return c_2.Value

                                                    def predicate(c_1: Comment, key: Any=key) -> bool:
                                                        return default_arg(c_1.Name, "") == key

                                                    return FsCell(default_arg(bind(binder, try_find(predicate, dc_3.Comments)), ""))

                                                return map(mapping_2, comment_keys)

                                            return append(create_text(DataContext__get_Label(dc_3)), delay(_arrow3289))

                                        return append(create_text(DataContext__get_GeneratedBy(dc_3)), delay(_arrow3290))

                                    return append(create_text(DataContext__get_Description(dc_3)), delay(_arrow3291))

                                return append(create_term(DataContext__get_ObjectType(dc_3)), delay(_arrow3292))

                            return append(create_term(DataContext__get_Unit(dc_3)), delay(_arrow3293))

                        return append(create_term(DataContext__get_Explication(dc_3)), delay(_arrow3294))

                    return append(_arrow3288(), delay(_arrow3295))

                return to_list(delay(_arrow3296))

            return map_1(_arrow3297, dc)

        return append(singleton_1(headers), delay(_arrow3298))

    return transpose(to_list(delay(_arrow3299)))


__all__ = ["set_from_fs_columns", "to_fs_columns"]

