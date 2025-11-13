from __future__ import annotations
from collections.abc import Callable
from typing import Any
from ..fable_library.array_ import (contains as contains_1, remove_in_place, add_range_in_place)
from ..fable_library.option import (map, default_arg, value as value_5)
from ..fable_library.range import range_big_int
from ..fable_library.reflection import (TypeInfo, class_type)
from ..fable_library.resize_array import find_index
from ..fable_library.seq import (to_array, filter, contains, for_all, length, fold, to_list, delay, map as map_1, item, choose, exists, try_find_index, iterate, remove_at, try_find, append as append_4, collect)
from ..fable_library.seq2 import Array_distinct
from ..fable_library.string_ import (to_text, printf)
from ..fable_library.types import (Array, FSharpRef)
from ..fable_library.util import (string_hash, IEnumerable_1, get_enumerator, dispose, equals, safe_hash, to_enumerable, ignore)
from .comment import (Comment, Remark)
from .data_map import DataMap
from .Helper.collections_ import (ResizeArray_map, ResizeArray_filter, ResizeArray_choose)
from .Helper.hash_codes import (box_hash_array, box_hash_option, box_hash_seq)
from .Helper.identifier import check_valid_characters
from .ontology_annotation import OntologyAnnotation
from .ontology_source_reference import OntologySourceReference
from .person import Person
from .Process.component import Component
from .Process.protocol_parameter import ProtocolParameter
from .publication import Publication
from .Table.arc_table import ArcTable
from .Table.arc_tables import (ArcTables, ArcTables_reflection, ArcTablesAux_getIOMap, ArcTablesAux_applyIOMap)
from .Table.composite_cell import CompositeCell
from .Table.composite_column import CompositeColumn
from .Table.composite_header import CompositeHeader

def _expr517() -> TypeInfo:
    return class_type("ARCtrl.ArcAssay", None, ArcAssay, ArcTables_reflection())


class ArcAssay(ArcTables):
    def __init__(self, identifier: str, title: str | None=None, description: str | None=None, measurement_type: OntologyAnnotation | None=None, technology_type: OntologyAnnotation | None=None, technology_platform: OntologyAnnotation | None=None, tables: Array[ArcTable] | None=None, datamap: DataMap | None=None, performers: Array[Person] | None=None, comments: Array[Comment] | None=None) -> None:
        super().__init__(default_arg(tables, []))
        performers_1: Array[Person] = default_arg(performers, [])
        comments_1: Array[Comment] = default_arg(comments, [])
        def _arrow516(__unit: None=None) -> str:
            identifier_1: str = identifier.strip()
            check_valid_characters(identifier_1)
            return identifier_1

        self.identifier_0040129: str = _arrow516()
        self.title_0040133: str | None = title
        self.description_0040134: str | None = description
        self.investigation: ArcInvestigation | None = None
        self.measurement_type_0040136: OntologyAnnotation | None = measurement_type
        self.technology_type_0040137: OntologyAnnotation | None = technology_type
        self.technology_platform_0040138: OntologyAnnotation | None = technology_platform
        self.data_map: DataMap | None = datamap
        self.performers_0040140_002D1: Array[Person] = performers_1
        self.comments_0040141_002D1: Array[Comment] = comments_1
        self.static_hash: int = 0

    @property
    def Identifier(self, __unit: None=None) -> str:
        this: ArcAssay = self
        return this.identifier_0040129

    @Identifier.setter
    def Identifier(self, i: str) -> None:
        this: ArcAssay = self
        this.identifier_0040129 = i

    @property
    def Investigation(self, __unit: None=None) -> ArcInvestigation | None:
        this: ArcAssay = self
        return this.investigation

    @Investigation.setter
    def Investigation(self, i: ArcInvestigation | None=None) -> None:
        this: ArcAssay = self
        this.investigation = i

    @property
    def Title(self, __unit: None=None) -> str | None:
        this: ArcAssay = self
        return this.title_0040133

    @Title.setter
    def Title(self, t: str | None=None) -> None:
        this: ArcAssay = self
        this.title_0040133 = t

    @property
    def Description(self, __unit: None=None) -> str | None:
        this: ArcAssay = self
        return this.description_0040134

    @Description.setter
    def Description(self, d: str | None=None) -> None:
        this: ArcAssay = self
        this.description_0040134 = d

    @property
    def MeasurementType(self, __unit: None=None) -> OntologyAnnotation | None:
        this: ArcAssay = self
        return this.measurement_type_0040136

    @MeasurementType.setter
    def MeasurementType(self, n: OntologyAnnotation | None=None) -> None:
        this: ArcAssay = self
        this.measurement_type_0040136 = n

    @property
    def TechnologyType(self, __unit: None=None) -> OntologyAnnotation | None:
        this: ArcAssay = self
        return this.technology_type_0040137

    @TechnologyType.setter
    def TechnologyType(self, n: OntologyAnnotation | None=None) -> None:
        this: ArcAssay = self
        this.technology_type_0040137 = n

    @property
    def TechnologyPlatform(self, __unit: None=None) -> OntologyAnnotation | None:
        this: ArcAssay = self
        return this.technology_platform_0040138

    @TechnologyPlatform.setter
    def TechnologyPlatform(self, n: OntologyAnnotation | None=None) -> None:
        this: ArcAssay = self
        this.technology_platform_0040138 = n

    @property
    def DataMap(self, __unit: None=None) -> DataMap | None:
        this: ArcAssay = self
        return this.data_map

    @DataMap.setter
    def DataMap(self, n: DataMap | None=None) -> None:
        this: ArcAssay = self
        this.data_map = n

    @property
    def Performers(self, __unit: None=None) -> Array[Person]:
        this: ArcAssay = self
        return this.performers_0040140_002D1

    @Performers.setter
    def Performers(self, n: Array[Person]) -> None:
        this: ArcAssay = self
        this.performers_0040140_002D1 = n

    @property
    def Comments(self, __unit: None=None) -> Array[Comment]:
        this: ArcAssay = self
        return this.comments_0040141_002D1

    @Comments.setter
    def Comments(self, n: Array[Comment]) -> None:
        this: ArcAssay = self
        this.comments_0040141_002D1 = n

    @property
    def StaticHash(self, __unit: None=None) -> int:
        this: ArcAssay = self
        return this.static_hash

    @StaticHash.setter
    def StaticHash(self, h: int) -> None:
        this: ArcAssay = self
        this.static_hash = h or 0

    @staticmethod
    def init(identifier: str) -> ArcAssay:
        return ArcAssay(identifier)

    @staticmethod
    def create(identifier: str, title: str | None=None, description: str | None=None, measurement_type: OntologyAnnotation | None=None, technology_type: OntologyAnnotation | None=None, technology_platform: OntologyAnnotation | None=None, tables: Array[ArcTable] | None=None, datamap: DataMap | None=None, performers: Array[Person] | None=None, comments: Array[Comment] | None=None) -> ArcAssay:
        return ArcAssay(identifier, title, description, measurement_type, technology_type, technology_platform, tables, datamap, performers, comments)

    @staticmethod
    def make(identifier: str, title: str | None, description: str | None, measurement_type: OntologyAnnotation | None, technology_type: OntologyAnnotation | None, technology_platform: OntologyAnnotation | None, tables: Array[ArcTable], datamap: DataMap | None, performers: Array[Person], comments: Array[Comment]) -> ArcAssay:
        return ArcAssay(identifier, title, description, measurement_type, technology_type, technology_platform, tables, datamap, performers, comments)

    @staticmethod
    def FileName() -> str:
        return "isa.assay.xlsx"

    @property
    def StudiesRegisteredIn(self, __unit: None=None) -> Array[ArcStudy]:
        this: ArcAssay = self
        match_value: ArcInvestigation | None = this.Investigation
        if match_value is None:
            return []

        else: 
            i: ArcInvestigation = match_value
            def predicate(s: ArcStudy) -> bool:
                source: Array[str] = s.RegisteredAssayIdentifiers
                class ObjectExpr468:
                    @property
                    def Equals(self) -> Callable[[str, str], bool]:
                        def _arrow467(x: str, y: str) -> bool:
                            return x == y

                        return _arrow467

                    @property
                    def GetHashCode(self) -> Callable[[str], int]:
                        return string_hash

                return contains(this.Identifier, source, ObjectExpr468())

            return to_array(filter(predicate, i.Studies))


    @staticmethod
    def add_table(table: ArcTable, index: int | None=None) -> Callable[[ArcAssay], ArcAssay]:
        def _arrow469(assay: ArcAssay) -> ArcAssay:
            c: ArcAssay = assay.Copy()
            c.AddTable(table, index)
            return c

        return _arrow469

    @staticmethod
    def add_tables(tables: IEnumerable_1[ArcTable], index: int | None=None) -> Callable[[ArcAssay], ArcAssay]:
        def _arrow470(assay: ArcAssay) -> ArcAssay:
            c: ArcAssay = assay.Copy()
            c.AddTables(tables, index)
            return c

        return _arrow470

    @staticmethod
    def init_table(table_name: str, index: int | None=None) -> Callable[[ArcAssay], tuple[ArcAssay, ArcTable]]:
        def _arrow471(assay: ArcAssay) -> tuple[ArcAssay, ArcTable]:
            c: ArcAssay = assay.Copy()
            return (c, c.InitTable(table_name, index))

        return _arrow471

    @staticmethod
    def init_tables(table_names: IEnumerable_1[str], index: int | None=None) -> Callable[[ArcAssay], ArcAssay]:
        def _arrow472(assay: ArcAssay) -> ArcAssay:
            c: ArcAssay = assay.Copy()
            c.InitTables(table_names, index)
            return c

        return _arrow472

    @staticmethod
    def get_table_at(index: int) -> Callable[[ArcAssay], ArcTable]:
        def _arrow473(assay: ArcAssay) -> ArcTable:
            new_assay: ArcAssay = assay.Copy()
            return new_assay.GetTableAt(index)

        return _arrow473

    @staticmethod
    def get_table(name: str) -> Callable[[ArcAssay], ArcTable]:
        def _arrow474(assay: ArcAssay) -> ArcTable:
            new_assay: ArcAssay = assay.Copy()
            return new_assay.GetTable(name)

        return _arrow474

    @staticmethod
    def update_table_at(index: int, table: ArcTable) -> Callable[[ArcAssay], ArcAssay]:
        def _arrow475(assay: ArcAssay) -> ArcAssay:
            new_assay: ArcAssay = assay.Copy()
            new_assay.UpdateTableAt(index, table)
            return new_assay

        return _arrow475

    @staticmethod
    def update_table(name: str, table: ArcTable) -> Callable[[ArcAssay], ArcAssay]:
        def _arrow476(assay: ArcAssay) -> ArcAssay:
            new_assay: ArcAssay = assay.Copy()
            new_assay.UpdateTable(name, table)
            return new_assay

        return _arrow476

    @staticmethod
    def set_table_at(index: int, table: ArcTable) -> Callable[[ArcAssay], ArcAssay]:
        def _arrow477(assay: ArcAssay) -> ArcAssay:
            new_assay: ArcAssay = assay.Copy()
            new_assay.SetTableAt(index, table)
            return new_assay

        return _arrow477

    @staticmethod
    def set_table(name: str, table: ArcTable) -> Callable[[ArcAssay], ArcAssay]:
        def _arrow478(assay: ArcAssay) -> ArcAssay:
            new_assay: ArcAssay = assay.Copy()
            new_assay.SetTable(name, table)
            return new_assay

        return _arrow478

    @staticmethod
    def remove_table_at(index: int) -> Callable[[ArcAssay], ArcAssay]:
        def _arrow479(assay: ArcAssay) -> ArcAssay:
            new_assay: ArcAssay = assay.Copy()
            new_assay.RemoveTableAt(index)
            return new_assay

        return _arrow479

    @staticmethod
    def remove_table(name: str) -> Callable[[ArcAssay], ArcAssay]:
        def _arrow480(assay: ArcAssay) -> ArcAssay:
            new_assay: ArcAssay = assay.Copy()
            new_assay.RemoveTable(name)
            return new_assay

        return _arrow480

    @staticmethod
    def map_table_at(index: int, update_fun: Callable[[ArcTable], None]) -> Callable[[ArcAssay], ArcAssay]:
        def _arrow481(assay: ArcAssay) -> ArcAssay:
            new_assay: ArcAssay = assay.Copy()
            new_assay.MapTableAt(index, update_fun)
            return new_assay

        return _arrow481

    @staticmethod
    def update_table_by(name: str, update_fun: Callable[[ArcTable], None]) -> Callable[[ArcAssay], ArcAssay]:
        def _arrow482(assay: ArcAssay) -> ArcAssay:
            new_assay: ArcAssay = assay.Copy()
            new_assay.MapTable(name, update_fun)
            return new_assay

        return _arrow482

    @staticmethod
    def rename_table_at(index: int, new_name: str) -> Callable[[ArcAssay], ArcAssay]:
        def _arrow483(assay: ArcAssay) -> ArcAssay:
            new_assay: ArcAssay = assay.Copy()
            new_assay.RenameTableAt(index, new_name)
            return new_assay

        return _arrow483

    @staticmethod
    def rename_table(name: str, new_name: str) -> Callable[[ArcAssay], ArcAssay]:
        def _arrow484(assay: ArcAssay) -> ArcAssay:
            new_assay: ArcAssay = assay.Copy()
            new_assay.RenameTable(name, new_name)
            return new_assay

        return _arrow484

    @staticmethod
    def add_column_at(table_index: int, header: CompositeHeader, cells: Array[CompositeCell] | None=None, column_index: int | None=None, force_replace: bool | None=None) -> Callable[[ArcAssay], ArcAssay]:
        def _arrow485(assay: ArcAssay) -> ArcAssay:
            new_assay: ArcAssay = assay.Copy()
            new_assay.AddColumnAt(table_index, header, cells, column_index, force_replace)
            return new_assay

        return _arrow485

    @staticmethod
    def add_column(table_name: str, header: CompositeHeader, cells: Array[CompositeCell] | None=None, column_index: int | None=None, force_replace: bool | None=None) -> Callable[[ArcAssay], ArcAssay]:
        def _arrow486(assay: ArcAssay) -> ArcAssay:
            new_assay: ArcAssay = assay.Copy()
            new_assay.AddColumn(table_name, header, cells, column_index, force_replace)
            return new_assay

        return _arrow486

    @staticmethod
    def remove_column_at(table_index: int, column_index: int) -> Callable[[ArcAssay], ArcAssay]:
        def _arrow487(assay: ArcAssay) -> ArcAssay:
            new_assay: ArcAssay = assay.Copy()
            new_assay.RemoveColumnAt(table_index, column_index)
            return new_assay

        return _arrow487

    @staticmethod
    def remove_column(table_name: str, column_index: int) -> Callable[[ArcAssay], ArcAssay]:
        def _arrow488(assay: ArcAssay) -> ArcAssay:
            new_assay: ArcAssay = assay.Copy()
            new_assay.RemoveColumn(table_name, column_index)
            return new_assay

        return _arrow488

    @staticmethod
    def update_column_at(table_index: int, column_index: int, header: CompositeHeader, cells: Array[CompositeCell] | None=None) -> Callable[[ArcAssay], ArcAssay]:
        def _arrow489(assay: ArcAssay) -> ArcAssay:
            new_assay: ArcAssay = assay.Copy()
            new_assay.UpdateColumnAt(table_index, column_index, header, cells)
            return new_assay

        return _arrow489

    @staticmethod
    def update_column(table_name: str, column_index: int, header: CompositeHeader, cells: Array[CompositeCell] | None=None) -> Callable[[ArcAssay], ArcAssay]:
        def _arrow490(assay: ArcAssay) -> ArcAssay:
            new_assay: ArcAssay = assay.Copy()
            new_assay.UpdateColumn(table_name, column_index, header, cells)
            return new_assay

        return _arrow490

    @staticmethod
    def get_column_at(table_index: int, column_index: int) -> Callable[[ArcAssay], CompositeColumn]:
        def _arrow491(assay: ArcAssay) -> CompositeColumn:
            new_assay: ArcAssay = assay.Copy()
            return new_assay.GetColumnAt(table_index, column_index)

        return _arrow491

    @staticmethod
    def get_column(table_name: str, column_index: int) -> Callable[[ArcAssay], CompositeColumn]:
        def _arrow492(assay: ArcAssay) -> CompositeColumn:
            new_assay: ArcAssay = assay.Copy()
            return new_assay.GetColumn(table_name, column_index)

        return _arrow492

    @staticmethod
    def add_row_at(table_index: int, cells: Array[CompositeCell] | None=None, row_index: int | None=None) -> Callable[[ArcAssay], ArcAssay]:
        def _arrow493(assay: ArcAssay) -> ArcAssay:
            new_assay: ArcAssay = assay.Copy()
            new_assay.AddRowAt(table_index, cells, row_index)
            return new_assay

        return _arrow493

    @staticmethod
    def add_row(table_name: str, cells: Array[CompositeCell] | None=None, row_index: int | None=None) -> Callable[[ArcAssay], ArcAssay]:
        def _arrow494(assay: ArcAssay) -> ArcAssay:
            new_assay: ArcAssay = assay.Copy()
            new_assay.AddRow(table_name, cells, row_index)
            return new_assay

        return _arrow494

    @staticmethod
    def remove_row_at(table_index: int, row_index: int) -> Callable[[ArcAssay], ArcAssay]:
        def _arrow495(assay: ArcAssay) -> ArcAssay:
            new_assay: ArcAssay = assay.Copy()
            new_assay.RemoveColumnAt(table_index, row_index)
            return new_assay

        return _arrow495

    @staticmethod
    def remove_row(table_name: str, row_index: int) -> Callable[[ArcAssay], ArcAssay]:
        def _arrow496(assay: ArcAssay) -> ArcAssay:
            new_assay: ArcAssay = assay.Copy()
            new_assay.RemoveRow(table_name, row_index)
            return new_assay

        return _arrow496

    @staticmethod
    def update_row_at(table_index: int, row_index: int, cells: Array[CompositeCell]) -> Callable[[ArcAssay], ArcAssay]:
        def _arrow497(assay: ArcAssay) -> ArcAssay:
            new_assay: ArcAssay = assay.Copy()
            new_assay.UpdateRowAt(table_index, row_index, cells)
            return new_assay

        return _arrow497

    @staticmethod
    def update_row(table_name: str, row_index: int, cells: Array[CompositeCell]) -> Callable[[ArcAssay], ArcAssay]:
        def _arrow498(assay: ArcAssay) -> ArcAssay:
            new_assay: ArcAssay = assay.Copy()
            new_assay.UpdateRow(table_name, row_index, cells)
            return new_assay

        return _arrow498

    @staticmethod
    def get_row_at(table_index: int, row_index: int) -> Callable[[ArcAssay], Array[CompositeCell]]:
        def _arrow499(assay: ArcAssay) -> Array[CompositeCell]:
            new_assay: ArcAssay = assay.Copy()
            return new_assay.GetRowAt(table_index, row_index)

        return _arrow499

    @staticmethod
    def get_row(table_name: str, row_index: int) -> Callable[[ArcAssay], Array[CompositeCell]]:
        def _arrow500(assay: ArcAssay) -> Array[CompositeCell]:
            new_assay: ArcAssay = assay.Copy()
            return new_assay.GetRow(table_name, row_index)

        return _arrow500

    @staticmethod
    def set_performers(performers: Array[Person], assay: ArcAssay) -> ArcAssay:
        assay.Performers = performers
        return assay

    def Copy(self, __unit: None=None) -> ArcAssay:
        this: ArcAssay = self
        def f(c: ArcTable) -> ArcTable:
            return c.Copy()

        next_tables: Array[ArcTable] = ResizeArray_map(f, this.Tables)
        def f_1(c_1: Comment) -> Comment:
            return c_1.Copy()

        next_comments: Array[Comment] = ResizeArray_map(f_1, this.Comments)
        def mapping(d: DataMap) -> DataMap:
            return d.Copy()

        next_data_map: DataMap | None = map(mapping, this.DataMap)
        def f_2(c_2: Person) -> Person:
            return c_2.Copy()

        next_performers: Array[Person] = ResizeArray_map(f_2, this.Performers)
        identifier: str = this.Identifier
        title: str | None = this.Title
        description: str | None = this.Description
        measurement_type: OntologyAnnotation | None = this.MeasurementType
        technology_type: OntologyAnnotation | None = this.TechnologyType
        technology_platform: OntologyAnnotation | None = this.TechnologyPlatform
        return ArcAssay.make(identifier, title, description, measurement_type, technology_type, technology_platform, next_tables, next_data_map, next_performers, next_comments)

    def UpdateBy(self, assay: ArcAssay, only_replace_existing: bool | None=None, append_sequences: bool | None=None) -> None:
        this: ArcAssay = self
        only_replace_existing_1: bool = default_arg(only_replace_existing, False)
        append_sequences_1: bool = default_arg(append_sequences, False)
        update_always: bool = not only_replace_existing_1
        if True if (assay.Title is not None) else update_always:
            this.Title = assay.Title

        if True if (assay.Description is not None) else update_always:
            this.Description = assay.Description

        if True if (assay.MeasurementType is not None) else update_always:
            this.MeasurementType = assay.MeasurementType

        if True if (assay.TechnologyType is not None) else update_always:
            this.TechnologyType = assay.TechnologyType

        if True if (assay.TechnologyPlatform is not None) else update_always:
            this.TechnologyPlatform = assay.TechnologyPlatform

        if True if (len(assay.Tables) != 0) else update_always:
            s: Array[ArcTable]
            origin: Array[ArcTable] = this.Tables
            next_1: Array[ArcTable] = assay.Tables
            if not append_sequences_1:
                def f(x: ArcTable) -> ArcTable:
                    return x

                s = ResizeArray_map(f, next_1)

            else: 
                combined: Array[ArcTable] = []
                enumerator: Any = get_enumerator(origin)
                try: 
                    while enumerator.System_Collections_IEnumerator_MoveNext():
                        e: ArcTable = enumerator.System_Collections_Generic_IEnumerator_1_get_Current()
                        class ObjectExpr501:
                            @property
                            def Equals(self) -> Callable[[ArcTable, ArcTable], bool]:
                                return equals

                            @property
                            def GetHashCode(self) -> Callable[[ArcTable], int]:
                                return safe_hash

                        if not contains_1(e, combined, ObjectExpr501()):
                            (combined.append(e))


                finally: 
                    dispose(enumerator)

                enumerator_1: Any = get_enumerator(next_1)
                try: 
                    while enumerator_1.System_Collections_IEnumerator_MoveNext():
                        e_1: ArcTable = enumerator_1.System_Collections_Generic_IEnumerator_1_get_Current()
                        class ObjectExpr502:
                            @property
                            def Equals(self) -> Callable[[ArcTable, ArcTable], bool]:
                                return equals

                            @property
                            def GetHashCode(self) -> Callable[[ArcTable], int]:
                                return safe_hash

                        if not contains_1(e_1, combined, ObjectExpr502()):
                            (combined.append(e_1))


                finally: 
                    dispose(enumerator_1)

                s = combined

            this.Tables = s

        if True if (len(assay.Performers) != 0) else update_always:
            s_1: Array[Person]
            origin_1: Array[Person] = this.Performers
            next_1_1: Array[Person] = assay.Performers
            if not append_sequences_1:
                def f_1(x_3: Person) -> Person:
                    return x_3

                s_1 = ResizeArray_map(f_1, next_1_1)

            else: 
                combined_1: Array[Person] = []
                enumerator_2: Any = get_enumerator(origin_1)
                try: 
                    while enumerator_2.System_Collections_IEnumerator_MoveNext():
                        e_2: Person = enumerator_2.System_Collections_Generic_IEnumerator_1_get_Current()
                        class ObjectExpr503:
                            @property
                            def Equals(self) -> Callable[[Person, Person], bool]:
                                return equals

                            @property
                            def GetHashCode(self) -> Callable[[Person], int]:
                                return safe_hash

                        if not contains_1(e_2, combined_1, ObjectExpr503()):
                            (combined_1.append(e_2))


                finally: 
                    dispose(enumerator_2)

                enumerator_1_1: Any = get_enumerator(next_1_1)
                try: 
                    while enumerator_1_1.System_Collections_IEnumerator_MoveNext():
                        e_1_1: Person = enumerator_1_1.System_Collections_Generic_IEnumerator_1_get_Current()
                        class ObjectExpr504:
                            @property
                            def Equals(self) -> Callable[[Person, Person], bool]:
                                return equals

                            @property
                            def GetHashCode(self) -> Callable[[Person], int]:
                                return safe_hash

                        if not contains_1(e_1_1, combined_1, ObjectExpr504()):
                            (combined_1.append(e_1_1))


                finally: 
                    dispose(enumerator_1_1)

                s_1 = combined_1

            this.Performers = s_1

        if True if (len(assay.Comments) != 0) else update_always:
            s_2: Array[Comment]
            origin_2: Array[Comment] = this.Comments
            next_1_2: Array[Comment] = assay.Comments
            if not append_sequences_1:
                def f_2(x_6: Comment) -> Comment:
                    return x_6

                s_2 = ResizeArray_map(f_2, next_1_2)

            else: 
                combined_2: Array[Comment] = []
                enumerator_3: Any = get_enumerator(origin_2)
                try: 
                    while enumerator_3.System_Collections_IEnumerator_MoveNext():
                        e_3: Comment = enumerator_3.System_Collections_Generic_IEnumerator_1_get_Current()
                        class ObjectExpr505:
                            @property
                            def Equals(self) -> Callable[[Comment, Comment], bool]:
                                return equals

                            @property
                            def GetHashCode(self) -> Callable[[Comment], int]:
                                return safe_hash

                        if not contains_1(e_3, combined_2, ObjectExpr505()):
                            (combined_2.append(e_3))


                finally: 
                    dispose(enumerator_3)

                enumerator_1_2: Any = get_enumerator(next_1_2)
                try: 
                    while enumerator_1_2.System_Collections_IEnumerator_MoveNext():
                        e_1_2: Comment = enumerator_1_2.System_Collections_Generic_IEnumerator_1_get_Current()
                        class ObjectExpr506:
                            @property
                            def Equals(self) -> Callable[[Comment, Comment], bool]:
                                return equals

                            @property
                            def GetHashCode(self) -> Callable[[Comment], int]:
                                return safe_hash

                        if not contains_1(e_1_2, combined_2, ObjectExpr506()):
                            (combined_2.append(e_1_2))


                finally: 
                    dispose(enumerator_1_2)

                s_2 = combined_2

            this.Comments = s_2


    def __str__(self, __unit: None=None) -> str:
        this: ArcAssay = self
        arg: str = this.Identifier
        arg_1: str | None = this.Title
        arg_2: str | None = this.Description
        arg_3: OntologyAnnotation | None = this.MeasurementType
        arg_4: OntologyAnnotation | None = this.TechnologyType
        arg_5: OntologyAnnotation | None = this.TechnologyPlatform
        arg_6: Array[ArcTable] = this.Tables
        arg_7: Array[Person] = this.Performers
        arg_8: Array[Comment] = this.Comments
        return to_text(printf("ArcAssay({\r\n    Identifier = \"%s\",\r\n    Title = %A,\r\n    Description = %A,\r\n    MeasurementType = %A,\r\n    TechnologyType = %A,\r\n    TechnologyPlatform = %A,\r\n    Tables = %A,\r\n    Performers = %A,\r\n    Comments = %A\r\n})"))(arg)(arg_1)(arg_2)(arg_3)(arg_4)(arg_5)(arg_6)(arg_7)(arg_8)

    def AddToInvestigation(self, investigation: ArcInvestigation) -> None:
        this: ArcAssay = self
        this.Investigation = investigation

    def RemoveFromInvestigation(self, __unit: None=None) -> None:
        this: ArcAssay = self
        this.Investigation = None

    def UpdateReferenceByAssayFile(self, assay: ArcAssay, only_replace_existing: bool | None=None) -> None:
        this: ArcAssay = self
        update_always: bool = not default_arg(only_replace_existing, False)
        if True if (assay.Title is not None) else update_always:
            this.Title = assay.Title

        if True if (assay.Description is not None) else update_always:
            this.Description = assay.Description

        if True if (assay.MeasurementType is not None) else update_always:
            this.MeasurementType = assay.MeasurementType

        if True if (assay.TechnologyPlatform is not None) else update_always:
            this.TechnologyPlatform = assay.TechnologyPlatform

        if True if (assay.TechnologyType is not None) else update_always:
            this.TechnologyType = assay.TechnologyType

        if True if (len(assay.Tables) != 0) else update_always:
            this.Tables = assay.Tables

        if True if (len(assay.Comments) != 0) else update_always:
            this.Comments = assay.Comments

        this.DataMap = assay.DataMap
        if True if (len(assay.Performers) != 0) else update_always:
            this.Performers = assay.Performers


    def StructurallyEquals(self, other: ArcAssay) -> bool:
        this: ArcAssay = self
        def predicate(x: bool) -> bool:
            return x == True

        def _arrow509(__unit: None=None) -> bool:
            a: IEnumerable_1[ArcTable] = this.Tables
            b: IEnumerable_1[ArcTable] = other.Tables
            def folder(acc: bool, e: bool) -> bool:
                if acc:
                    return e

                else: 
                    return False


            def _arrow508(__unit: None=None) -> IEnumerable_1[bool]:
                def _arrow507(i_1: int) -> bool:
                    return equals(item(i_1, a), item(i_1, b))

                return map_1(_arrow507, range_big_int(0, 1, length(a) - 1))

            return fold(folder, True, to_list(delay(_arrow508))) if (length(a) == length(b)) else False

        def _arrow512(__unit: None=None) -> bool:
            a_1: IEnumerable_1[Person] = this.Performers
            b_1: IEnumerable_1[Person] = other.Performers
            def folder_1(acc_1: bool, e_1: bool) -> bool:
                if acc_1:
                    return e_1

                else: 
                    return False


            def _arrow511(__unit: None=None) -> IEnumerable_1[bool]:
                def _arrow510(i_2: int) -> bool:
                    return equals(item(i_2, a_1), item(i_2, b_1))

                return map_1(_arrow510, range_big_int(0, 1, length(a_1) - 1))

            return fold(folder_1, True, to_list(delay(_arrow511))) if (length(a_1) == length(b_1)) else False

        def _arrow515(__unit: None=None) -> bool:
            a_2: IEnumerable_1[Comment] = this.Comments
            b_2: IEnumerable_1[Comment] = other.Comments
            def folder_2(acc_2: bool, e_2: bool) -> bool:
                if acc_2:
                    return e_2

                else: 
                    return False


            def _arrow514(__unit: None=None) -> IEnumerable_1[bool]:
                def _arrow513(i_3: int) -> bool:
                    return equals(item(i_3, a_2), item(i_3, b_2))

                return map_1(_arrow513, range_big_int(0, 1, length(a_2) - 1))

            return fold(folder_2, True, to_list(delay(_arrow514))) if (length(a_2) == length(b_2)) else False

        return for_all(predicate, to_enumerable([this.Identifier == other.Identifier, equals(this.Title, other.Title), equals(this.Description, other.Description), equals(this.MeasurementType, other.MeasurementType), equals(this.TechnologyType, other.TechnologyType), equals(this.TechnologyPlatform, other.TechnologyPlatform), equals(this.DataMap, other.DataMap), _arrow509(), _arrow512(), _arrow515()]))

    def ReferenceEquals(self, other: ArcAssay) -> bool:
        this: ArcAssay = self
        return this is other

    def __eq__(self, other: Any=None) -> bool:
        this: ArcAssay = self
        return this.StructurallyEquals(other) if isinstance(other, ArcAssay) else False

    def GetLightHashCode(self, __unit: None=None) -> Any:
        this: ArcAssay = self
        return box_hash_array([this.Identifier, box_hash_option(this.Title), box_hash_option(this.Description), box_hash_option(this.MeasurementType), box_hash_option(this.TechnologyType), box_hash_option(this.TechnologyPlatform), box_hash_seq(this.Tables), box_hash_seq(this.Performers), box_hash_seq(this.Comments)])

    def __hash__(self, __unit: None=None) -> Any:
        this: ArcAssay = self
        return box_hash_array([this.Identifier, box_hash_option(this.Title), box_hash_option(this.Description), box_hash_option(this.MeasurementType), box_hash_option(this.TechnologyType), box_hash_option(this.TechnologyPlatform), box_hash_option(this.DataMap), box_hash_seq(this.Tables), box_hash_seq(this.Performers), box_hash_seq(this.Comments)])


ArcAssay_reflection = _expr517

def ArcAssay__ctor_11E1F34(identifier: str, title: str | None=None, description: str | None=None, measurement_type: OntologyAnnotation | None=None, technology_type: OntologyAnnotation | None=None, technology_platform: OntologyAnnotation | None=None, tables: Array[ArcTable] | None=None, datamap: DataMap | None=None, performers: Array[Person] | None=None, comments: Array[Comment] | None=None) -> ArcAssay:
    return ArcAssay(identifier, title, description, measurement_type, technology_type, technology_platform, tables, datamap, performers, comments)


def _expr584() -> TypeInfo:
    return class_type("ARCtrl.ArcStudy", None, ArcStudy, ArcTables_reflection())


class ArcStudy(ArcTables):
    def __init__(self, identifier: str, title: str | None=None, description: str | None=None, submission_date: str | None=None, public_release_date: str | None=None, publications: Array[Publication] | None=None, contacts: Array[Person] | None=None, study_design_descriptors: Array[OntologyAnnotation] | None=None, tables: Array[ArcTable] | None=None, datamap: DataMap | None=None, registered_assay_identifiers: Array[str] | None=None, comments: Array[Comment] | None=None) -> None:
        super().__init__(default_arg(tables, []))
        publications_1: Array[Publication] = default_arg(publications, [])
        contacts_1: Array[Person] = default_arg(contacts, [])
        study_design_descriptors_1: Array[OntologyAnnotation] = default_arg(study_design_descriptors, [])
        registered_assay_identifiers_1: Array[str] = default_arg(registered_assay_identifiers, [])
        comments_1: Array[Comment] = default_arg(comments, [])
        def _arrow583(__unit: None=None) -> str:
            identifier_1: str = identifier.strip()
            check_valid_characters(identifier_1)
            return identifier_1

        self.identifier_0040579: str = _arrow583()
        self.investigation: ArcInvestigation | None = None
        self.title_0040584: str | None = title
        self.description_0040585: str | None = description
        self.submission_date_0040586: str | None = submission_date
        self.public_release_date_0040587: str | None = public_release_date
        self.publications_0040588_002D1: Array[Publication] = publications_1
        self.contacts_0040589_002D1: Array[Person] = contacts_1
        self.study_design_descriptors_0040590_002D1: Array[OntologyAnnotation] = study_design_descriptors_1
        self.datamap_0040591: DataMap | None = datamap
        self.registered_assay_identifiers_0040592_002D1: Array[str] = registered_assay_identifiers_1
        self.comments_0040593_002D1: Array[Comment] = comments_1
        self.static_hash: int = 0

    @property
    def Identifier(self, __unit: None=None) -> str:
        this: ArcStudy = self
        return this.identifier_0040579

    @Identifier.setter
    def Identifier(self, i: str) -> None:
        this: ArcStudy = self
        this.identifier_0040579 = i

    @property
    def Investigation(self, __unit: None=None) -> ArcInvestigation | None:
        this: ArcStudy = self
        return this.investigation

    @Investigation.setter
    def Investigation(self, i: ArcInvestigation | None=None) -> None:
        this: ArcStudy = self
        this.investigation = i

    @property
    def Title(self, __unit: None=None) -> str | None:
        this: ArcStudy = self
        return this.title_0040584

    @Title.setter
    def Title(self, n: str | None=None) -> None:
        this: ArcStudy = self
        this.title_0040584 = n

    @property
    def Description(self, __unit: None=None) -> str | None:
        this: ArcStudy = self
        return this.description_0040585

    @Description.setter
    def Description(self, n: str | None=None) -> None:
        this: ArcStudy = self
        this.description_0040585 = n

    @property
    def SubmissionDate(self, __unit: None=None) -> str | None:
        this: ArcStudy = self
        return this.submission_date_0040586

    @SubmissionDate.setter
    def SubmissionDate(self, n: str | None=None) -> None:
        this: ArcStudy = self
        this.submission_date_0040586 = n

    @property
    def PublicReleaseDate(self, __unit: None=None) -> str | None:
        this: ArcStudy = self
        return this.public_release_date_0040587

    @PublicReleaseDate.setter
    def PublicReleaseDate(self, n: str | None=None) -> None:
        this: ArcStudy = self
        this.public_release_date_0040587 = n

    @property
    def Publications(self, __unit: None=None) -> Array[Publication]:
        this: ArcStudy = self
        return this.publications_0040588_002D1

    @Publications.setter
    def Publications(self, n: Array[Publication]) -> None:
        this: ArcStudy = self
        this.publications_0040588_002D1 = n

    @property
    def Contacts(self, __unit: None=None) -> Array[Person]:
        this: ArcStudy = self
        return this.contacts_0040589_002D1

    @Contacts.setter
    def Contacts(self, n: Array[Person]) -> None:
        this: ArcStudy = self
        this.contacts_0040589_002D1 = n

    @property
    def StudyDesignDescriptors(self, __unit: None=None) -> Array[OntologyAnnotation]:
        this: ArcStudy = self
        return this.study_design_descriptors_0040590_002D1

    @StudyDesignDescriptors.setter
    def StudyDesignDescriptors(self, n: Array[OntologyAnnotation]) -> None:
        this: ArcStudy = self
        this.study_design_descriptors_0040590_002D1 = n

    @property
    def DataMap(self, __unit: None=None) -> DataMap | None:
        this: ArcStudy = self
        return this.datamap_0040591

    @DataMap.setter
    def DataMap(self, n: DataMap | None=None) -> None:
        this: ArcStudy = self
        this.datamap_0040591 = n

    @property
    def RegisteredAssayIdentifiers(self, __unit: None=None) -> Array[str]:
        this: ArcStudy = self
        return this.registered_assay_identifiers_0040592_002D1

    @RegisteredAssayIdentifiers.setter
    def RegisteredAssayIdentifiers(self, n: Array[str]) -> None:
        this: ArcStudy = self
        this.registered_assay_identifiers_0040592_002D1 = n

    @property
    def Comments(self, __unit: None=None) -> Array[Comment]:
        this: ArcStudy = self
        return this.comments_0040593_002D1

    @Comments.setter
    def Comments(self, n: Array[Comment]) -> None:
        this: ArcStudy = self
        this.comments_0040593_002D1 = n

    @property
    def StaticHash(self, __unit: None=None) -> int:
        this: ArcStudy = self
        return this.static_hash

    @StaticHash.setter
    def StaticHash(self, h: int) -> None:
        this: ArcStudy = self
        this.static_hash = h or 0

    @staticmethod
    def init(identifier: str) -> ArcStudy:
        return ArcStudy(identifier)

    @staticmethod
    def create(identifier: str, title: str | None=None, description: str | None=None, submission_date: str | None=None, public_release_date: str | None=None, publications: Array[Publication] | None=None, contacts: Array[Person] | None=None, study_design_descriptors: Array[OntologyAnnotation] | None=None, tables: Array[ArcTable] | None=None, datamap: DataMap | None=None, registered_assay_identifiers: Array[str] | None=None, comments: Array[Comment] | None=None) -> ArcStudy:
        return ArcStudy(identifier, title, description, submission_date, public_release_date, publications, contacts, study_design_descriptors, tables, datamap, registered_assay_identifiers, comments)

    @staticmethod
    def make(identifier: str, title: str | None, description: str | None, submission_date: str | None, public_release_date: str | None, publications: Array[Publication], contacts: Array[Person], study_design_descriptors: Array[OntologyAnnotation], tables: Array[ArcTable], datamap: DataMap | None, registered_assay_identifiers: Array[str], comments: Array[Comment]) -> ArcStudy:
        return ArcStudy(identifier, title, description, submission_date, public_release_date, publications, contacts, study_design_descriptors, tables, datamap, registered_assay_identifiers, comments)

    @property
    def is_empty(self, __unit: None=None) -> bool:
        this: ArcStudy = self
        return (len(this.Comments) == 0) if ((len(this.RegisteredAssayIdentifiers) == 0) if ((len(this.Tables) == 0) if ((len(this.StudyDesignDescriptors) == 0) if ((len(this.Contacts) == 0) if ((len(this.Publications) == 0) if (equals(this.PublicReleaseDate, None) if (equals(this.SubmissionDate, None) if (equals(this.Description, None) if equals(this.Title, None) else False) else False) else False) else False) else False) else False) else False) else False) else False

    @staticmethod
    def FileName() -> str:
        return "isa.study.xlsx"

    @property
    def RegisteredAssayIdentifierCount(self, __unit: None=None) -> int:
        this: ArcStudy = self
        return len(this.RegisteredAssayIdentifiers)

    @property
    def RegisteredAssayCount(self, __unit: None=None) -> int:
        this: ArcStudy = self
        return len(this.RegisteredAssays)

    @property
    def RegisteredAssays(self, __unit: None=None) -> Array[ArcAssay]:
        this: ArcStudy = self
        inv: ArcInvestigation
        investigation: ArcInvestigation | None = this.Investigation
        if investigation is not None:
            inv = investigation

        else: 
            raise Exception("Cannot execute this function. Object is not part of ArcInvestigation.")

        def chooser(assay_identifier: str) -> ArcAssay | None:
            return inv.TryGetAssay(assay_identifier)

        return list(choose(chooser, this.RegisteredAssayIdentifiers))

    @property
    def VacantAssayIdentifiers(self, __unit: None=None) -> Array[str]:
        this: ArcStudy = self
        inv: ArcInvestigation
        investigation: ArcInvestigation | None = this.Investigation
        if investigation is not None:
            inv = investigation

        else: 
            raise Exception("Cannot execute this function. Object is not part of ArcInvestigation.")

        def predicate(arg: str) -> bool:
            return not inv.ContainsAssay(arg)

        return list(filter(predicate, this.RegisteredAssayIdentifiers))

    def AddRegisteredAssay(self, assay: ArcAssay) -> None:
        this: ArcStudy = self
        inv: ArcInvestigation
        investigation: ArcInvestigation | None = this.Investigation
        if investigation is not None:
            inv = investigation

        else: 
            raise Exception("Cannot execute this function. Object is not part of ArcInvestigation.")

        inv.AddAssay(assay)
        inv.RegisterAssay(this.Identifier, assay.Identifier)

    @staticmethod
    def add_registered_assay(assay: ArcAssay) -> Callable[[ArcStudy], ArcStudy]:
        def _arrow518(study: ArcStudy) -> ArcStudy:
            new_study: ArcStudy = study.Copy()
            new_study.AddRegisteredAssay(assay)
            return new_study

        return _arrow518

    def InitRegisteredAssay(self, assay_identifier: str) -> ArcAssay:
        this: ArcStudy = self
        assay: ArcAssay = ArcAssay(assay_identifier)
        this.AddRegisteredAssay(assay)
        return assay

    @staticmethod
    def init_registered_assay(assay_identifier: str) -> Callable[[ArcStudy], tuple[ArcStudy, ArcAssay]]:
        def _arrow519(study: ArcStudy) -> tuple[ArcStudy, ArcAssay]:
            copy: ArcStudy = study.Copy()
            return (copy, copy.InitRegisteredAssay(assay_identifier))

        return _arrow519

    def RegisterAssay(self, assay_identifier: str) -> None:
        this: ArcStudy = self
        class ObjectExpr521:
            @property
            def Equals(self) -> Callable[[str, str], bool]:
                def _arrow520(x: str, y: str) -> bool:
                    return x == y

                return _arrow520

            @property
            def GetHashCode(self) -> Callable[[str], int]:
                return string_hash

        if contains(assay_identifier, this.RegisteredAssayIdentifiers, ObjectExpr521()):
            raise Exception(("Assay `" + assay_identifier) + "` is already registered on the study.")

        (this.RegisteredAssayIdentifiers.append(assay_identifier))

    @staticmethod
    def register_assay(assay_identifier: str) -> Callable[[ArcStudy], ArcStudy]:
        def _arrow522(study: ArcStudy) -> ArcStudy:
            copy: ArcStudy = study.Copy()
            copy.RegisterAssay(assay_identifier)
            return copy

        return _arrow522

    def DeregisterAssay(self, assay_identifier: str) -> None:
        this: ArcStudy = self
        class ObjectExpr524:
            @property
            def Equals(self) -> Callable[[str, str], bool]:
                def _arrow523(x: str, y: str) -> bool:
                    return x == y

                return _arrow523

            @property
            def GetHashCode(self) -> Callable[[str], int]:
                return string_hash

        ignore(remove_in_place(assay_identifier, this.RegisteredAssayIdentifiers, ObjectExpr524()))

    @staticmethod
    def deregister_assay(assay_identifier: str) -> Callable[[ArcStudy], ArcStudy]:
        def _arrow525(study: ArcStudy) -> ArcStudy:
            copy: ArcStudy = study.Copy()
            copy.DeregisterAssay(assay_identifier)
            return copy

        return _arrow525

    def GetRegisteredAssay(self, assay_identifier: str) -> ArcAssay:
        this: ArcStudy = self
        class ObjectExpr527:
            @property
            def Equals(self) -> Callable[[str, str], bool]:
                def _arrow526(x: str, y: str) -> bool:
                    return x == y

                return _arrow526

            @property
            def GetHashCode(self) -> Callable[[str], int]:
                return string_hash

        if not contains(assay_identifier, this.RegisteredAssayIdentifiers, ObjectExpr527()):
            raise Exception(("Assay `" + assay_identifier) + "` is not registered on the study.")

        inv: ArcInvestigation
        investigation: ArcInvestigation | None = this.Investigation
        if investigation is not None:
            inv = investigation

        else: 
            raise Exception("Cannot execute this function. Object is not part of ArcInvestigation.")

        return inv.GetAssay(assay_identifier)

    @staticmethod
    def get_registered_assay(assay_identifier: str) -> Callable[[ArcStudy], ArcAssay]:
        def _arrow528(study: ArcStudy) -> ArcAssay:
            copy: ArcStudy = study.Copy()
            return copy.GetRegisteredAssay(assay_identifier)

        return _arrow528

    @staticmethod
    def get_registered_assays(__unit: None=None) -> Callable[[ArcStudy], Array[ArcAssay]]:
        def _arrow529(study: ArcStudy) -> Array[ArcAssay]:
            copy: ArcStudy = study.Copy()
            return copy.RegisteredAssays

        return _arrow529

    def GetRegisteredAssaysOrIdentifier(self, __unit: None=None) -> Array[ArcAssay]:
        this: ArcStudy = self
        match_value: ArcInvestigation | None = this.Investigation
        if match_value is None:
            def f_1(identifier_1: str) -> ArcAssay:
                return ArcAssay.init(identifier_1)

            return ResizeArray_map(f_1, this.RegisteredAssayIdentifiers)

        else: 
            i: ArcInvestigation = match_value
            def f(identifier: str) -> ArcAssay:
                match_value_1: ArcAssay | None = i.TryGetAssay(identifier)
                if match_value_1 is None:
                    return ArcAssay.init(identifier)

                else: 
                    return match_value_1


            return ResizeArray_map(f, this.RegisteredAssayIdentifiers)


    @staticmethod
    def get_registered_assays_or_identifier(__unit: None=None) -> Callable[[ArcStudy], Array[ArcAssay]]:
        def _arrow530(study: ArcStudy) -> Array[ArcAssay]:
            copy: ArcStudy = study.Copy()
            return copy.GetRegisteredAssaysOrIdentifier()

        return _arrow530

    @staticmethod
    def add_table(table: ArcTable, index: int | None=None) -> Callable[[ArcStudy], ArcStudy]:
        def _arrow531(study: ArcStudy) -> ArcStudy:
            c: ArcStudy = study.Copy()
            c.AddTable(table, index)
            return c

        return _arrow531

    @staticmethod
    def add_tables(tables: IEnumerable_1[ArcTable], index: int | None=None) -> Callable[[ArcStudy], ArcStudy]:
        def _arrow532(study: ArcStudy) -> ArcStudy:
            c: ArcStudy = study.Copy()
            c.AddTables(tables, index)
            return c

        return _arrow532

    @staticmethod
    def init_table(table_name: str, index: int | None=None) -> Callable[[ArcStudy], tuple[ArcStudy, ArcTable]]:
        def _arrow533(study: ArcStudy) -> tuple[ArcStudy, ArcTable]:
            c: ArcStudy = study.Copy()
            return (c, c.InitTable(table_name, index))

        return _arrow533

    @staticmethod
    def init_tables(table_names: IEnumerable_1[str], index: int | None=None) -> Callable[[ArcStudy], ArcStudy]:
        def _arrow534(study: ArcStudy) -> ArcStudy:
            c: ArcStudy = study.Copy()
            c.InitTables(table_names, index)
            return c

        return _arrow534

    @staticmethod
    def get_table_at(index: int) -> Callable[[ArcStudy], ArcTable]:
        def _arrow535(study: ArcStudy) -> ArcTable:
            new_assay: ArcStudy = study.Copy()
            return new_assay.GetTableAt(index)

        return _arrow535

    @staticmethod
    def get_table(name: str) -> Callable[[ArcStudy], ArcTable]:
        def _arrow536(study: ArcStudy) -> ArcTable:
            new_assay: ArcStudy = study.Copy()
            return new_assay.GetTable(name)

        return _arrow536

    @staticmethod
    def update_table_at(index: int, table: ArcTable) -> Callable[[ArcStudy], ArcStudy]:
        def _arrow537(study: ArcStudy) -> ArcStudy:
            new_assay: ArcStudy = study.Copy()
            new_assay.UpdateTableAt(index, table)
            return new_assay

        return _arrow537

    @staticmethod
    def update_table(name: str, table: ArcTable) -> Callable[[ArcStudy], ArcStudy]:
        def _arrow538(study: ArcStudy) -> ArcStudy:
            new_assay: ArcStudy = study.Copy()
            new_assay.UpdateTable(name, table)
            return new_assay

        return _arrow538

    @staticmethod
    def set_table_at(index: int, table: ArcTable) -> Callable[[ArcStudy], ArcStudy]:
        def _arrow539(study: ArcStudy) -> ArcStudy:
            new_assay: ArcStudy = study.Copy()
            new_assay.SetTableAt(index, table)
            return new_assay

        return _arrow539

    @staticmethod
    def set_table(name: str, table: ArcTable) -> Callable[[ArcStudy], ArcStudy]:
        def _arrow540(study: ArcStudy) -> ArcStudy:
            new_assay: ArcStudy = study.Copy()
            new_assay.SetTable(name, table)
            return new_assay

        return _arrow540

    @staticmethod
    def remove_table_at(index: int) -> Callable[[ArcStudy], ArcStudy]:
        def _arrow541(study: ArcStudy) -> ArcStudy:
            new_assay: ArcStudy = study.Copy()
            new_assay.RemoveTableAt(index)
            return new_assay

        return _arrow541

    @staticmethod
    def remove_table(name: str) -> Callable[[ArcStudy], ArcStudy]:
        def _arrow542(study: ArcStudy) -> ArcStudy:
            new_assay: ArcStudy = study.Copy()
            new_assay.RemoveTable(name)
            return new_assay

        return _arrow542

    @staticmethod
    def map_table_at(index: int, update_fun: Callable[[ArcTable], None]) -> Callable[[ArcStudy], ArcStudy]:
        def _arrow543(study: ArcStudy) -> ArcStudy:
            new_assay: ArcStudy = study.Copy()
            new_assay.MapTableAt(index, update_fun)
            return new_assay

        return _arrow543

    @staticmethod
    def map_table(name: str, update_fun: Callable[[ArcTable], None]) -> Callable[[ArcStudy], ArcStudy]:
        def _arrow544(study: ArcStudy) -> ArcStudy:
            new_assay: ArcStudy = study.Copy()
            new_assay.MapTable(name, update_fun)
            return new_assay

        return _arrow544

    @staticmethod
    def rename_table_at(index: int, new_name: str) -> Callable[[ArcStudy], ArcStudy]:
        def _arrow545(study: ArcStudy) -> ArcStudy:
            new_assay: ArcStudy = study.Copy()
            new_assay.RenameTableAt(index, new_name)
            return new_assay

        return _arrow545

    @staticmethod
    def rename_table(name: str, new_name: str) -> Callable[[ArcStudy], ArcStudy]:
        def _arrow546(study: ArcStudy) -> ArcStudy:
            new_assay: ArcStudy = study.Copy()
            new_assay.RenameTable(name, new_name)
            return new_assay

        return _arrow546

    @staticmethod
    def add_column_at(table_index: int, header: CompositeHeader, cells: Array[CompositeCell] | None=None, column_index: int | None=None, force_replace: bool | None=None) -> Callable[[ArcStudy], ArcStudy]:
        def _arrow547(study: ArcStudy) -> ArcStudy:
            new_assay: ArcStudy = study.Copy()
            new_assay.AddColumnAt(table_index, header, cells, column_index, force_replace)
            return new_assay

        return _arrow547

    @staticmethod
    def add_column(table_name: str, header: CompositeHeader, cells: Array[CompositeCell] | None=None, column_index: int | None=None, force_replace: bool | None=None) -> Callable[[ArcStudy], ArcStudy]:
        def _arrow548(study: ArcStudy) -> ArcStudy:
            new_assay: ArcStudy = study.Copy()
            new_assay.AddColumn(table_name, header, cells, column_index, force_replace)
            return new_assay

        return _arrow548

    @staticmethod
    def remove_column_at(table_index: int, column_index: int) -> Callable[[ArcStudy], ArcStudy]:
        def _arrow549(study: ArcStudy) -> ArcStudy:
            new_assay: ArcStudy = study.Copy()
            new_assay.RemoveColumnAt(table_index, column_index)
            return new_assay

        return _arrow549

    @staticmethod
    def remove_column(table_name: str, column_index: int) -> Callable[[ArcStudy], ArcStudy]:
        def _arrow550(study: ArcStudy) -> ArcStudy:
            new_assay: ArcStudy = study.Copy()
            new_assay.RemoveColumn(table_name, column_index)
            return new_assay

        return _arrow550

    @staticmethod
    def update_column_at(table_index: int, column_index: int, header: CompositeHeader, cells: Array[CompositeCell] | None=None) -> Callable[[ArcStudy], ArcStudy]:
        def _arrow552(study: ArcStudy) -> ArcStudy:
            new_assay: ArcStudy = study.Copy()
            new_assay.UpdateColumnAt(table_index, column_index, header, cells)
            return new_assay

        return _arrow552

    @staticmethod
    def update_column(table_name: str, column_index: int, header: CompositeHeader, cells: Array[CompositeCell] | None=None) -> Callable[[ArcStudy], ArcStudy]:
        def _arrow554(study: ArcStudy) -> ArcStudy:
            new_assay: ArcStudy = study.Copy()
            new_assay.UpdateColumn(table_name, column_index, header, cells)
            return new_assay

        return _arrow554

    @staticmethod
    def get_column_at(table_index: int, column_index: int) -> Callable[[ArcStudy], CompositeColumn]:
        def _arrow555(study: ArcStudy) -> CompositeColumn:
            new_assay: ArcStudy = study.Copy()
            return new_assay.GetColumnAt(table_index, column_index)

        return _arrow555

    @staticmethod
    def get_column(table_name: str, column_index: int) -> Callable[[ArcStudy], CompositeColumn]:
        def _arrow556(study: ArcStudy) -> CompositeColumn:
            new_assay: ArcStudy = study.Copy()
            return new_assay.GetColumn(table_name, column_index)

        return _arrow556

    @staticmethod
    def add_row_at(table_index: int, cells: Array[CompositeCell] | None=None, row_index: int | None=None) -> Callable[[ArcStudy], ArcStudy]:
        def _arrow557(study: ArcStudy) -> ArcStudy:
            new_assay: ArcStudy = study.Copy()
            new_assay.AddRowAt(table_index, cells, row_index)
            return new_assay

        return _arrow557

    @staticmethod
    def add_row(table_name: str, cells: Array[CompositeCell] | None=None, row_index: int | None=None) -> Callable[[ArcStudy], ArcStudy]:
        def _arrow558(study: ArcStudy) -> ArcStudy:
            new_assay: ArcStudy = study.Copy()
            new_assay.AddRow(table_name, cells, row_index)
            return new_assay

        return _arrow558

    @staticmethod
    def remove_row_at(table_index: int, row_index: int) -> Callable[[ArcStudy], ArcStudy]:
        def _arrow559(study: ArcStudy) -> ArcStudy:
            new_assay: ArcStudy = study.Copy()
            new_assay.RemoveColumnAt(table_index, row_index)
            return new_assay

        return _arrow559

    @staticmethod
    def remove_row(table_name: str, row_index: int) -> Callable[[ArcStudy], ArcStudy]:
        def _arrow560(study: ArcStudy) -> ArcStudy:
            new_assay: ArcStudy = study.Copy()
            new_assay.RemoveRow(table_name, row_index)
            return new_assay

        return _arrow560

    @staticmethod
    def update_row_at(table_index: int, row_index: int, cells: Array[CompositeCell]) -> Callable[[ArcStudy], ArcStudy]:
        def _arrow561(study: ArcStudy) -> ArcStudy:
            new_assay: ArcStudy = study.Copy()
            new_assay.UpdateRowAt(table_index, row_index, cells)
            return new_assay

        return _arrow561

    @staticmethod
    def update_row(table_name: str, row_index: int, cells: Array[CompositeCell]) -> Callable[[ArcStudy], ArcStudy]:
        def _arrow562(study: ArcStudy) -> ArcStudy:
            new_assay: ArcStudy = study.Copy()
            new_assay.UpdateRow(table_name, row_index, cells)
            return new_assay

        return _arrow562

    @staticmethod
    def get_row_at(table_index: int, row_index: int) -> Callable[[ArcStudy], Array[CompositeCell]]:
        def _arrow563(study: ArcStudy) -> Array[CompositeCell]:
            new_assay: ArcStudy = study.Copy()
            return new_assay.GetRowAt(table_index, row_index)

        return _arrow563

    @staticmethod
    def get_row(table_name: str, row_index: int) -> Callable[[ArcStudy], Array[CompositeCell]]:
        def _arrow564(study: ArcStudy) -> Array[CompositeCell]:
            new_assay: ArcStudy = study.Copy()
            return new_assay.GetRow(table_name, row_index)

        return _arrow564

    def AddToInvestigation(self, investigation: ArcInvestigation) -> None:
        this: ArcStudy = self
        this.Investigation = investigation

    def RemoveFromInvestigation(self, __unit: None=None) -> None:
        this: ArcStudy = self
        this.Investigation = None

    def Copy(self, copy_investigation_ref: bool | None=None) -> ArcStudy:
        this: ArcStudy = self
        copy_investigation_ref_1: bool = default_arg(copy_investigation_ref, False)
        next_tables: Array[ArcTable] = []
        next_assay_identifiers: Array[str] = list(this.RegisteredAssayIdentifiers)
        enumerator: Any = get_enumerator(this.Tables)
        try: 
            while enumerator.System_Collections_IEnumerator_MoveNext():
                table: ArcTable = enumerator.System_Collections_Generic_IEnumerator_1_get_Current()
                copy: ArcTable = table.Copy()
                (next_tables.append(copy))

        finally: 
            dispose(enumerator)

        def f(c: Comment) -> Comment:
            return c.Copy()

        next_comments: Array[Comment] = ResizeArray_map(f, this.Comments)
        def f_1(c_1: Person) -> Person:
            return c_1.Copy()

        next_contacts: Array[Person] = ResizeArray_map(f_1, this.Contacts)
        def f_2(c_2: Publication) -> Publication:
            return c_2.Copy()

        next_publications: Array[Publication] = ResizeArray_map(f_2, this.Publications)
        def f_3(c_3: OntologyAnnotation) -> OntologyAnnotation:
            return c_3.Copy()

        next_study_design_descriptors: Array[OntologyAnnotation] = ResizeArray_map(f_3, this.StudyDesignDescriptors)
        def mapping(d: DataMap) -> DataMap:
            return d.Copy()

        next_data_map: DataMap | None = map(mapping, this.DataMap)
        study: ArcStudy
        identifier: str = this.Identifier
        title: str | None = this.Title
        description: str | None = this.Description
        submission_date: str | None = this.SubmissionDate
        public_release_date: str | None = this.PublicReleaseDate
        study = ArcStudy.make(identifier, title, description, submission_date, public_release_date, next_publications, next_contacts, next_study_design_descriptors, next_tables, next_data_map, next_assay_identifiers, next_comments)
        if copy_investigation_ref_1:
            study.Investigation = this.Investigation

        return study

    def UpdateReferenceByStudyFile(self, study: ArcStudy, only_replace_existing: bool | None=None, keep_unused_ref_tables: bool | None=None) -> None:
        this: ArcStudy = self
        update_always: bool = not default_arg(only_replace_existing, False)
        if True if (study.Title is not None) else update_always:
            this.Title = study.Title

        if True if (study.Description is not None) else update_always:
            this.Description = study.Description

        if True if (study.SubmissionDate is not None) else update_always:
            this.SubmissionDate = study.SubmissionDate

        if True if (study.PublicReleaseDate is not None) else update_always:
            this.PublicReleaseDate = study.PublicReleaseDate

        if True if (len(study.Publications) != 0) else update_always:
            this.Publications = study.Publications

        if True if (len(study.Contacts) != 0) else update_always:
            this.Contacts = study.Contacts

        if True if (len(study.StudyDesignDescriptors) != 0) else update_always:
            this.StudyDesignDescriptors = study.StudyDesignDescriptors

        if True if (len(study.Tables) != 0) else update_always:
            tables: ArcTables = ArcTables.update_reference_tables_by_sheets(ArcTables(this.Tables), ArcTables(study.Tables), keep_unused_ref_tables)
            this.Tables = tables.Tables

        this.DataMap = study.DataMap
        if True if (len(study.RegisteredAssayIdentifiers) != 0) else update_always:
            this.RegisteredAssayIdentifiers = study.RegisteredAssayIdentifiers

        if True if (len(study.Comments) != 0) else update_always:
            this.Comments = study.Comments


    def StructurallyEquals(self, other: ArcStudy) -> bool:
        this: ArcStudy = self
        def predicate(x: bool) -> bool:
            return x == True

        def _arrow567(__unit: None=None) -> bool:
            a: IEnumerable_1[Publication] = this.Publications
            b: IEnumerable_1[Publication] = other.Publications
            def folder(acc: bool, e: bool) -> bool:
                if acc:
                    return e

                else: 
                    return False


            def _arrow566(__unit: None=None) -> IEnumerable_1[bool]:
                def _arrow565(i_1: int) -> bool:
                    return equals(item(i_1, a), item(i_1, b))

                return map_1(_arrow565, range_big_int(0, 1, length(a) - 1))

            return fold(folder, True, to_list(delay(_arrow566))) if (length(a) == length(b)) else False

        def _arrow570(__unit: None=None) -> bool:
            a_1: IEnumerable_1[Person] = this.Contacts
            b_1: IEnumerable_1[Person] = other.Contacts
            def folder_1(acc_1: bool, e_1: bool) -> bool:
                if acc_1:
                    return e_1

                else: 
                    return False


            def _arrow569(__unit: None=None) -> IEnumerable_1[bool]:
                def _arrow568(i_2: int) -> bool:
                    return equals(item(i_2, a_1), item(i_2, b_1))

                return map_1(_arrow568, range_big_int(0, 1, length(a_1) - 1))

            return fold(folder_1, True, to_list(delay(_arrow569))) if (length(a_1) == length(b_1)) else False

        def _arrow573(__unit: None=None) -> bool:
            a_2: IEnumerable_1[OntologyAnnotation] = this.StudyDesignDescriptors
            b_2: IEnumerable_1[OntologyAnnotation] = other.StudyDesignDescriptors
            def folder_2(acc_2: bool, e_2: bool) -> bool:
                if acc_2:
                    return e_2

                else: 
                    return False


            def _arrow572(__unit: None=None) -> IEnumerable_1[bool]:
                def _arrow571(i_3: int) -> bool:
                    return equals(item(i_3, a_2), item(i_3, b_2))

                return map_1(_arrow571, range_big_int(0, 1, length(a_2) - 1))

            return fold(folder_2, True, to_list(delay(_arrow572))) if (length(a_2) == length(b_2)) else False

        def _arrow576(__unit: None=None) -> bool:
            a_3: IEnumerable_1[ArcTable] = this.Tables
            b_3: IEnumerable_1[ArcTable] = other.Tables
            def folder_3(acc_3: bool, e_3: bool) -> bool:
                if acc_3:
                    return e_3

                else: 
                    return False


            def _arrow575(__unit: None=None) -> IEnumerable_1[bool]:
                def _arrow574(i_4: int) -> bool:
                    return equals(item(i_4, a_3), item(i_4, b_3))

                return map_1(_arrow574, range_big_int(0, 1, length(a_3) - 1))

            return fold(folder_3, True, to_list(delay(_arrow575))) if (length(a_3) == length(b_3)) else False

        def _arrow579(__unit: None=None) -> bool:
            a_4: IEnumerable_1[str] = this.RegisteredAssayIdentifiers
            b_4: IEnumerable_1[str] = other.RegisteredAssayIdentifiers
            def folder_4(acc_4: bool, e_4: bool) -> bool:
                if acc_4:
                    return e_4

                else: 
                    return False


            def _arrow578(__unit: None=None) -> IEnumerable_1[bool]:
                def _arrow577(i_5: int) -> bool:
                    return item(i_5, a_4) == item(i_5, b_4)

                return map_1(_arrow577, range_big_int(0, 1, length(a_4) - 1))

            return fold(folder_4, True, to_list(delay(_arrow578))) if (length(a_4) == length(b_4)) else False

        def _arrow582(__unit: None=None) -> bool:
            a_5: IEnumerable_1[Comment] = this.Comments
            b_5: IEnumerable_1[Comment] = other.Comments
            def folder_5(acc_5: bool, e_5: bool) -> bool:
                if acc_5:
                    return e_5

                else: 
                    return False


            def _arrow581(__unit: None=None) -> IEnumerable_1[bool]:
                def _arrow580(i_6: int) -> bool:
                    return equals(item(i_6, a_5), item(i_6, b_5))

                return map_1(_arrow580, range_big_int(0, 1, length(a_5) - 1))

            return fold(folder_5, True, to_list(delay(_arrow581))) if (length(a_5) == length(b_5)) else False

        return for_all(predicate, to_enumerable([this.Identifier == other.Identifier, equals(this.Title, other.Title), equals(this.Description, other.Description), equals(this.SubmissionDate, other.SubmissionDate), equals(this.PublicReleaseDate, other.PublicReleaseDate), equals(this.DataMap, other.DataMap), _arrow567(), _arrow570(), _arrow573(), _arrow576(), _arrow579(), _arrow582()]))

    def ReferenceEquals(self, other: ArcStudy) -> bool:
        this: ArcStudy = self
        return this is other

    def __str__(self, __unit: None=None) -> str:
        this: ArcStudy = self
        arg: str = this.Identifier
        arg_1: str | None = this.Title
        arg_2: str | None = this.Description
        arg_3: str | None = this.SubmissionDate
        arg_4: str | None = this.PublicReleaseDate
        arg_5: Array[Publication] = this.Publications
        arg_6: Array[Person] = this.Contacts
        arg_7: Array[OntologyAnnotation] = this.StudyDesignDescriptors
        arg_8: Array[ArcTable] = this.Tables
        arg_9: Array[str] = this.RegisteredAssayIdentifiers
        arg_10: Array[Comment] = this.Comments
        return to_text(printf("ArcStudy {\r\n    Identifier = %A,\r\n    Title = %A,\r\n    Description = %A,\r\n    SubmissionDate = %A,\r\n    PublicReleaseDate = %A,\r\n    Publications = %A,\r\n    Contacts = %A,\r\n    StudyDesignDescriptors = %A,\r\n    Tables = %A,\r\n    RegisteredAssayIdentifiers = %A,\r\n    Comments = %A,\r\n}"))(arg)(arg_1)(arg_2)(arg_3)(arg_4)(arg_5)(arg_6)(arg_7)(arg_8)(arg_9)(arg_10)

    def __eq__(self, other: Any=None) -> bool:
        this: ArcStudy = self
        return this.StructurallyEquals(other) if isinstance(other, ArcStudy) else False

    def __hash__(self, __unit: None=None) -> Any:
        this: ArcStudy = self
        return box_hash_array([this.Identifier, box_hash_option(this.Title), box_hash_option(this.Description), box_hash_option(this.SubmissionDate), box_hash_option(this.PublicReleaseDate), box_hash_option(this.DataMap), box_hash_seq(this.Publications), box_hash_seq(this.Contacts), box_hash_seq(this.StudyDesignDescriptors), box_hash_seq(this.Tables), box_hash_seq(this.RegisteredAssayIdentifiers), box_hash_seq(this.Comments)])

    def GetLightHashCode(self, __unit: None=None) -> Any:
        this: ArcStudy = self
        return box_hash_array([this.Identifier, box_hash_option(this.Title), box_hash_option(this.Description), box_hash_option(this.SubmissionDate), box_hash_option(this.PublicReleaseDate), box_hash_seq(this.Publications), box_hash_seq(this.Contacts), box_hash_seq(this.StudyDesignDescriptors), box_hash_seq(this.Tables), box_hash_seq(this.RegisteredAssayIdentifiers), box_hash_seq(this.Comments)])


ArcStudy_reflection = _expr584

def ArcStudy__ctor_64321D5B(identifier: str, title: str | None=None, description: str | None=None, submission_date: str | None=None, public_release_date: str | None=None, publications: Array[Publication] | None=None, contacts: Array[Person] | None=None, study_design_descriptors: Array[OntologyAnnotation] | None=None, tables: Array[ArcTable] | None=None, datamap: DataMap | None=None, registered_assay_identifiers: Array[str] | None=None, comments: Array[Comment] | None=None) -> ArcStudy:
    return ArcStudy(identifier, title, description, submission_date, public_release_date, publications, contacts, study_design_descriptors, tables, datamap, registered_assay_identifiers, comments)


def _expr614() -> TypeInfo:
    return class_type("ARCtrl.ArcWorkflow", None, ArcWorkflow)


class ArcWorkflow:
    def __init__(self, identifier: str, title: str | None=None, description: str | None=None, workflow_type: OntologyAnnotation | None=None, uri: str | None=None, version: str | None=None, sub_workflow_identifiers: Array[str] | None=None, parameters: Array[ProtocolParameter] | None=None, components: Array[Component] | None=None, datamap: DataMap | None=None, contacts: Array[Person] | None=None, comments: Array[Comment] | None=None) -> None:
        def _arrow613(__unit: None=None) -> str:
            identifier_1: str = identifier.strip()
            check_valid_characters(identifier_1)
            return identifier_1

        self.identifier_00401151: str = _arrow613()
        self.investigation: ArcInvestigation | None = None
        self.title_00401156: str | None = title
        self.description_00401157: str | None = description
        self.sub_workflow_identifiers_00401158: Array[str] = default_arg(sub_workflow_identifiers, [])
        self.workflow_type_00401159: OntologyAnnotation | None = workflow_type
        self.uri_00401160: str | None = uri
        self.version_00401161: str | None = version
        self.parameters_00401162: Array[ProtocolParameter] = default_arg(parameters, [])
        self.components_00401163: Array[Component] = default_arg(components, [])
        self.data_map: DataMap | None = datamap
        self.contacts_00401165: Array[Person] = default_arg(contacts, [])
        self.comments_00401166: Array[Comment] = default_arg(comments, [])
        self.static_hash: int = 0

    @property
    def Identifier(self, __unit: None=None) -> str:
        this: ArcWorkflow = self
        return this.identifier_00401151

    @Identifier.setter
    def Identifier(self, i: str) -> None:
        this: ArcWorkflow = self
        this.identifier_00401151 = i

    @property
    def Investigation(self, __unit: None=None) -> ArcInvestigation | None:
        this: ArcWorkflow = self
        return this.investigation

    @Investigation.setter
    def Investigation(self, a: ArcInvestigation | None=None) -> None:
        this: ArcWorkflow = self
        this.investigation = a

    @property
    def Title(self, __unit: None=None) -> str | None:
        this: ArcWorkflow = self
        return this.title_00401156

    @Title.setter
    def Title(self, t: str | None=None) -> None:
        this: ArcWorkflow = self
        this.title_00401156 = t

    @property
    def Description(self, __unit: None=None) -> str | None:
        this: ArcWorkflow = self
        return this.description_00401157

    @Description.setter
    def Description(self, d: str | None=None) -> None:
        this: ArcWorkflow = self
        this.description_00401157 = d

    @property
    def SubWorkflowIdentifiers(self, __unit: None=None) -> Array[str]:
        this: ArcWorkflow = self
        return this.sub_workflow_identifiers_00401158

    @SubWorkflowIdentifiers.setter
    def SubWorkflowIdentifiers(self, s: Array[str]) -> None:
        this: ArcWorkflow = self
        this.sub_workflow_identifiers_00401158 = s

    @property
    def WorkflowType(self, __unit: None=None) -> OntologyAnnotation | None:
        this: ArcWorkflow = self
        return this.workflow_type_00401159

    @WorkflowType.setter
    def WorkflowType(self, w: OntologyAnnotation | None=None) -> None:
        this: ArcWorkflow = self
        this.workflow_type_00401159 = w

    @property
    def URI(self, __unit: None=None) -> str | None:
        this: ArcWorkflow = self
        return this.uri_00401160

    @URI.setter
    def URI(self, u: str | None=None) -> None:
        this: ArcWorkflow = self
        this.uri_00401160 = u

    @property
    def Version(self, __unit: None=None) -> str | None:
        this: ArcWorkflow = self
        return this.version_00401161

    @Version.setter
    def Version(self, v: str | None=None) -> None:
        this: ArcWorkflow = self
        this.version_00401161 = v

    @property
    def Parameters(self, __unit: None=None) -> Array[ProtocolParameter]:
        this: ArcWorkflow = self
        return this.parameters_00401162

    @Parameters.setter
    def Parameters(self, p: Array[ProtocolParameter]) -> None:
        this: ArcWorkflow = self
        this.parameters_00401162 = p

    @property
    def Components(self, __unit: None=None) -> Array[Component]:
        this: ArcWorkflow = self
        return this.components_00401163

    @Components.setter
    def Components(self, c: Array[Component]) -> None:
        this: ArcWorkflow = self
        this.components_00401163 = c

    @property
    def DataMap(self, __unit: None=None) -> DataMap | None:
        this: ArcWorkflow = self
        return this.data_map

    @DataMap.setter
    def DataMap(self, dm: DataMap | None=None) -> None:
        this: ArcWorkflow = self
        this.data_map = dm

    @property
    def Contacts(self, __unit: None=None) -> Array[Person]:
        this: ArcWorkflow = self
        return this.contacts_00401165

    @Contacts.setter
    def Contacts(self, c: Array[Person]) -> None:
        this: ArcWorkflow = self
        this.contacts_00401165 = c

    @property
    def Comments(self, __unit: None=None) -> Array[Comment]:
        this: ArcWorkflow = self
        return this.comments_00401166

    @Comments.setter
    def Comments(self, c: Array[Comment]) -> None:
        this: ArcWorkflow = self
        this.comments_00401166 = c

    @property
    def StaticHash(self, __unit: None=None) -> int:
        this: ArcWorkflow = self
        return this.static_hash

    @StaticHash.setter
    def StaticHash(self, s: int) -> None:
        this: ArcWorkflow = self
        this.static_hash = s or 0

    @staticmethod
    def init(identifier: str) -> ArcWorkflow:
        return ArcWorkflow(identifier)

    @staticmethod
    def create(identifier: str, title: str | None=None, description: str | None=None, workflow_type: OntologyAnnotation | None=None, uri: str | None=None, version: str | None=None, sub_workflow_identifiers: Array[str] | None=None, parameters: Array[ProtocolParameter] | None=None, components: Array[Component] | None=None, datamap: DataMap | None=None, contacts: Array[Person] | None=None, comments: Array[Comment] | None=None) -> ArcWorkflow:
        return ArcWorkflow(identifier, title, description, workflow_type, uri, version, sub_workflow_identifiers, parameters, components, datamap, contacts, comments)

    @staticmethod
    def make(identifier: str, title: str | None, description: str | None, workflow_type: OntologyAnnotation | None, uri: str | None, version: str | None, sub_workflow_identifiers: Array[str], parameters: Array[ProtocolParameter], components: Array[Component], datamap: DataMap | None, contacts: Array[Person], comments: Array[Comment]) -> ArcWorkflow:
        return ArcWorkflow(identifier, title, description, workflow_type, uri, version, sub_workflow_identifiers, parameters, components, datamap, contacts, comments)

    @staticmethod
    def FileName() -> str:
        return "isa.run.xlsx"

    @property
    def SubWorkflowIdentifiersCount(self, __unit: None=None) -> int:
        this: ArcWorkflow = self
        return len(this.SubWorkflowIdentifiers)

    @property
    def SubWorkflowCount(self, __unit: None=None) -> int:
        this: ArcWorkflow = self
        return len(this.SubWorkflows)

    @property
    def SubWorkflows(self, __unit: None=None) -> Array[ArcWorkflow]:
        this: ArcWorkflow = self
        inv: ArcInvestigation
        investigation: ArcInvestigation | None = this.Investigation
        if investigation is not None:
            inv = investigation

        else: 
            raise Exception("Cannot execute this function. Object is not part of ArcInvestigation.")

        def chooser(workflow_identifier: str) -> ArcWorkflow | None:
            return inv.TryGetWorkflow(workflow_identifier)

        return list(choose(chooser, this.SubWorkflowIdentifiers))

    @property
    def VacantSubWorkflowIdentifiers(self, __unit: None=None) -> Array[str]:
        this: ArcWorkflow = self
        inv: ArcInvestigation
        investigation: ArcInvestigation | None = this.Investigation
        if investigation is not None:
            inv = investigation

        else: 
            raise Exception("Cannot execute this function. Object is not part of ArcInvestigation.")

        def predicate(arg: str) -> bool:
            return not inv.ContainsWorkflow(arg)

        return list(filter(predicate, this.SubWorkflowIdentifiers))

    def AddSubWorkflow(self, sub_workflow: ArcWorkflow) -> None:
        this: ArcWorkflow = self
        inv: ArcInvestigation
        investigation: ArcInvestigation | None = this.Investigation
        if investigation is not None:
            inv = investigation

        else: 
            raise Exception("Cannot execute this function. Object is not part of ArcInvestigation.")

        inv.AddWorkflow(sub_workflow)

    @staticmethod
    def add_sub_workflow(sub_workflow: ArcWorkflow) -> Callable[[ArcWorkflow], ArcWorkflow]:
        def _arrow585(workflow: ArcWorkflow) -> ArcWorkflow:
            new_workflow: ArcWorkflow = workflow.Copy()
            new_workflow.AddSubWorkflow(sub_workflow)
            return new_workflow

        return _arrow585

    def InitSubWorkflow(self, sub_workflow_identifier: str) -> ArcWorkflow:
        this: ArcWorkflow = self
        sub_workflow: ArcWorkflow = ArcWorkflow(sub_workflow_identifier)
        this.AddSubWorkflow(sub_workflow)
        return sub_workflow

    @staticmethod
    def init_sub_workflow(sub_workflow_identifier: str) -> Callable[[ArcWorkflow], tuple[ArcWorkflow, ArcWorkflow]]:
        def _arrow586(workflow: ArcWorkflow) -> tuple[ArcWorkflow, ArcWorkflow]:
            copy: ArcWorkflow = workflow.Copy()
            return (copy, copy.InitSubWorkflow(sub_workflow_identifier))

        return _arrow586

    def RegisterSubWorkflow(self, sub_workflow_identifier: str) -> None:
        this: ArcWorkflow = self
        class ObjectExpr588:
            @property
            def Equals(self) -> Callable[[str, str], bool]:
                def _arrow587(x: str, y: str) -> bool:
                    return x == y

                return _arrow587

            @property
            def GetHashCode(self) -> Callable[[str], int]:
                return string_hash

        if contains(sub_workflow_identifier, this.SubWorkflowIdentifiers, ObjectExpr588()):
            raise Exception(("SubWorkflow `" + sub_workflow_identifier) + "` is already registered on the workflow.")

        (this.SubWorkflowIdentifiers.append(sub_workflow_identifier))

    @staticmethod
    def register_sub_workflow(sub_workflow_identifier: str) -> Callable[[ArcWorkflow], ArcWorkflow]:
        def _arrow589(workflow: ArcWorkflow) -> ArcWorkflow:
            copy: ArcWorkflow = workflow.Copy()
            copy.RegisterSubWorkflow(sub_workflow_identifier)
            return copy

        return _arrow589

    def DeregisterSubWorkflow(self, sub_workflow_identifier: str) -> None:
        this: ArcWorkflow = self
        class ObjectExpr591:
            @property
            def Equals(self) -> Callable[[str, str], bool]:
                def _arrow590(x: str, y: str) -> bool:
                    return x == y

                return _arrow590

            @property
            def GetHashCode(self) -> Callable[[str], int]:
                return string_hash

        ignore(remove_in_place(sub_workflow_identifier, this.SubWorkflowIdentifiers, ObjectExpr591()))

    @staticmethod
    def deregister_sub_workflow(sub_workflow_identifier: str) -> Callable[[ArcWorkflow], ArcWorkflow]:
        def _arrow592(workflow: ArcWorkflow) -> ArcWorkflow:
            copy: ArcWorkflow = workflow.Copy()
            copy.DeregisterSubWorkflow(sub_workflow_identifier)
            return copy

        return _arrow592

    def GetRegisteredSubWorkflow(self, sub_workflow_identifier: str) -> ArcWorkflow:
        this: ArcWorkflow = self
        class ObjectExpr594:
            @property
            def Equals(self) -> Callable[[str, str], bool]:
                def _arrow593(x: str, y: str) -> bool:
                    return x == y

                return _arrow593

            @property
            def GetHashCode(self) -> Callable[[str], int]:
                return string_hash

        if not contains(sub_workflow_identifier, this.SubWorkflowIdentifiers, ObjectExpr594()):
            raise Exception(("SubWorkflow `" + sub_workflow_identifier) + "` is not registered on the workflow.")

        inv: ArcInvestigation
        investigation: ArcInvestigation | None = this.Investigation
        if investigation is not None:
            inv = investigation

        else: 
            raise Exception("Cannot execute this function. Object is not part of ArcInvestigation.")

        return inv.GetWorkflow(sub_workflow_identifier)

    @staticmethod
    def get_registered_sub_workflow(sub_workflow_identifier: str) -> Callable[[ArcWorkflow], ArcWorkflow]:
        def _arrow595(workflow: ArcWorkflow) -> ArcWorkflow:
            copy: ArcWorkflow = workflow.Copy()
            return copy.GetRegisteredSubWorkflow(sub_workflow_identifier)

        return _arrow595

    @staticmethod
    def get_registered_sub_workflows(__unit: None=None) -> Callable[[ArcWorkflow], Array[ArcWorkflow]]:
        def _arrow596(workflow: ArcWorkflow) -> Array[ArcWorkflow]:
            copy: ArcWorkflow = workflow.Copy()
            return copy.SubWorkflows

        return _arrow596

    def GetRegisteredSubWorkflowsOrIdentifier(self, __unit: None=None) -> Array[ArcWorkflow]:
        this: ArcWorkflow = self
        match_value: ArcInvestigation | None = this.Investigation
        if match_value is None:
            def f_1(identifier_1: str) -> ArcWorkflow:
                return ArcWorkflow.init(identifier_1)

            return ResizeArray_map(f_1, this.SubWorkflowIdentifiers)

        else: 
            i: ArcInvestigation = match_value
            def f(identifier: str) -> ArcWorkflow:
                match_value_1: ArcWorkflow | None = i.TryGetWorkflow(identifier)
                if match_value_1 is None:
                    return ArcWorkflow.init(identifier)

                else: 
                    return match_value_1


            return ResizeArray_map(f, this.SubWorkflowIdentifiers)


    @staticmethod
    def get_registered_sub_workflows_or_identifier(__unit: None=None) -> Callable[[ArcWorkflow], Array[ArcWorkflow]]:
        def _arrow597(workflow: ArcWorkflow) -> Array[ArcWorkflow]:
            copy: ArcWorkflow = workflow.Copy()
            return copy.GetRegisteredSubWorkflowsOrIdentifier()

        return _arrow597

    def Copy(self, copy_investigation_ref: bool | None=None) -> ArcWorkflow:
        this: ArcWorkflow = self
        copy_investigation_ref_1: bool = default_arg(copy_investigation_ref, False)
        def mapping(w: OntologyAnnotation) -> OntologyAnnotation:
            return w.Copy()

        next_work_flow_type: OntologyAnnotation | None = map(mapping, this.WorkflowType)
        next_sub_workflow_identifiers: Array[str] = list(this.SubWorkflowIdentifiers)
        def f(x: ProtocolParameter) -> ProtocolParameter:
            return x

        next_parameters: Array[ProtocolParameter] = ResizeArray_map(f, this.Parameters)
        def f_1(x_1: Component) -> Component:
            return x_1

        next_components: Array[Component] = ResizeArray_map(f_1, this.Components)
        def mapping_1(d: DataMap) -> DataMap:
            return d.Copy()

        next_data_map: DataMap | None = map(mapping_1, this.DataMap)
        def f_2(c: Person) -> Person:
            return c.Copy()

        next_contacts: Array[Person] = ResizeArray_map(f_2, this.Contacts)
        def f_3(c_1: Comment) -> Comment:
            return c_1.Copy()

        next_comments: Array[Comment] = ResizeArray_map(f_3, this.Comments)
        workflow: ArcWorkflow
        identifier: str = this.Identifier
        title: str | None = this.Title
        description: str | None = this.Description
        uri: str | None = this.URI
        version: str | None = this.Version
        workflow = ArcWorkflow.make(identifier, title, description, next_work_flow_type, uri, version, next_sub_workflow_identifiers, next_parameters, next_components, next_data_map, next_contacts, next_comments)
        if copy_investigation_ref_1:
            workflow.Investigation = this.Investigation

        return workflow

    def StructurallyEquals(self, other: ArcWorkflow) -> bool:
        this: ArcWorkflow = self
        def predicate(x: bool) -> bool:
            return x == True

        def _arrow600(__unit: None=None) -> bool:
            a: IEnumerable_1[str] = this.SubWorkflowIdentifiers
            b: IEnumerable_1[str] = other.SubWorkflowIdentifiers
            def folder(acc: bool, e: bool) -> bool:
                if acc:
                    return e

                else: 
                    return False


            def _arrow599(__unit: None=None) -> IEnumerable_1[bool]:
                def _arrow598(i_1: int) -> bool:
                    return item(i_1, a) == item(i_1, b)

                return map_1(_arrow598, range_big_int(0, 1, length(a) - 1))

            return fold(folder, True, to_list(delay(_arrow599))) if (length(a) == length(b)) else False

        def _arrow603(__unit: None=None) -> bool:
            a_1: IEnumerable_1[ProtocolParameter] = this.Parameters
            b_1: IEnumerable_1[ProtocolParameter] = other.Parameters
            def folder_1(acc_1: bool, e_1: bool) -> bool:
                if acc_1:
                    return e_1

                else: 
                    return False


            def _arrow602(__unit: None=None) -> IEnumerable_1[bool]:
                def _arrow601(i_2: int) -> bool:
                    return equals(item(i_2, a_1), item(i_2, b_1))

                return map_1(_arrow601, range_big_int(0, 1, length(a_1) - 1))

            return fold(folder_1, True, to_list(delay(_arrow602))) if (length(a_1) == length(b_1)) else False

        def _arrow606(__unit: None=None) -> bool:
            a_2: IEnumerable_1[Component] = this.Components
            b_2: IEnumerable_1[Component] = other.Components
            def folder_2(acc_2: bool, e_2: bool) -> bool:
                if acc_2:
                    return e_2

                else: 
                    return False


            def _arrow605(__unit: None=None) -> IEnumerable_1[bool]:
                def _arrow604(i_3: int) -> bool:
                    return equals(item(i_3, a_2), item(i_3, b_2))

                return map_1(_arrow604, range_big_int(0, 1, length(a_2) - 1))

            return fold(folder_2, True, to_list(delay(_arrow605))) if (length(a_2) == length(b_2)) else False

        def _arrow609(__unit: None=None) -> bool:
            a_3: IEnumerable_1[Person] = this.Contacts
            b_3: IEnumerable_1[Person] = other.Contacts
            def folder_3(acc_3: bool, e_3: bool) -> bool:
                if acc_3:
                    return e_3

                else: 
                    return False


            def _arrow608(__unit: None=None) -> IEnumerable_1[bool]:
                def _arrow607(i_4: int) -> bool:
                    return equals(item(i_4, a_3), item(i_4, b_3))

                return map_1(_arrow607, range_big_int(0, 1, length(a_3) - 1))

            return fold(folder_3, True, to_list(delay(_arrow608))) if (length(a_3) == length(b_3)) else False

        def _arrow612(__unit: None=None) -> bool:
            a_4: IEnumerable_1[Comment] = this.Comments
            b_4: IEnumerable_1[Comment] = other.Comments
            def folder_4(acc_4: bool, e_4: bool) -> bool:
                if acc_4:
                    return e_4

                else: 
                    return False


            def _arrow611(__unit: None=None) -> IEnumerable_1[bool]:
                def _arrow610(i_5: int) -> bool:
                    return equals(item(i_5, a_4), item(i_5, b_4))

                return map_1(_arrow610, range_big_int(0, 1, length(a_4) - 1))

            return fold(folder_4, True, to_list(delay(_arrow611))) if (length(a_4) == length(b_4)) else False

        return for_all(predicate, to_enumerable([this.Identifier == other.Identifier, equals(this.Title, other.Title), equals(this.Description, other.Description), equals(this.WorkflowType, other.WorkflowType), equals(this.URI, other.URI), equals(this.Version, other.Version), _arrow600(), _arrow603(), _arrow606(), equals(this.DataMap, other.DataMap), _arrow609(), _arrow612()]))

    def ReferenceEquals(self, other: ArcStudy) -> bool:
        this: ArcWorkflow = self
        return this is other

    def __str__(self, __unit: None=None) -> str:
        this: ArcWorkflow = self
        arg: str = this.Identifier
        arg_1: str | None = this.Title
        arg_2: str | None = this.Description
        arg_3: OntologyAnnotation | None = this.WorkflowType
        arg_4: str | None = this.URI
        arg_5: str | None = this.Version
        arg_6: Array[str] = this.SubWorkflowIdentifiers
        arg_7: Array[ProtocolParameter] = this.Parameters
        arg_8: Array[Component] = this.Components
        arg_9: DataMap | None = this.DataMap
        arg_10: Array[Person] = this.Contacts
        arg_11: Array[Comment] = this.Comments
        return to_text(printf("ArcWorkflow {\r\n    Identifier = %A,\r\n    Title = %A,\r\n    Description = %A,\r\n    WorkflowType = %A,\r\n    URI = %A,\r\n    Version = %A,\r\n    SubWorkflowIdentifiers = %A,\r\n    Parameters = %A,\r\n    Components = %A,\r\n    DataMap = %A,\r\n    Contacts = %A,\r\n    Comments = %A}"))(arg)(arg_1)(arg_2)(arg_3)(arg_4)(arg_5)(arg_6)(arg_7)(arg_8)(arg_9)(arg_10)(arg_11)

    def __eq__(self, other: Any=None) -> bool:
        this: ArcWorkflow = self
        return this.StructurallyEquals(other) if isinstance(other, ArcWorkflow) else False

    def __hash__(self, __unit: None=None) -> Any:
        this: ArcWorkflow = self
        return box_hash_array([this.Identifier, box_hash_option(this.Title), box_hash_option(this.Description), box_hash_option(this.WorkflowType), box_hash_option(this.URI), box_hash_option(this.Version), box_hash_seq(this.SubWorkflowIdentifiers), box_hash_seq(this.Parameters), box_hash_seq(this.Components), box_hash_option(this.DataMap), box_hash_seq(this.Contacts), box_hash_seq(this.Comments)])

    def GetLightHashCode(self, __unit: None=None) -> Any:
        this: ArcWorkflow = self
        return box_hash_array([this.Identifier, box_hash_option(this.Title), box_hash_option(this.Description), box_hash_option(this.WorkflowType), box_hash_option(this.URI), box_hash_option(this.Version), box_hash_seq(this.SubWorkflowIdentifiers), box_hash_seq(this.Parameters), box_hash_seq(this.Components), box_hash_seq(this.Contacts), box_hash_seq(this.Comments)])


ArcWorkflow_reflection = _expr614

def ArcWorkflow__ctor_Z3BB02240(identifier: str, title: str | None=None, description: str | None=None, workflow_type: OntologyAnnotation | None=None, uri: str | None=None, version: str | None=None, sub_workflow_identifiers: Array[str] | None=None, parameters: Array[ProtocolParameter] | None=None, components: Array[Component] | None=None, datamap: DataMap | None=None, contacts: Array[Person] | None=None, comments: Array[Comment] | None=None) -> ArcWorkflow:
    return ArcWorkflow(identifier, title, description, workflow_type, uri, version, sub_workflow_identifiers, parameters, components, datamap, contacts, comments)


def _expr670() -> TypeInfo:
    return class_type("ARCtrl.ArcRun", None, ArcRun, ArcTables_reflection())


class ArcRun(ArcTables):
    def __init__(self, identifier: str, title: str | None=None, description: str | None=None, measurement_type: OntologyAnnotation | None=None, technology_type: OntologyAnnotation | None=None, technology_platform: OntologyAnnotation | None=None, workflow_identifiers: Array[str] | None=None, tables: Array[ArcTable] | None=None, datamap: DataMap | None=None, performers: Array[Person] | None=None, comments: Array[Comment] | None=None) -> None:
        super().__init__(default_arg(tables, []))
        performers_1: Array[Person] = default_arg(performers, [])
        comments_1: Array[Comment] = default_arg(comments, [])
        workflow_identifiers_1: Array[str] = default_arg(workflow_identifiers, [])
        def _arrow669(__unit: None=None) -> str:
            identifier_1: str = identifier.strip()
            check_valid_characters(identifier_1)
            return identifier_1

        self.identifier_00401447: str = _arrow669()
        self.title_00401451: str | None = title
        self.description_00401452: str | None = description
        self.investigation: ArcInvestigation | None = None
        self.measurement_type_00401454: OntologyAnnotation | None = measurement_type
        self.technology_type_00401455: OntologyAnnotation | None = technology_type
        self.technology_platform_00401456: OntologyAnnotation | None = technology_platform
        self.workflow_identifiers_00401457_002D1: Array[str] = workflow_identifiers_1
        self.data_map: DataMap | None = datamap
        self.performers_00401459_002D1: Array[Person] = performers_1
        self.comments_00401460_002D1: Array[Comment] = comments_1
        self.static_hash: int = 0

    @property
    def Identifier(self, __unit: None=None) -> str:
        this: ArcRun = self
        return this.identifier_00401447

    @Identifier.setter
    def Identifier(self, i: str) -> None:
        this: ArcRun = self
        this.identifier_00401447 = i

    @property
    def Investigation(self, __unit: None=None) -> ArcInvestigation | None:
        this: ArcRun = self
        return this.investigation

    @Investigation.setter
    def Investigation(self, i: ArcInvestigation | None=None) -> None:
        this: ArcRun = self
        this.investigation = i

    @property
    def Title(self, __unit: None=None) -> str | None:
        this: ArcRun = self
        return this.title_00401451

    @Title.setter
    def Title(self, t: str | None=None) -> None:
        this: ArcRun = self
        this.title_00401451 = t

    @property
    def Description(self, __unit: None=None) -> str | None:
        this: ArcRun = self
        return this.description_00401452

    @Description.setter
    def Description(self, d: str | None=None) -> None:
        this: ArcRun = self
        this.description_00401452 = d

    @property
    def MeasurementType(self, __unit: None=None) -> OntologyAnnotation | None:
        this: ArcRun = self
        return this.measurement_type_00401454

    @MeasurementType.setter
    def MeasurementType(self, n: OntologyAnnotation | None=None) -> None:
        this: ArcRun = self
        this.measurement_type_00401454 = n

    @property
    def TechnologyType(self, __unit: None=None) -> OntologyAnnotation | None:
        this: ArcRun = self
        return this.technology_type_00401455

    @TechnologyType.setter
    def TechnologyType(self, n: OntologyAnnotation | None=None) -> None:
        this: ArcRun = self
        this.technology_type_00401455 = n

    @property
    def TechnologyPlatform(self, __unit: None=None) -> OntologyAnnotation | None:
        this: ArcRun = self
        return this.technology_platform_00401456

    @TechnologyPlatform.setter
    def TechnologyPlatform(self, n: OntologyAnnotation | None=None) -> None:
        this: ArcRun = self
        this.technology_platform_00401456 = n

    @property
    def WorkflowIdentifiers(self, __unit: None=None) -> Array[str]:
        this: ArcRun = self
        return this.workflow_identifiers_00401457_002D1

    @WorkflowIdentifiers.setter
    def WorkflowIdentifiers(self, w: Array[str]) -> None:
        this: ArcRun = self
        this.workflow_identifiers_00401457_002D1 = w

    @property
    def DataMap(self, __unit: None=None) -> DataMap | None:
        this: ArcRun = self
        return this.data_map

    @DataMap.setter
    def DataMap(self, n: DataMap | None=None) -> None:
        this: ArcRun = self
        this.data_map = n

    @property
    def Performers(self, __unit: None=None) -> Array[Person]:
        this: ArcRun = self
        return this.performers_00401459_002D1

    @Performers.setter
    def Performers(self, n: Array[Person]) -> None:
        this: ArcRun = self
        this.performers_00401459_002D1 = n

    @property
    def Comments(self, __unit: None=None) -> Array[Comment]:
        this: ArcRun = self
        return this.comments_00401460_002D1

    @Comments.setter
    def Comments(self, n: Array[Comment]) -> None:
        this: ArcRun = self
        this.comments_00401460_002D1 = n

    @property
    def StaticHash(self, __unit: None=None) -> int:
        this: ArcRun = self
        return this.static_hash

    @StaticHash.setter
    def StaticHash(self, h: int) -> None:
        this: ArcRun = self
        this.static_hash = h or 0

    @staticmethod
    def init(identifier: str) -> ArcRun:
        return ArcRun(identifier)

    @staticmethod
    def create(identifier: str, title: str | None=None, description: str | None=None, measurement_type: OntologyAnnotation | None=None, technology_type: OntologyAnnotation | None=None, technology_platform: OntologyAnnotation | None=None, workflow_identifiers: Array[str] | None=None, tables: Array[ArcTable] | None=None, datamap: DataMap | None=None, performers: Array[Person] | None=None, comments: Array[Comment] | None=None) -> ArcRun:
        return ArcRun(identifier, title, description, measurement_type, technology_type, technology_platform, workflow_identifiers, tables, datamap, performers, comments)

    @staticmethod
    def make(identifier: str, title: str | None, description: str | None, measurement_type: OntologyAnnotation | None, technology_type: OntologyAnnotation | None, technology_platform: OntologyAnnotation | None, workflow_identifiers: Array[str], tables: Array[ArcTable], datamap: DataMap | None, performers: Array[Person], comments: Array[Comment]) -> ArcRun:
        return ArcRun(identifier, title, description, measurement_type, technology_type, technology_platform, workflow_identifiers, tables, datamap, performers, comments)

    @staticmethod
    def FileName() -> str:
        return "isa.run.xlsx"

    @property
    def WorkflowIdentifierCount(self, __unit: None=None) -> int:
        this: ArcRun = self
        return len(this.WorkflowIdentifiers)

    @property
    def WorkflowCount(self, __unit: None=None) -> int:
        this: ArcRun = self
        return len(this.Workflows)

    @property
    def Workflows(self, __unit: None=None) -> Array[ArcWorkflow]:
        this: ArcRun = self
        inv: ArcInvestigation
        investigation: ArcInvestigation | None = this.Investigation
        if investigation is not None:
            inv = investigation

        else: 
            raise Exception("Cannot execute this function. Object is not part of ArcInvestigation.")

        def chooser(workflow_identifier: str) -> ArcWorkflow | None:
            return inv.TryGetWorkflow(workflow_identifier)

        return list(choose(chooser, this.WorkflowIdentifiers))

    @property
    def VacantWorkflowIdentifiers(self, __unit: None=None) -> Array[str]:
        this: ArcRun = self
        inv: ArcInvestigation
        investigation: ArcInvestigation | None = this.Investigation
        if investigation is not None:
            inv = investigation

        else: 
            raise Exception("Cannot execute this function. Object is not part of ArcInvestigation.")

        def predicate(arg: str) -> bool:
            return not inv.ContainsWorkflow(arg)

        return list(filter(predicate, this.WorkflowIdentifiers))

    @staticmethod
    def add_table(table: ArcTable, index: int | None=None) -> Callable[[ArcRun], ArcRun]:
        def _arrow615(run: ArcRun) -> ArcRun:
            c: ArcRun = run.Copy()
            c.AddTable(table, index)
            return c

        return _arrow615

    @staticmethod
    def add_tables(tables: IEnumerable_1[ArcTable], index: int | None=None) -> Callable[[ArcRun], ArcRun]:
        def _arrow616(run: ArcRun) -> ArcRun:
            c: ArcRun = run.Copy()
            c.AddTables(tables, index)
            return c

        return _arrow616

    @staticmethod
    def init_table(table_name: str, index: int | None=None) -> Callable[[ArcRun], tuple[ArcRun, ArcTable]]:
        def _arrow617(run: ArcRun) -> tuple[ArcRun, ArcTable]:
            c: ArcRun = run.Copy()
            return (c, c.InitTable(table_name, index))

        return _arrow617

    @staticmethod
    def init_tables(table_names: IEnumerable_1[str], index: int | None=None) -> Callable[[ArcRun], ArcRun]:
        def _arrow618(run: ArcRun) -> ArcRun:
            c: ArcRun = run.Copy()
            c.InitTables(table_names, index)
            return c

        return _arrow618

    @staticmethod
    def get_table_at(index: int) -> Callable[[ArcRun], ArcTable]:
        def _arrow619(run: ArcRun) -> ArcTable:
            new_run: ArcRun = run.Copy()
            return new_run.GetTableAt(index)

        return _arrow619

    @staticmethod
    def get_table(name: str) -> Callable[[ArcRun], ArcTable]:
        def _arrow620(run: ArcRun) -> ArcTable:
            new_run: ArcRun = run.Copy()
            return new_run.GetTable(name)

        return _arrow620

    @staticmethod
    def update_table_at(index: int, table: ArcTable) -> Callable[[ArcRun], ArcRun]:
        def _arrow621(run: ArcRun) -> ArcRun:
            new_run: ArcRun = run.Copy()
            new_run.UpdateTableAt(index, table)
            return new_run

        return _arrow621

    @staticmethod
    def update_table(name: str, table: ArcTable) -> Callable[[ArcRun], ArcRun]:
        def _arrow622(run: ArcRun) -> ArcRun:
            new_run: ArcRun = run.Copy()
            new_run.UpdateTable(name, table)
            return new_run

        return _arrow622

    @staticmethod
    def set_table_at(index: int, table: ArcTable) -> Callable[[ArcRun], ArcRun]:
        def _arrow623(run: ArcRun) -> ArcRun:
            new_run: ArcRun = run.Copy()
            new_run.SetTableAt(index, table)
            return new_run

        return _arrow623

    @staticmethod
    def set_table(name: str, table: ArcTable) -> Callable[[ArcRun], ArcRun]:
        def _arrow624(run: ArcRun) -> ArcRun:
            new_run: ArcRun = run.Copy()
            new_run.SetTable(name, table)
            return new_run

        return _arrow624

    @staticmethod
    def remove_table_at(index: int) -> Callable[[ArcRun], ArcRun]:
        def _arrow625(run: ArcRun) -> ArcRun:
            new_run: ArcRun = run.Copy()
            new_run.RemoveTableAt(index)
            return new_run

        return _arrow625

    @staticmethod
    def remove_table(name: str) -> Callable[[ArcRun], ArcRun]:
        def _arrow626(run: ArcRun) -> ArcRun:
            new_run: ArcRun = run.Copy()
            new_run.RemoveTable(name)
            return new_run

        return _arrow626

    @staticmethod
    def map_table_at(index: int, update_fun: Callable[[ArcTable], None]) -> Callable[[ArcRun], ArcRun]:
        def _arrow627(run: ArcRun) -> ArcRun:
            new_run: ArcRun = run.Copy()
            new_run.MapTableAt(index, update_fun)
            return new_run

        return _arrow627

    @staticmethod
    def map_table(name: str, update_fun: Callable[[ArcTable], None]) -> Callable[[ArcRun], ArcRun]:
        def _arrow628(run: ArcRun) -> ArcRun:
            new_run: ArcRun = run.Copy()
            new_run.MapTable(name, update_fun)
            return new_run

        return _arrow628

    @staticmethod
    def rename_table_at(index: int, new_name: str) -> Callable[[ArcRun], ArcRun]:
        def _arrow629(run: ArcRun) -> ArcRun:
            new_run: ArcRun = run.Copy()
            new_run.RenameTableAt(index, new_name)
            return new_run

        return _arrow629

    @staticmethod
    def rename_table(name: str, new_name: str) -> Callable[[ArcRun], ArcRun]:
        def _arrow630(run: ArcRun) -> ArcRun:
            new_run: ArcRun = run.Copy()
            new_run.RenameTable(name, new_name)
            return new_run

        return _arrow630

    @staticmethod
    def add_column_at(table_index: int, header: CompositeHeader, cells: Array[CompositeCell] | None=None, column_index: int | None=None, force_replace: bool | None=None) -> Callable[[ArcRun], ArcRun]:
        def _arrow631(run: ArcRun) -> ArcRun:
            new_run: ArcRun = run.Copy()
            new_run.AddColumnAt(table_index, header, cells, column_index, force_replace)
            return new_run

        return _arrow631

    @staticmethod
    def add_column(table_name: str, header: CompositeHeader, cells: Array[CompositeCell] | None=None, column_index: int | None=None, force_replace: bool | None=None) -> Callable[[ArcRun], ArcRun]:
        def _arrow632(run: ArcRun) -> ArcRun:
            new_run: ArcRun = run.Copy()
            new_run.AddColumn(table_name, header, cells, column_index, force_replace)
            return new_run

        return _arrow632

    @staticmethod
    def remove_column_at(table_index: int, column_index: int) -> Callable[[ArcRun], ArcRun]:
        def _arrow633(run: ArcRun) -> ArcRun:
            new_run: ArcRun = run.Copy()
            new_run.RemoveColumnAt(table_index, column_index)
            return new_run

        return _arrow633

    @staticmethod
    def remove_column(table_name: str, column_index: int) -> Callable[[ArcRun], ArcRun]:
        def _arrow634(run: ArcRun) -> ArcRun:
            new_run: ArcRun = run.Copy()
            new_run.RemoveColumn(table_name, column_index)
            return new_run

        return _arrow634

    @staticmethod
    def update_column_at(table_index: int, column_index: int, header: CompositeHeader, cells: Array[CompositeCell] | None=None) -> Callable[[ArcRun], ArcRun]:
        def _arrow635(run: ArcRun) -> ArcRun:
            new_run: ArcRun = run.Copy()
            new_run.UpdateColumnAt(table_index, column_index, header, cells)
            return new_run

        return _arrow635

    @staticmethod
    def update_column(table_name: str, column_index: int, header: CompositeHeader, cells: Array[CompositeCell] | None=None) -> Callable[[ArcRun], ArcRun]:
        def _arrow636(run: ArcRun) -> ArcRun:
            new_run: ArcRun = run.Copy()
            new_run.UpdateColumn(table_name, column_index, header, cells)
            return new_run

        return _arrow636

    @staticmethod
    def get_column_at(table_index: int, column_index: int) -> Callable[[ArcRun], CompositeColumn]:
        def _arrow637(run: ArcRun) -> CompositeColumn:
            new_run: ArcRun = run.Copy()
            return new_run.GetColumnAt(table_index, column_index)

        return _arrow637

    @staticmethod
    def get_column(table_name: str, column_index: int) -> Callable[[ArcRun], CompositeColumn]:
        def _arrow638(run: ArcRun) -> CompositeColumn:
            new_run: ArcRun = run.Copy()
            return new_run.GetColumn(table_name, column_index)

        return _arrow638

    @staticmethod
    def add_row_at(table_index: int, cells: Array[CompositeCell] | None=None, row_index: int | None=None) -> Callable[[ArcRun], ArcRun]:
        def _arrow639(run: ArcRun) -> ArcRun:
            new_run: ArcRun = run.Copy()
            new_run.AddRowAt(table_index, cells, row_index)
            return new_run

        return _arrow639

    @staticmethod
    def add_row(table_name: str, cells: Array[CompositeCell] | None=None, row_index: int | None=None) -> Callable[[ArcRun], ArcRun]:
        def _arrow640(run: ArcRun) -> ArcRun:
            new_run: ArcRun = run.Copy()
            new_run.AddRow(table_name, cells, row_index)
            return new_run

        return _arrow640

    @staticmethod
    def remove_row_at(table_index: int, row_index: int) -> Callable[[ArcRun], ArcRun]:
        def _arrow641(run: ArcRun) -> ArcRun:
            new_run: ArcRun = run.Copy()
            new_run.RemoveColumnAt(table_index, row_index)
            return new_run

        return _arrow641

    @staticmethod
    def remove_row(table_name: str, row_index: int) -> Callable[[ArcRun], ArcRun]:
        def _arrow642(run: ArcRun) -> ArcRun:
            new_run: ArcRun = run.Copy()
            new_run.RemoveRow(table_name, row_index)
            return new_run

        return _arrow642

    @staticmethod
    def update_row_at(table_index: int, row_index: int, cells: Array[CompositeCell]) -> Callable[[ArcRun], ArcRun]:
        def _arrow643(run: ArcRun) -> ArcRun:
            new_run: ArcRun = run.Copy()
            new_run.UpdateRowAt(table_index, row_index, cells)
            return new_run

        return _arrow643

    @staticmethod
    def update_row(table_name: str, row_index: int, cells: Array[CompositeCell]) -> Callable[[ArcRun], ArcRun]:
        def _arrow644(run: ArcRun) -> ArcRun:
            new_run: ArcRun = run.Copy()
            new_run.UpdateRow(table_name, row_index, cells)
            return new_run

        return _arrow644

    @staticmethod
    def get_row_at(table_index: int, row_index: int) -> Callable[[ArcRun], Array[CompositeCell]]:
        def _arrow645(run: ArcRun) -> Array[CompositeCell]:
            new_run: ArcRun = run.Copy()
            return new_run.GetRowAt(table_index, row_index)

        return _arrow645

    @staticmethod
    def get_row(table_name: str, row_index: int) -> Callable[[ArcRun], Array[CompositeCell]]:
        def _arrow646(run: ArcRun) -> Array[CompositeCell]:
            new_run: ArcRun = run.Copy()
            return new_run.GetRow(table_name, row_index)

        return _arrow646

    @staticmethod
    def set_performers(performers: Array[Person], run: ArcRun) -> ArcRun:
        run.Performers = performers
        return run

    def Copy(self, __unit: None=None) -> ArcRun:
        this: ArcRun = self
        def f(c: ArcTable) -> ArcTable:
            return c.Copy()

        next_tables: Array[ArcTable] = ResizeArray_map(f, this.Tables)
        def f_1(c_1: Comment) -> Comment:
            return c_1.Copy()

        next_comments: Array[Comment] = ResizeArray_map(f_1, this.Comments)
        def mapping(d: DataMap) -> DataMap:
            return d.Copy()

        next_data_map: DataMap | None = map(mapping, this.DataMap)
        def f_2(c_2: Person) -> Person:
            return c_2.Copy()

        next_performers: Array[Person] = ResizeArray_map(f_2, this.Performers)
        def f_3(c_3: str) -> str:
            return c_3

        next_workflow_identifiers: Array[str] = ResizeArray_map(f_3, this.WorkflowIdentifiers)
        identifier: str = this.Identifier
        title: str | None = this.Title
        description: str | None = this.Description
        measurement_type: OntologyAnnotation | None = this.MeasurementType
        technology_type: OntologyAnnotation | None = this.TechnologyType
        technology_platform: OntologyAnnotation | None = this.TechnologyPlatform
        return ArcRun.make(identifier, title, description, measurement_type, technology_type, technology_platform, next_workflow_identifiers, next_tables, next_data_map, next_performers, next_comments)

    def UpdateBy(self, run: ArcRun, only_replace_existing: bool | None=None, append_sequences: bool | None=None) -> None:
        this: ArcRun = self
        only_replace_existing_1: bool = default_arg(only_replace_existing, False)
        append_sequences_1: bool = default_arg(append_sequences, False)
        update_always: bool = not only_replace_existing_1
        if True if (run.Title is not None) else update_always:
            this.Title = run.Title

        if True if (run.Description is not None) else update_always:
            this.Description = run.Description

        if True if (run.MeasurementType is not None) else update_always:
            this.MeasurementType = run.MeasurementType

        if True if (run.TechnologyType is not None) else update_always:
            this.TechnologyType = run.TechnologyType

        if True if (run.TechnologyPlatform is not None) else update_always:
            this.TechnologyPlatform = run.TechnologyPlatform

        if True if (len(run.WorkflowIdentifiers) != 0) else update_always:
            s: Array[str]
            origin: Array[str] = this.WorkflowIdentifiers
            next_1: Array[str] = run.WorkflowIdentifiers
            if not append_sequences_1:
                def f(x: str) -> str:
                    return x

                s = ResizeArray_map(f, next_1)

            else: 
                combined: Array[str] = []
                enumerator: Any = get_enumerator(origin)
                try: 
                    while enumerator.System_Collections_IEnumerator_MoveNext():
                        e: str = enumerator.System_Collections_Generic_IEnumerator_1_get_Current()
                        class ObjectExpr648:
                            @property
                            def Equals(self) -> Callable[[str, str], bool]:
                                def _arrow647(x_1: str, y: str) -> bool:
                                    return x_1 == y

                                return _arrow647

                            @property
                            def GetHashCode(self) -> Callable[[str], int]:
                                return string_hash

                        if not contains_1(e, combined, ObjectExpr648()):
                            (combined.append(e))


                finally: 
                    dispose(enumerator)

                enumerator_1: Any = get_enumerator(next_1)
                try: 
                    while enumerator_1.System_Collections_IEnumerator_MoveNext():
                        e_1: str = enumerator_1.System_Collections_Generic_IEnumerator_1_get_Current()
                        class ObjectExpr650:
                            @property
                            def Equals(self) -> Callable[[str, str], bool]:
                                def _arrow649(x_2: str, y_1: str) -> bool:
                                    return x_2 == y_1

                                return _arrow649

                            @property
                            def GetHashCode(self) -> Callable[[str], int]:
                                return string_hash

                        if not contains_1(e_1, combined, ObjectExpr650()):
                            (combined.append(e_1))


                finally: 
                    dispose(enumerator_1)

                s = combined

            this.WorkflowIdentifiers = s

        if True if (run.DataMap is not None) else update_always:
            this.DataMap = run.DataMap

        if True if (len(run.Tables) != 0) else update_always:
            s_1: Array[ArcTable]
            origin_1: Array[ArcTable] = this.Tables
            next_1_1: Array[ArcTable] = run.Tables
            if not append_sequences_1:
                def f_1(x_3: ArcTable) -> ArcTable:
                    return x_3

                s_1 = ResizeArray_map(f_1, next_1_1)

            else: 
                combined_1: Array[ArcTable] = []
                enumerator_2: Any = get_enumerator(origin_1)
                try: 
                    while enumerator_2.System_Collections_IEnumerator_MoveNext():
                        e_2: ArcTable = enumerator_2.System_Collections_Generic_IEnumerator_1_get_Current()
                        class ObjectExpr651:
                            @property
                            def Equals(self) -> Callable[[ArcTable, ArcTable], bool]:
                                return equals

                            @property
                            def GetHashCode(self) -> Callable[[ArcTable], int]:
                                return safe_hash

                        if not contains_1(e_2, combined_1, ObjectExpr651()):
                            (combined_1.append(e_2))


                finally: 
                    dispose(enumerator_2)

                enumerator_1_1: Any = get_enumerator(next_1_1)
                try: 
                    while enumerator_1_1.System_Collections_IEnumerator_MoveNext():
                        e_1_1: ArcTable = enumerator_1_1.System_Collections_Generic_IEnumerator_1_get_Current()
                        class ObjectExpr652:
                            @property
                            def Equals(self) -> Callable[[ArcTable, ArcTable], bool]:
                                return equals

                            @property
                            def GetHashCode(self) -> Callable[[ArcTable], int]:
                                return safe_hash

                        if not contains_1(e_1_1, combined_1, ObjectExpr652()):
                            (combined_1.append(e_1_1))


                finally: 
                    dispose(enumerator_1_1)

                s_1 = combined_1

            this.Tables = s_1

        if True if (len(run.Performers) != 0) else update_always:
            s_2: Array[Person]
            origin_2: Array[Person] = this.Performers
            next_1_2: Array[Person] = run.Performers
            if not append_sequences_1:
                def f_2(x_6: Person) -> Person:
                    return x_6

                s_2 = ResizeArray_map(f_2, next_1_2)

            else: 
                combined_2: Array[Person] = []
                enumerator_3: Any = get_enumerator(origin_2)
                try: 
                    while enumerator_3.System_Collections_IEnumerator_MoveNext():
                        e_3: Person = enumerator_3.System_Collections_Generic_IEnumerator_1_get_Current()
                        class ObjectExpr653:
                            @property
                            def Equals(self) -> Callable[[Person, Person], bool]:
                                return equals

                            @property
                            def GetHashCode(self) -> Callable[[Person], int]:
                                return safe_hash

                        if not contains_1(e_3, combined_2, ObjectExpr653()):
                            (combined_2.append(e_3))


                finally: 
                    dispose(enumerator_3)

                enumerator_1_2: Any = get_enumerator(next_1_2)
                try: 
                    while enumerator_1_2.System_Collections_IEnumerator_MoveNext():
                        e_1_2: Person = enumerator_1_2.System_Collections_Generic_IEnumerator_1_get_Current()
                        class ObjectExpr654:
                            @property
                            def Equals(self) -> Callable[[Person, Person], bool]:
                                return equals

                            @property
                            def GetHashCode(self) -> Callable[[Person], int]:
                                return safe_hash

                        if not contains_1(e_1_2, combined_2, ObjectExpr654()):
                            (combined_2.append(e_1_2))


                finally: 
                    dispose(enumerator_1_2)

                s_2 = combined_2

            this.Performers = s_2

        if True if (len(run.Comments) != 0) else update_always:
            s_3: Array[Comment]
            origin_3: Array[Comment] = this.Comments
            next_1_3: Array[Comment] = run.Comments
            if not append_sequences_1:
                def f_3(x_9: Comment) -> Comment:
                    return x_9

                s_3 = ResizeArray_map(f_3, next_1_3)

            else: 
                combined_3: Array[Comment] = []
                enumerator_4: Any = get_enumerator(origin_3)
                try: 
                    while enumerator_4.System_Collections_IEnumerator_MoveNext():
                        e_4: Comment = enumerator_4.System_Collections_Generic_IEnumerator_1_get_Current()
                        class ObjectExpr655:
                            @property
                            def Equals(self) -> Callable[[Comment, Comment], bool]:
                                return equals

                            @property
                            def GetHashCode(self) -> Callable[[Comment], int]:
                                return safe_hash

                        if not contains_1(e_4, combined_3, ObjectExpr655()):
                            (combined_3.append(e_4))


                finally: 
                    dispose(enumerator_4)

                enumerator_1_3: Any = get_enumerator(next_1_3)
                try: 
                    while enumerator_1_3.System_Collections_IEnumerator_MoveNext():
                        e_1_3: Comment = enumerator_1_3.System_Collections_Generic_IEnumerator_1_get_Current()
                        class ObjectExpr656:
                            @property
                            def Equals(self) -> Callable[[Comment, Comment], bool]:
                                return equals

                            @property
                            def GetHashCode(self) -> Callable[[Comment], int]:
                                return safe_hash

                        if not contains_1(e_1_3, combined_3, ObjectExpr656()):
                            (combined_3.append(e_1_3))


                finally: 
                    dispose(enumerator_1_3)

                s_3 = combined_3

            this.Comments = s_3


    def __str__(self, __unit: None=None) -> str:
        this: ArcRun = self
        arg: str = this.Identifier
        arg_1: str | None = this.Title
        arg_2: str | None = this.Description
        arg_3: OntologyAnnotation | None = this.MeasurementType
        arg_4: OntologyAnnotation | None = this.TechnologyType
        arg_5: OntologyAnnotation | None = this.TechnologyPlatform
        arg_6: Array[str] = this.WorkflowIdentifiers
        arg_7: DataMap | None = this.DataMap
        arg_8: Array[ArcTable] = this.Tables
        arg_9: Array[Person] = this.Performers
        arg_10: Array[Comment] = this.Comments
        return to_text(printf("ArcRun({\r\n    Identifier = \"%s\",\r\n    Title = %A,\r\n    Description = %A,\r\n    MeasurementType = %A,\r\n    TechnologyType = %A,\r\n    TechnologyPlatform = %A,\r\n    WorkflowIdentifiers = %A,\r\n    DataMap = %A,\r\n    Tables = %A,\r\n    Performers = %A,\r\n    Comments = %A\r\n})"))(arg)(arg_1)(arg_2)(arg_3)(arg_4)(arg_5)(arg_6)(arg_7)(arg_8)(arg_9)(arg_10)

    def AddToInvestigation(self, investigation: ArcInvestigation) -> None:
        this: ArcRun = self
        this.Investigation = investigation

    def RemoveFromInvestigation(self, __unit: None=None) -> None:
        this: ArcRun = self
        this.Investigation = None

    def StructurallyEquals(self, other: ArcRun) -> bool:
        this: ArcRun = self
        def predicate(x: bool) -> bool:
            return x == True

        def _arrow659(__unit: None=None) -> bool:
            a: IEnumerable_1[str] = this.WorkflowIdentifiers
            b: IEnumerable_1[str] = other.WorkflowIdentifiers
            def folder(acc: bool, e: bool) -> bool:
                if acc:
                    return e

                else: 
                    return False


            def _arrow658(__unit: None=None) -> IEnumerable_1[bool]:
                def _arrow657(i_1: int) -> bool:
                    return item(i_1, a) == item(i_1, b)

                return map_1(_arrow657, range_big_int(0, 1, length(a) - 1))

            return fold(folder, True, to_list(delay(_arrow658))) if (length(a) == length(b)) else False

        def _arrow662(__unit: None=None) -> bool:
            a_1: IEnumerable_1[ArcTable] = this.Tables
            b_1: IEnumerable_1[ArcTable] = other.Tables
            def folder_1(acc_1: bool, e_1: bool) -> bool:
                if acc_1:
                    return e_1

                else: 
                    return False


            def _arrow661(__unit: None=None) -> IEnumerable_1[bool]:
                def _arrow660(i_2: int) -> bool:
                    return equals(item(i_2, a_1), item(i_2, b_1))

                return map_1(_arrow660, range_big_int(0, 1, length(a_1) - 1))

            return fold(folder_1, True, to_list(delay(_arrow661))) if (length(a_1) == length(b_1)) else False

        def _arrow665(__unit: None=None) -> bool:
            a_2: IEnumerable_1[Person] = this.Performers
            b_2: IEnumerable_1[Person] = other.Performers
            def folder_2(acc_2: bool, e_2: bool) -> bool:
                if acc_2:
                    return e_2

                else: 
                    return False


            def _arrow664(__unit: None=None) -> IEnumerable_1[bool]:
                def _arrow663(i_3: int) -> bool:
                    return equals(item(i_3, a_2), item(i_3, b_2))

                return map_1(_arrow663, range_big_int(0, 1, length(a_2) - 1))

            return fold(folder_2, True, to_list(delay(_arrow664))) if (length(a_2) == length(b_2)) else False

        def _arrow668(__unit: None=None) -> bool:
            a_3: IEnumerable_1[Comment] = this.Comments
            b_3: IEnumerable_1[Comment] = other.Comments
            def folder_3(acc_3: bool, e_3: bool) -> bool:
                if acc_3:
                    return e_3

                else: 
                    return False


            def _arrow667(__unit: None=None) -> IEnumerable_1[bool]:
                def _arrow666(i_4: int) -> bool:
                    return equals(item(i_4, a_3), item(i_4, b_3))

                return map_1(_arrow666, range_big_int(0, 1, length(a_3) - 1))

            return fold(folder_3, True, to_list(delay(_arrow667))) if (length(a_3) == length(b_3)) else False

        return for_all(predicate, to_enumerable([this.Identifier == other.Identifier, equals(this.Title, other.Title), equals(this.Description, other.Description), equals(this.MeasurementType, other.MeasurementType), equals(this.TechnologyType, other.TechnologyType), equals(this.TechnologyPlatform, other.TechnologyPlatform), _arrow659(), equals(this.DataMap, other.DataMap), _arrow662(), _arrow665(), _arrow668()]))

    def ReferenceEquals(self, other: ArcRun) -> bool:
        this: ArcRun = self
        return this is other

    def __eq__(self, other: Any=None) -> bool:
        this: ArcRun = self
        return this.StructurallyEquals(other) if isinstance(other, ArcRun) else False

    def GetLightHashCode(self, __unit: None=None) -> Any:
        this: ArcRun = self
        return box_hash_array([this.Identifier, box_hash_option(this.Title), box_hash_option(this.Description), box_hash_option(this.MeasurementType), box_hash_option(this.TechnologyType), box_hash_option(this.TechnologyPlatform), box_hash_seq(this.WorkflowIdentifiers), box_hash_seq(this.Tables), box_hash_seq(this.Performers), box_hash_seq(this.Comments)])

    def __hash__(self, __unit: None=None) -> Any:
        this: ArcRun = self
        return box_hash_array([this.Identifier, box_hash_option(this.Title), box_hash_option(this.Description), box_hash_option(this.MeasurementType), box_hash_option(this.TechnologyType), box_hash_option(this.TechnologyPlatform), box_hash_option(this.DataMap), box_hash_seq(this.WorkflowIdentifiers), box_hash_seq(this.Tables), box_hash_seq(this.Performers), box_hash_seq(this.Comments)])


ArcRun_reflection = _expr670

def ArcRun__ctor_Z38E7054B(identifier: str, title: str | None=None, description: str | None=None, measurement_type: OntologyAnnotation | None=None, technology_type: OntologyAnnotation | None=None, technology_platform: OntologyAnnotation | None=None, workflow_identifiers: Array[str] | None=None, tables: Array[ArcTable] | None=None, datamap: DataMap | None=None, performers: Array[Person] | None=None, comments: Array[Comment] | None=None) -> ArcRun:
    return ArcRun(identifier, title, description, measurement_type, technology_type, technology_platform, workflow_identifiers, tables, datamap, performers, comments)


def _expr787() -> TypeInfo:
    return class_type("ARCtrl.ArcInvestigation", None, ArcInvestigation)


class ArcInvestigation:
    def __init__(self, identifier: str, title: str | None=None, description: str | None=None, submission_date: str | None=None, public_release_date: str | None=None, ontology_source_references: Array[OntologySourceReference] | None=None, publications: Array[Publication] | None=None, contacts: Array[Person] | None=None, assays: Array[ArcAssay] | None=None, studies: Array[ArcStudy] | None=None, workflows: Array[ArcWorkflow] | None=None, runs: Array[ArcRun] | None=None, registered_study_identifiers: Array[str] | None=None, comments: Array[Comment] | None=None, remarks: Array[Remark] | None=None) -> None:
        this: FSharpRef[ArcInvestigation] = FSharpRef(None)
        this.contents = self
        ontology_source_references_1: Array[OntologySourceReference] = default_arg(ontology_source_references, [])
        publications_1: Array[Publication] = default_arg(publications, [])
        contacts_1: Array[Person] = default_arg(contacts, [])
        assays_1: Array[ArcAssay]
        ass: Array[ArcAssay] = default_arg(assays, [])
        enumerator: Any = get_enumerator(ass)
        try: 
            while enumerator.System_Collections_IEnumerator_MoveNext():
                a: ArcAssay = enumerator.System_Collections_Generic_IEnumerator_1_get_Current()
                a.Investigation = this.contents

        finally: 
            dispose(enumerator)

        assays_1 = ass
        studies_1: Array[ArcStudy]
        sss: Array[ArcStudy] = default_arg(studies, [])
        enumerator_1: Any = get_enumerator(sss)
        try: 
            while enumerator_1.System_Collections_IEnumerator_MoveNext():
                s: ArcStudy = enumerator_1.System_Collections_Generic_IEnumerator_1_get_Current()
                s.Investigation = this.contents

        finally: 
            dispose(enumerator_1)

        studies_1 = sss
        workflows_1: Array[ArcWorkflow]
        wss: Array[ArcWorkflow] = default_arg(workflows, [])
        enumerator_2: Any = get_enumerator(wss)
        try: 
            while enumerator_2.System_Collections_IEnumerator_MoveNext():
                w: ArcWorkflow = enumerator_2.System_Collections_Generic_IEnumerator_1_get_Current()
                w.Investigation = this.contents

        finally: 
            dispose(enumerator_2)

        workflows_1 = wss
        runs_1: Array[ArcRun]
        rss: Array[ArcRun] = default_arg(runs, [])
        enumerator_3: Any = get_enumerator(rss)
        try: 
            while enumerator_3.System_Collections_IEnumerator_MoveNext():
                r: ArcRun = enumerator_3.System_Collections_Generic_IEnumerator_1_get_Current()
                r.Investigation = this.contents

        finally: 
            dispose(enumerator_3)

        runs_1 = rss
        registered_study_identifiers_1: Array[str] = default_arg(registered_study_identifiers, [])
        comments_1: Array[Comment] = default_arg(comments, [])
        remarks_1: Array[Remark] = default_arg(remarks, [])
        self.identifier_00401928: str = identifier
        self.title_00401929: str | None = title
        self.description_00401930: str | None = description
        self.submission_date_00401931: str | None = submission_date
        self.public_release_date_00401932: str | None = public_release_date
        self.ontology_source_references_00401933_002D1: Array[OntologySourceReference] = ontology_source_references_1
        self.publications_00401934_002D1: Array[Publication] = publications_1
        self.contacts_00401935_002D1: Array[Person] = contacts_1
        self.assays_00401936_002D1: Array[ArcAssay] = assays_1
        self.studies_00401937_002D1: Array[ArcStudy] = studies_1
        self.workflows_00401938_002D1: Array[ArcWorkflow] = workflows_1
        self.runs_00401939_002D1: Array[ArcRun] = runs_1
        self.registered_study_identifiers_00401940_002D1: Array[str] = registered_study_identifiers_1
        self.comments_00401941_002D1: Array[Comment] = comments_1
        self.remarks_00401942_002D1: Array[Remark] = remarks_1
        self.static_hash: int = 0
        self.init_00401899: int = 1

    @property
    def Identifier(self, __unit: None=None) -> str:
        this: ArcInvestigation = self
        return this.identifier_00401928

    @Identifier.setter
    def Identifier(self, i: str) -> None:
        this: ArcInvestigation = self
        this.identifier_00401928 = i

    @property
    def Title(self, __unit: None=None) -> str | None:
        this: ArcInvestigation = self
        return this.title_00401929

    @Title.setter
    def Title(self, n: str | None=None) -> None:
        this: ArcInvestigation = self
        this.title_00401929 = n

    @property
    def Description(self, __unit: None=None) -> str | None:
        this: ArcInvestigation = self
        return this.description_00401930

    @Description.setter
    def Description(self, n: str | None=None) -> None:
        this: ArcInvestigation = self
        this.description_00401930 = n

    @property
    def SubmissionDate(self, __unit: None=None) -> str | None:
        this: ArcInvestigation = self
        return this.submission_date_00401931

    @SubmissionDate.setter
    def SubmissionDate(self, n: str | None=None) -> None:
        this: ArcInvestigation = self
        this.submission_date_00401931 = n

    @property
    def PublicReleaseDate(self, __unit: None=None) -> str | None:
        this: ArcInvestigation = self
        return this.public_release_date_00401932

    @PublicReleaseDate.setter
    def PublicReleaseDate(self, n: str | None=None) -> None:
        this: ArcInvestigation = self
        this.public_release_date_00401932 = n

    @property
    def OntologySourceReferences(self, __unit: None=None) -> Array[OntologySourceReference]:
        this: ArcInvestigation = self
        return this.ontology_source_references_00401933_002D1

    @OntologySourceReferences.setter
    def OntologySourceReferences(self, n: Array[OntologySourceReference]) -> None:
        this: ArcInvestigation = self
        this.ontology_source_references_00401933_002D1 = n

    @property
    def Publications(self, __unit: None=None) -> Array[Publication]:
        this: ArcInvestigation = self
        return this.publications_00401934_002D1

    @Publications.setter
    def Publications(self, n: Array[Publication]) -> None:
        this: ArcInvestigation = self
        this.publications_00401934_002D1 = n

    @property
    def Contacts(self, __unit: None=None) -> Array[Person]:
        this: ArcInvestigation = self
        return this.contacts_00401935_002D1

    @Contacts.setter
    def Contacts(self, n: Array[Person]) -> None:
        this: ArcInvestigation = self
        this.contacts_00401935_002D1 = n

    @property
    def Assays(self, __unit: None=None) -> Array[ArcAssay]:
        this: ArcInvestigation = self
        return this.assays_00401936_002D1

    @Assays.setter
    def Assays(self, n: Array[ArcAssay]) -> None:
        this: ArcInvestigation = self
        this.assays_00401936_002D1 = n

    @property
    def Studies(self, __unit: None=None) -> Array[ArcStudy]:
        this: ArcInvestigation = self
        return this.studies_00401937_002D1

    @Studies.setter
    def Studies(self, n: Array[ArcStudy]) -> None:
        this: ArcInvestigation = self
        this.studies_00401937_002D1 = n

    @property
    def Workflows(self, __unit: None=None) -> Array[ArcWorkflow]:
        this: ArcInvestigation = self
        return this.workflows_00401938_002D1

    @Workflows.setter
    def Workflows(self, n: Array[ArcWorkflow]) -> None:
        this: ArcInvestigation = self
        this.workflows_00401938_002D1 = n

    @property
    def Runs(self, __unit: None=None) -> Array[ArcRun]:
        this: ArcInvestigation = self
        return this.runs_00401939_002D1

    @Runs.setter
    def Runs(self, n: Array[ArcRun]) -> None:
        this: ArcInvestigation = self
        this.runs_00401939_002D1 = n

    @property
    def RegisteredStudyIdentifiers(self, __unit: None=None) -> Array[str]:
        this: ArcInvestigation = self
        return this.registered_study_identifiers_00401940_002D1

    @RegisteredStudyIdentifiers.setter
    def RegisteredStudyIdentifiers(self, n: Array[str]) -> None:
        this: ArcInvestigation = self
        this.registered_study_identifiers_00401940_002D1 = n

    @property
    def Comments(self, __unit: None=None) -> Array[Comment]:
        this: ArcInvestigation = self
        return this.comments_00401941_002D1

    @Comments.setter
    def Comments(self, n: Array[Comment]) -> None:
        this: ArcInvestigation = self
        this.comments_00401941_002D1 = n

    @property
    def Remarks(self, __unit: None=None) -> Array[Remark]:
        this: ArcInvestigation = self
        return this.remarks_00401942_002D1

    @Remarks.setter
    def Remarks(self, n: Array[Remark]) -> None:
        this: ArcInvestigation = self
        this.remarks_00401942_002D1 = n

    @property
    def StaticHash(self, __unit: None=None) -> int:
        this: ArcInvestigation = self
        return this.static_hash

    @StaticHash.setter
    def StaticHash(self, h: int) -> None:
        this: ArcInvestigation = self
        this.static_hash = h or 0

    @staticmethod
    def FileName() -> str:
        return "isa.investigation.xlsx"

    @staticmethod
    def init(identifier: str) -> ArcInvestigation:
        return ArcInvestigation(identifier)

    @staticmethod
    def create(identifier: str, title: str | None=None, description: str | None=None, submission_date: str | None=None, public_release_date: str | None=None, ontology_source_references: Array[OntologySourceReference] | None=None, publications: Array[Publication] | None=None, contacts: Array[Person] | None=None, assays: Array[ArcAssay] | None=None, studies: Array[ArcStudy] | None=None, workflows: Array[ArcWorkflow] | None=None, runs: Array[ArcRun] | None=None, registered_study_identifiers: Array[str] | None=None, comments: Array[Comment] | None=None, remarks: Array[Remark] | None=None) -> ArcInvestigation:
        return ArcInvestigation(identifier, title, description, submission_date, public_release_date, ontology_source_references, publications, contacts, assays, studies, workflows, runs, registered_study_identifiers, comments, remarks)

    @staticmethod
    def make(identifier: str, title: str | None, description: str | None, submission_date: str | None, public_release_date: str | None, ontology_source_references: Array[OntologySourceReference], publications: Array[Publication], contacts: Array[Person], assays: Array[ArcAssay], studies: Array[ArcStudy], workflows: Array[ArcWorkflow], runs: Array[ArcRun], registered_study_identifiers: Array[str], comments: Array[Comment], remarks: Array[Remark]) -> ArcInvestigation:
        return ArcInvestigation(identifier, title, description, submission_date, public_release_date, ontology_source_references, publications, contacts, assays, studies, workflows, runs, registered_study_identifiers, comments, remarks)

    @property
    def AssayCount(self, __unit: None=None) -> int:
        this: ArcInvestigation = self
        return len(this.Assays)

    @property
    def AssayIdentifiers(self, __unit: None=None) -> Array[str]:
        this: ArcInvestigation = self
        def mapping(x: ArcAssay) -> str:
            return x.Identifier

        return list(map_1(mapping, this.Assays))

    @property
    def UnregisteredAssays(self, __unit: None=None) -> Array[ArcAssay]:
        this: ArcInvestigation = self
        def f(a: ArcAssay) -> bool:
            def predicate(s: ArcStudy, a: Any=a) -> bool:
                def _arrow671(i: str, s: Any=s) -> bool:
                    return i == a.Identifier

                return exists(_arrow671, s.RegisteredAssayIdentifiers)

            return not exists(predicate, this.RegisteredStudies)

        return ResizeArray_filter(f, this.Assays)

    def AddAssay(self, assay: ArcAssay, register_in: Array[ArcStudy] | None=None) -> None:
        this: ArcInvestigation = self
        assay_ident: str = assay.Identifier
        def predicate(x_1: str) -> bool:
            return x_1 == assay_ident

        def mapping(x: ArcAssay) -> str:
            return x.Identifier

        match_value: int | None = try_find_index(predicate, map_1(mapping, this.Assays))
        if match_value is None:
            pass

        else: 
            raise Exception(((("Cannot create assay with name " + assay_ident) + ", as assay names must be unique and assay at index ") + str(match_value)) + " has the same name.")

        assay.Investigation = this
        (this.Assays.append(assay))
        if register_in is not None:
            enumerator: Any = get_enumerator(value_5(register_in))
            try: 
                while enumerator.System_Collections_IEnumerator_MoveNext():
                    study: ArcStudy = enumerator.System_Collections_Generic_IEnumerator_1_get_Current()
                    study.RegisterAssay(assay.Identifier)

            finally: 
                dispose(enumerator)



    @staticmethod
    def add_assay(assay: ArcAssay, register_in: Array[ArcStudy] | None=None) -> Callable[[ArcInvestigation], ArcInvestigation]:
        def _arrow672(inv: ArcInvestigation) -> ArcInvestigation:
            new_investigation: ArcInvestigation = inv.Copy()
            new_investigation.AddAssay(assay, register_in)
            return new_investigation

        return _arrow672

    def InitAssay(self, assay_identifier: str, register_in: Array[ArcStudy] | None=None) -> ArcAssay:
        this: ArcInvestigation = self
        assay: ArcAssay = ArcAssay(assay_identifier)
        this.AddAssay(assay, register_in)
        return assay

    @staticmethod
    def init_assay(assay_identifier: str, register_in: Array[ArcStudy] | None=None) -> Callable[[ArcInvestigation], ArcAssay]:
        def _arrow673(inv: ArcInvestigation) -> ArcAssay:
            new_investigation: ArcInvestigation = inv.Copy()
            return new_investigation.InitAssay(assay_identifier, register_in)

        return _arrow673

    def DeleteAssayAt(self, index: int) -> None:
        this: ArcInvestigation = self
        this.Assays.pop(index)

    @staticmethod
    def delete_assay_at(index: int) -> Callable[[ArcInvestigation], ArcInvestigation]:
        def _arrow674(inv: ArcInvestigation) -> ArcInvestigation:
            new_investigation: ArcInvestigation = inv.Copy()
            new_investigation.DeleteAssayAt(index)
            return new_investigation

        return _arrow674

    def DeleteAssay(self, assay_identifier: str) -> None:
        this: ArcInvestigation = self
        index: int = this.GetAssayIndex(assay_identifier) or 0
        this.DeleteAssayAt(index)

    @staticmethod
    def delete_assay(assay_identifier: str) -> Callable[[ArcInvestigation], ArcInvestigation]:
        def _arrow675(inv: ArcInvestigation) -> ArcInvestigation:
            new_inv: ArcInvestigation = inv.Copy()
            new_inv.DeleteAssay(assay_identifier)
            return new_inv

        return _arrow675

    def RemoveAssayAt(self, index: int) -> None:
        this: ArcInvestigation = self
        ident: str = this.GetAssayAt(index).Identifier
        this.Assays.pop(index)
        enumerator: Any = get_enumerator(this.Studies)
        try: 
            while enumerator.System_Collections_IEnumerator_MoveNext():
                study: ArcStudy = enumerator.System_Collections_Generic_IEnumerator_1_get_Current()
                study.DeregisterAssay(ident)

        finally: 
            dispose(enumerator)


    @staticmethod
    def remove_assay_at(index: int) -> Callable[[ArcInvestigation], ArcInvestigation]:
        def _arrow676(inv: ArcInvestigation) -> ArcInvestigation:
            new_investigation: ArcInvestigation = inv.Copy()
            new_investigation.RemoveAssayAt(index)
            return new_investigation

        return _arrow676

    def RemoveAssay(self, assay_identifier: str) -> None:
        this: ArcInvestigation = self
        index: int = this.GetAssayIndex(assay_identifier) or 0
        this.RemoveAssayAt(index)

    @staticmethod
    def remove_assay(assay_identifier: str) -> Callable[[ArcInvestigation], ArcInvestigation]:
        def _arrow677(inv: ArcInvestigation) -> ArcInvestigation:
            new_inv: ArcInvestigation = inv.Copy()
            new_inv.RemoveAssay(assay_identifier)
            return new_inv

        return _arrow677

    def RenameAssay(self, old_identifier: str, new_identifier: str) -> None:
        this: ArcInvestigation = self
        def action(a: ArcAssay) -> None:
            if a.Identifier == old_identifier:
                a.Identifier = new_identifier


        iterate(action, this.Assays)
        def action_1(s: ArcStudy) -> None:
            def predicate(ai: str, s: Any=s) -> bool:
                return ai == old_identifier

            index: int | None = try_find_index(predicate, s.RegisteredAssayIdentifiers)
            if index is not None:
                index_1: int = index or 0
                s.RegisteredAssayIdentifiers[index_1] = new_identifier


        iterate(action_1, this.Studies)

    @staticmethod
    def rename_assay(old_identifier: str, new_identifier: str) -> Callable[[ArcInvestigation], ArcInvestigation]:
        def _arrow678(inv: ArcInvestigation) -> ArcInvestigation:
            new_inv: ArcInvestigation = inv.Copy()
            new_inv.RenameAssay(old_identifier, new_identifier)
            return new_inv

        return _arrow678

    def RenameRun(self, old_identifier: str, new_identifier: str) -> None:
        this: ArcInvestigation = self
        def action(a: ArcRun) -> None:
            if a.Identifier == old_identifier:
                a.Identifier = new_identifier


        iterate(action, this.Runs)

    @staticmethod
    def rename_run(old_identifier: str, new_identifier: str) -> Callable[[ArcInvestigation], ArcInvestigation]:
        def _arrow679(inv: ArcInvestigation) -> ArcInvestigation:
            new_inv: ArcInvestigation = inv.Copy()
            new_inv.RenameRun(old_identifier, new_identifier)
            return new_inv

        return _arrow679

    def RenameWorkflow(self, old_identifier: str, new_identifier: str) -> None:
        this: ArcInvestigation = self
        def action(w: ArcWorkflow) -> None:
            if w.Identifier == old_identifier:
                w.Identifier = new_identifier

            def predicate(sub_id: str, w: Any=w) -> bool:
                return sub_id == old_identifier

            match_value: int | None = try_find_index(predicate, w.SubWorkflowIdentifiers)
            if match_value is not None:
                i: int = match_value or 0
                w.SubWorkflowIdentifiers[i] = new_identifier


        iterate(action, this.Workflows)
        def action_1(r: ArcRun) -> None:
            def predicate_1(w_id: str, r: Any=r) -> bool:
                return w_id == old_identifier

            match_value_1: int | None = try_find_index(predicate_1, r.WorkflowIdentifiers)
            if match_value_1 is not None:
                i_1: int = match_value_1 or 0
                r.WorkflowIdentifiers[i_1] = new_identifier


        iterate(action_1, this.Runs)

    @staticmethod
    def rename_workflow(old_identifier: str, new_identifier: str) -> Callable[[ArcInvestigation], ArcInvestigation]:
        def _arrow680(inv: ArcInvestigation) -> ArcInvestigation:
            new_inv: ArcInvestigation = inv.Copy()
            new_inv.RenameWorkflow(old_identifier, new_identifier)
            return new_inv

        return _arrow680

    def SetAssayAt(self, index: int, assay: ArcAssay) -> None:
        this: ArcInvestigation = self
        assay_ident: str = assay.Identifier
        def predicate(x: str) -> bool:
            return x == assay_ident

        def mapping(a: ArcAssay) -> str:
            return a.Identifier

        match_value: int | None = try_find_index(predicate, map_1(mapping, remove_at(index, this.Assays)))
        if match_value is None:
            pass

        else: 
            raise Exception(((("Cannot create assay with name " + assay_ident) + ", as assay names must be unique and assay at index ") + str(match_value)) + " has the same name.")

        assay.Investigation = this
        this.Assays[index] = assay
        this.DeregisterMissingAssays()

    @staticmethod
    def set_assay_at(index: int, assay: ArcAssay) -> Callable[[ArcInvestigation], ArcInvestigation]:
        def _arrow681(inv: ArcInvestigation) -> ArcInvestigation:
            new_investigation: ArcInvestigation = inv.Copy()
            new_investigation.SetAssayAt(index, assay)
            return new_investigation

        return _arrow681

    def SetAssay(self, assay_identifier: str, assay: ArcAssay) -> None:
        this: ArcInvestigation = self
        index: int = this.GetAssayIndex(assay_identifier) or 0
        this.SetAssayAt(index, assay)

    @staticmethod
    def set_assay(assay_identifier: str, assay: ArcAssay) -> Callable[[ArcInvestigation], ArcInvestigation]:
        def _arrow682(inv: ArcInvestigation) -> ArcInvestigation:
            new_investigation: ArcInvestigation = inv.Copy()
            new_investigation.SetAssay(assay_identifier, assay)
            return new_investigation

        return _arrow682

    def GetAssayIndex(self, assay_identifier: str) -> int:
        this: ArcInvestigation = self
        def _arrow683(a: ArcAssay) -> bool:
            return a.Identifier == assay_identifier

        index: int = find_index(_arrow683, this.Assays) or 0
        if index == -1:
            raise Exception(("Unable to find assay with specified identifier \'" + assay_identifier) + "\'!")

        return index

    @staticmethod
    def get_assay_index(assay_identifier: str) -> Callable[[ArcInvestigation], int]:
        def _arrow684(inv: ArcInvestigation) -> int:
            return inv.GetAssayIndex(assay_identifier)

        return _arrow684

    def GetAssayAt(self, index: int) -> ArcAssay:
        this: ArcInvestigation = self
        return this.Assays[index]

    @staticmethod
    def get_assay_at(index: int) -> Callable[[ArcInvestigation], ArcAssay]:
        def _arrow685(inv: ArcInvestigation) -> ArcAssay:
            new_investigation: ArcInvestigation = inv.Copy()
            return new_investigation.GetAssayAt(index)

        return _arrow685

    def GetAssay(self, assay_identifier: str) -> ArcAssay:
        this: ArcInvestigation = self
        match_value: ArcAssay | None = this.TryGetAssay(assay_identifier)
        if match_value is None:
            raise Exception(ArcTypesAux_ErrorMsgs_unableToFindAssayIdentifier(assay_identifier, this.Identifier))

        else: 
            return match_value


    @staticmethod
    def get_assay(assay_identifier: str) -> Callable[[ArcInvestigation], ArcAssay]:
        def _arrow686(inv: ArcInvestigation) -> ArcAssay:
            new_investigation: ArcInvestigation = inv.Copy()
            return new_investigation.GetAssay(assay_identifier)

        return _arrow686

    def TryGetAssay(self, assay_identifier: str) -> ArcAssay | None:
        this: ArcInvestigation = self
        def _arrow687(a: ArcAssay) -> bool:
            return a.Identifier == assay_identifier

        return try_find(_arrow687, this.Assays)

    @staticmethod
    def try_get_assay(assay_identifier: str) -> Callable[[ArcInvestigation], ArcAssay | None]:
        def _arrow688(inv: ArcInvestigation) -> ArcAssay | None:
            new_investigation: ArcInvestigation = inv.Copy()
            return new_investigation.TryGetAssay(assay_identifier)

        return _arrow688

    def ContainsAssay(self, assay_identifier: str) -> bool:
        this: ArcInvestigation = self
        def predicate(a: ArcAssay) -> bool:
            return a.Identifier == assay_identifier

        return exists(predicate, this.Assays)

    @staticmethod
    def contains_assay(assay_identifier: str) -> Callable[[ArcInvestigation], bool]:
        def _arrow689(inv: ArcInvestigation) -> bool:
            return inv.ContainsAssay(assay_identifier)

        return _arrow689

    @property
    def RegisteredStudyIdentifierCount(self, __unit: None=None) -> int:
        this: ArcInvestigation = self
        return len(this.RegisteredStudyIdentifiers)

    @property
    def RegisteredStudies(self, __unit: None=None) -> Array[ArcStudy]:
        this: ArcInvestigation = self
        def f(identifier: str) -> ArcStudy | None:
            return this.TryGetStudy(identifier)

        return ResizeArray_choose(f, this.RegisteredStudyIdentifiers)

    @property
    def RegisteredStudyCount(self, __unit: None=None) -> int:
        this: ArcInvestigation = self
        return len(this.RegisteredStudies)

    @property
    def VacantStudyIdentifiers(self, __unit: None=None) -> Array[str]:
        this: ArcInvestigation = self
        def f(arg: str) -> bool:
            return not this.ContainsStudy(arg)

        return ResizeArray_filter(f, this.RegisteredStudyIdentifiers)

    @property
    def StudyCount(self, __unit: None=None) -> int:
        this: ArcInvestigation = self
        return len(this.Studies)

    @property
    def StudyIdentifiers(self, __unit: None=None) -> Array[str]:
        this: ArcInvestigation = self
        def mapping(x: ArcStudy) -> str:
            return x.Identifier

        return to_array(map_1(mapping, this.Studies))

    @property
    def UnregisteredStudies(self, __unit: None=None) -> Array[ArcStudy]:
        this: ArcInvestigation = self
        def f(s: ArcStudy) -> bool:
            def _arrow692(__unit: None=None, s: Any=s) -> bool:
                source: Array[str] = this.RegisteredStudyIdentifiers
                def _arrow691(__unit: None=None) -> Callable[[str], bool]:
                    x: str = s.Identifier
                    def _arrow690(y: str) -> bool:
                        return x == y

                    return _arrow690

                return exists(_arrow691(), source)

            return not _arrow692()

        return ResizeArray_filter(f, this.Studies)

    def AddStudy(self, study: ArcStudy) -> None:
        this: ArcInvestigation = self
        study_1: ArcStudy = study
        def predicate(x: ArcStudy) -> bool:
            return x.Identifier == study_1.Identifier

        match_value: int | None = try_find_index(predicate, this.Studies)
        if match_value is None:
            pass

        else: 
            raise Exception(((("Cannot create study with name " + study_1.Identifier) + ", as study names must be unique and study at index ") + str(match_value)) + " has the same name.")

        study.Investigation = this
        (this.Studies.append(study))

    @staticmethod
    def add_study(study: ArcStudy) -> Callable[[ArcInvestigation], ArcInvestigation]:
        def _arrow693(inv: ArcInvestigation) -> ArcInvestigation:
            copy: ArcInvestigation = inv.Copy()
            copy.AddStudy(study)
            return copy

        return _arrow693

    def InitStudy(self, study_identifier: str) -> ArcStudy:
        this: ArcInvestigation = self
        study: ArcStudy = ArcStudy.init(study_identifier)
        this.AddStudy(study)
        return study

    @staticmethod
    def init_study(study_identifier: str) -> Callable[[ArcInvestigation], tuple[ArcInvestigation, ArcStudy]]:
        def _arrow694(inv: ArcInvestigation) -> tuple[ArcInvestigation, ArcStudy]:
            copy: ArcInvestigation = inv.Copy()
            return (copy, copy.InitStudy(study_identifier))

        return _arrow694

    def RegisterStudy(self, study_identifier: str) -> None:
        this: ArcInvestigation = self
        study_ident: str = study_identifier
        def predicate(x: str) -> bool:
            return x == study_ident

        match_value: str | None = try_find(predicate, this.StudyIdentifiers)
        if match_value is not None:
            pass

        else: 
            raise Exception(("The given study with identifier \'" + study_ident) + "\' must be added to Investigation before it can be registered.")

        study_ident_1: str = study_identifier
        class ObjectExpr696:
            @property
            def Equals(self) -> Callable[[str, str], bool]:
                def _arrow695(x_1: str, y: str) -> bool:
                    return x_1 == y

                return _arrow695

            @property
            def GetHashCode(self) -> Callable[[str], int]:
                return string_hash

        if contains(study_ident_1, this.RegisteredStudyIdentifiers, ObjectExpr696()):
            raise Exception(("Study with identifier \'" + study_ident_1) + "\' is already registered!")

        (this.RegisteredStudyIdentifiers.append(study_identifier))

    @staticmethod
    def register_study(study_identifier: str) -> Callable[[ArcInvestigation], ArcInvestigation]:
        def _arrow697(inv: ArcInvestigation) -> ArcInvestigation:
            copy: ArcInvestigation = inv.Copy()
            copy.RegisterStudy(study_identifier)
            return copy

        return _arrow697

    def AddRegisteredStudy(self, study: ArcStudy) -> None:
        this: ArcInvestigation = self
        this.AddStudy(study)
        this.RegisterStudy(study.Identifier)

    @staticmethod
    def add_registered_study(study: ArcStudy) -> Callable[[ArcInvestigation], ArcInvestigation]:
        def _arrow698(inv: ArcInvestigation) -> ArcInvestigation:
            copy: ArcInvestigation = inv.Copy()
            study_1: ArcStudy = study.Copy()
            copy.AddRegisteredStudy(study_1)
            return copy

        return _arrow698

    def DeleteStudyAt(self, index: int) -> None:
        this: ArcInvestigation = self
        this.Studies.pop(index)

    @staticmethod
    def delete_study_at(index: int) -> Callable[[ArcInvestigation], ArcInvestigation]:
        def _arrow699(i: ArcInvestigation) -> ArcInvestigation:
            copy: ArcInvestigation = i.Copy()
            copy.DeleteStudyAt(index)
            return copy

        return _arrow699

    def DeleteStudy(self, study_identifier: str) -> None:
        this: ArcInvestigation = self
        def _arrow700(s: ArcStudy) -> bool:
            return s.Identifier == study_identifier

        index: int = find_index(_arrow700, this.Studies) or 0
        this.DeleteStudyAt(index)

    @staticmethod
    def delete_study(study_identifier: str) -> Callable[[ArcInvestigation], ArcInvestigation]:
        def _arrow701(i: ArcInvestigation) -> ArcInvestigation:
            copy: ArcInvestigation = i.Copy()
            copy.DeleteStudy(study_identifier)
            return copy

        return _arrow701

    def RemoveStudyAt(self, index: int) -> None:
        this: ArcInvestigation = self
        ident: str = this.GetStudyAt(index).Identifier
        this.Studies.pop(index)
        this.DeregisterStudy(ident)

    @staticmethod
    def remove_study_at(index: int) -> Callable[[ArcInvestigation], ArcInvestigation]:
        def _arrow702(inv: ArcInvestigation) -> ArcInvestigation:
            new_inv: ArcInvestigation = inv.Copy()
            new_inv.RemoveStudyAt(index)
            return new_inv

        return _arrow702

    def RemoveStudy(self, study_identifier: str) -> None:
        this: ArcInvestigation = self
        index: int = this.GetStudyIndex(study_identifier) or 0
        this.RemoveStudyAt(index)

    @staticmethod
    def remove_study(study_identifier: str) -> Callable[[ArcInvestigation], ArcInvestigation]:
        def _arrow703(inv: ArcInvestigation) -> ArcInvestigation:
            copy: ArcInvestigation = inv.Copy()
            copy.RemoveStudy(study_identifier)
            return copy

        return _arrow703

    def RenameStudy(self, old_identifier: str, new_identifier: str) -> None:
        this: ArcInvestigation = self
        def action(s: ArcStudy) -> None:
            if s.Identifier == old_identifier:
                s.Identifier = new_identifier


        iterate(action, this.Studies)
        def predicate(si: str) -> bool:
            return si == old_identifier

        index: int | None = try_find_index(predicate, this.RegisteredStudyIdentifiers)
        if index is not None:
            index_1: int = index or 0
            this.RegisteredStudyIdentifiers[index_1] = new_identifier


    @staticmethod
    def rename_study(old_identifier: str, new_identifier: str) -> Callable[[ArcInvestigation], ArcInvestigation]:
        def _arrow704(inv: ArcInvestigation) -> ArcInvestigation:
            new_inv: ArcInvestigation = inv.Copy()
            new_inv.RenameStudy(old_identifier, new_identifier)
            return new_inv

        return _arrow704

    def SetStudyAt(self, index: int, study: ArcStudy) -> None:
        this: ArcInvestigation = self
        study_1: ArcStudy = study
        def predicate(x: ArcStudy) -> bool:
            return x.Identifier == study_1.Identifier

        match_value: int | None = try_find_index(predicate, remove_at(index, this.Studies))
        if match_value is None:
            pass

        else: 
            raise Exception(((("Cannot create study with name " + study_1.Identifier) + ", as study names must be unique and study at index ") + str(match_value)) + " has the same name.")

        study.Investigation = this
        this.Studies[index] = study

    @staticmethod
    def set_study_at(index: int, study: ArcStudy) -> Callable[[ArcInvestigation], ArcInvestigation]:
        def _arrow705(inv: ArcInvestigation) -> ArcInvestigation:
            new_inv: ArcInvestigation = inv.Copy()
            new_inv.SetStudyAt(index, study)
            return new_inv

        return _arrow705

    def SetStudy(self, study_identifier: str, study: ArcStudy) -> None:
        this: ArcInvestigation = self
        index: int = this.GetStudyIndex(study_identifier) or 0
        this.SetStudyAt(index, study)

    @staticmethod
    def set_study(study_identifier: str, study: ArcStudy) -> Callable[[ArcInvestigation], ArcInvestigation]:
        def _arrow706(inv: ArcInvestigation) -> ArcInvestigation:
            new_inv: ArcInvestigation = inv.Copy()
            new_inv.SetStudy(study_identifier, study)
            return new_inv

        return _arrow706

    def GetStudyIndex(self, study_identifier: str) -> int:
        this: ArcInvestigation = self
        def _arrow707(s: ArcStudy) -> bool:
            return s.Identifier == study_identifier

        index: int = find_index(_arrow707, this.Studies) or 0
        if index == -1:
            raise Exception(("Unable to find study with specified identifier \'" + study_identifier) + "\'!")

        return index

    @staticmethod
    def get_study_index(study_identifier: str) -> Callable[[ArcInvestigation], int]:
        def _arrow708(inv: ArcInvestigation) -> int:
            return inv.GetStudyIndex(study_identifier)

        return _arrow708

    def GetStudyAt(self, index: int) -> ArcStudy:
        this: ArcInvestigation = self
        return this.Studies[index]

    @staticmethod
    def get_study_at(index: int) -> Callable[[ArcInvestigation], ArcStudy]:
        def _arrow709(inv: ArcInvestigation) -> ArcStudy:
            new_inv: ArcInvestigation = inv.Copy()
            return new_inv.GetStudyAt(index)

        return _arrow709

    def GetStudy(self, study_identifier: str) -> ArcStudy:
        this: ArcInvestigation = self
        match_value: ArcStudy | None = this.TryGetStudy(study_identifier)
        if match_value is None:
            raise Exception(ArcTypesAux_ErrorMsgs_unableToFindStudyIdentifier(study_identifier, this.Identifier))

        else: 
            return match_value


    @staticmethod
    def get_study(study_identifier: str) -> Callable[[ArcInvestigation], ArcStudy]:
        def _arrow710(inv: ArcInvestigation) -> ArcStudy:
            new_inv: ArcInvestigation = inv.Copy()
            return new_inv.GetStudy(study_identifier)

        return _arrow710

    def TryGetStudy(self, study_identifier: str) -> ArcStudy | None:
        this: ArcInvestigation = self
        def predicate(s: ArcStudy) -> bool:
            return s.Identifier == study_identifier

        return try_find(predicate, this.Studies)

    @staticmethod
    def try_get_study(study_identifier: str) -> Callable[[ArcInvestigation], ArcStudy | None]:
        def _arrow711(inv: ArcInvestigation) -> ArcStudy | None:
            new_inv: ArcInvestigation = inv.Copy()
            return new_inv.TryGetStudy(study_identifier)

        return _arrow711

    def ContainsStudy(self, study_identifier: str) -> bool:
        this: ArcInvestigation = self
        def predicate(s: ArcStudy) -> bool:
            return s.Identifier == study_identifier

        return exists(predicate, this.Studies)

    @staticmethod
    def contains_study(study_identifier: str) -> Callable[[ArcInvestigation], bool]:
        def _arrow712(inv: ArcInvestigation) -> bool:
            return inv.ContainsStudy(study_identifier)

        return _arrow712

    def RegisterAssayAt(self, study_index: int, assay_identifier: str) -> None:
        this: ArcInvestigation = self
        study: ArcStudy = this.GetStudyAt(study_index)
        def predicate(x: str) -> bool:
            return x == assay_identifier

        def mapping(a: ArcAssay) -> str:
            return a.Identifier

        match_value: str | None = try_find(predicate, map_1(mapping, this.Assays))
        if match_value is not None:
            pass

        else: 
            raise Exception("The given assay must be added to Investigation before it can be registered.")

        assay_ident_1: str = assay_identifier
        def predicate_1(x_1: str) -> bool:
            return x_1 == assay_ident_1

        match_value_1: int | None = try_find_index(predicate_1, study.RegisteredAssayIdentifiers)
        if match_value_1 is None:
            pass

        else: 
            raise Exception(((("Cannot create assay with name " + assay_ident_1) + ", as assay names must be unique and assay at index ") + str(match_value_1)) + " has the same name.")

        study.RegisterAssay(assay_identifier)

    @staticmethod
    def register_assay_at(study_index: int, assay_identifier: str) -> Callable[[ArcInvestigation], ArcInvestigation]:
        def _arrow713(inv: ArcInvestigation) -> ArcInvestigation:
            copy: ArcInvestigation = inv.Copy()
            copy.RegisterAssayAt(study_index, assay_identifier)
            return copy

        return _arrow713

    def RegisterAssay(self, study_identifier: str, assay_identifier: str) -> None:
        this: ArcInvestigation = self
        index: int = this.GetStudyIndex(study_identifier) or 0
        this.RegisterAssayAt(index, assay_identifier)

    @staticmethod
    def register_assay(study_identifier: str, assay_identifier: str) -> Callable[[ArcInvestigation], ArcInvestigation]:
        def _arrow714(inv: ArcInvestigation) -> ArcInvestigation:
            copy: ArcInvestigation = inv.Copy()
            copy.RegisterAssay(study_identifier, assay_identifier)
            return copy

        return _arrow714

    def DeregisterAssayAt(self, study_index: int, assay_identifier: str) -> None:
        this: ArcInvestigation = self
        study: ArcStudy = this.GetStudyAt(study_index)
        study.DeregisterAssay(assay_identifier)

    @staticmethod
    def deregister_assay_at(study_index: int, assay_identifier: str) -> Callable[[ArcInvestigation], ArcInvestigation]:
        def _arrow715(inv: ArcInvestigation) -> ArcInvestigation:
            copy: ArcInvestigation = inv.Copy()
            copy.DeregisterAssayAt(study_index, assay_identifier)
            return copy

        return _arrow715

    def DeregisterAssay(self, study_identifier: str, assay_identifier: str) -> None:
        this: ArcInvestigation = self
        index: int = this.GetStudyIndex(study_identifier) or 0
        this.DeregisterAssayAt(index, assay_identifier)

    @staticmethod
    def deregister_assay(study_identifier: str, assay_identifier: str) -> Callable[[ArcInvestigation], ArcInvestigation]:
        def _arrow716(inv: ArcInvestigation) -> ArcInvestigation:
            copy: ArcInvestigation = inv.Copy()
            copy.DeregisterAssay(study_identifier, assay_identifier)
            return copy

        return _arrow716

    def DeregisterStudy(self, study_identifier: str) -> None:
        this: ArcInvestigation = self
        class ObjectExpr718:
            @property
            def Equals(self) -> Callable[[str, str], bool]:
                def _arrow717(x: str, y: str) -> bool:
                    return x == y

                return _arrow717

            @property
            def GetHashCode(self) -> Callable[[str], int]:
                return string_hash

        ignore(remove_in_place(study_identifier, this.RegisteredStudyIdentifiers, ObjectExpr718()))

    @staticmethod
    def deregister_study(study_identifier: str) -> Callable[[ArcInvestigation], ArcInvestigation]:
        def _arrow719(i: ArcInvestigation) -> ArcInvestigation:
            copy: ArcInvestigation = i.Copy()
            copy.DeregisterStudy(study_identifier)
            return copy

        return _arrow719

    @property
    def WorkflowCount(self, __unit: None=None) -> int:
        this: ArcInvestigation = self
        return len(this.Workflows)

    @property
    def WorkflowIdentifiers(self, __unit: None=None) -> Array[str]:
        this: ArcInvestigation = self
        def mapping(x: ArcWorkflow) -> str:
            return x.Identifier

        return to_array(map_1(mapping, this.Workflows))

    def GetWorkflowIndex(self, workflow_identifier: str) -> int:
        this: ArcInvestigation = self
        def _arrow720(w: ArcWorkflow) -> bool:
            return w.Identifier == workflow_identifier

        index: int = find_index(_arrow720, this.Workflows) or 0
        if index == -1:
            raise Exception(("Unable to find workflow with specified identifier \'" + workflow_identifier) + "\'!")

        return index

    @staticmethod
    def get_workflow_index(workflow_identifier: str) -> Callable[[ArcInvestigation], int]:
        def _arrow721(inv: ArcInvestigation) -> int:
            return inv.GetWorkflowIndex(workflow_identifier)

        return _arrow721

    def AddWorkflow(self, workflow: ArcWorkflow) -> None:
        this: ArcInvestigation = self
        workflow_1: ArcWorkflow = workflow
        def predicate(x: ArcWorkflow) -> bool:
            return x.Identifier == workflow_1.Identifier

        match_value: int | None = try_find_index(predicate, this.Workflows)
        if match_value is None:
            pass

        else: 
            raise Exception(((("Cannot create workflow with name " + workflow_1.Identifier) + ", as workflow names must be unique and workflow at index ") + str(match_value)) + " has the same name.")

        workflow.Investigation = this
        (this.Workflows.append(workflow))

    @staticmethod
    def add_workflow(workflow: ArcWorkflow) -> Callable[[ArcInvestigation], ArcInvestigation]:
        def _arrow722(inv: ArcInvestigation) -> ArcInvestigation:
            copy: ArcInvestigation = inv.Copy()
            copy.AddWorkflow(workflow)
            return copy

        return _arrow722

    def InitWorkflow(self, workflow_identifier: str) -> ArcWorkflow:
        this: ArcInvestigation = self
        workflow: ArcWorkflow = ArcWorkflow.init(workflow_identifier)
        this.AddWorkflow(workflow)
        return workflow

    @staticmethod
    def init_workflow(workflow_identifier: str) -> Callable[[ArcInvestigation], ArcWorkflow]:
        def _arrow723(inv: ArcInvestigation) -> ArcWorkflow:
            copy: ArcInvestigation = inv.Copy()
            return copy.InitWorkflow(workflow_identifier)

        return _arrow723

    def DeleteWorkflowAt(self, index: int) -> None:
        this: ArcInvestigation = self
        this.Workflows.pop(index)

    @staticmethod
    def delete_workflow_at(index: int) -> Callable[[ArcInvestigation], ArcInvestigation]:
        def _arrow724(inv: ArcInvestigation) -> ArcInvestigation:
            copy: ArcInvestigation = inv.Copy()
            copy.DeleteWorkflowAt(index)
            return copy

        return _arrow724

    def DeleteWorkflow(self, workflow_identifier: str) -> None:
        this: ArcInvestigation = self
        def _arrow725(w: ArcWorkflow) -> bool:
            return w.Identifier == workflow_identifier

        index: int = find_index(_arrow725, this.Workflows) or 0
        this.DeleteWorkflowAt(index)
        def action(w_1: ArcWorkflow) -> None:
            def predicate(swi: str, w_1: Any=w_1) -> bool:
                return swi == workflow_identifier

            match_value: int | None = try_find_index(predicate, w_1.SubWorkflowIdentifiers)
            if match_value is not None:
                swi_index: int = match_value or 0
                w_1.SubWorkflowIdentifiers.pop(swi_index)


        iterate(action, this.Workflows)
        def action_1(r: ArcRun) -> None:
            def predicate_1(wi: str, r: Any=r) -> bool:
                return wi == workflow_identifier

            match_value_1: int | None = try_find_index(predicate_1, r.WorkflowIdentifiers)
            if match_value_1 is not None:
                wi_index: int = match_value_1 or 0
                r.WorkflowIdentifiers.pop(wi_index)


        iterate(action_1, this.Runs)

    @staticmethod
    def delete_workflow(workflow_identifier: str) -> Callable[[ArcInvestigation], ArcInvestigation]:
        def _arrow726(inv: ArcInvestigation) -> ArcInvestigation:
            copy: ArcInvestigation = inv.Copy()
            copy.DeleteWorkflow(workflow_identifier)
            return copy

        return _arrow726

    def GetWorkflowAt(self, index: int) -> ArcWorkflow:
        this: ArcInvestigation = self
        return this.Workflows[index]

    @staticmethod
    def get_workflow_at(index: int) -> Callable[[ArcInvestigation], ArcWorkflow]:
        def _arrow727(inv: ArcInvestigation) -> ArcWorkflow:
            copy: ArcInvestigation = inv.Copy()
            return copy.GetWorkflowAt(index)

        return _arrow727

    def GetWorkflow(self, workflow_identifier: str) -> ArcWorkflow:
        this: ArcInvestigation = self
        match_value: ArcWorkflow | None = this.TryGetWorkflow(workflow_identifier)
        if match_value is None:
            raise Exception(ArcTypesAux_ErrorMsgs_unableToFindWorkflowIdentifier(workflow_identifier, this.Identifier))

        else: 
            return match_value


    @staticmethod
    def get_workflow(workflow_identifier: str) -> Callable[[ArcInvestigation], ArcWorkflow]:
        def _arrow728(inv: ArcInvestigation) -> ArcWorkflow:
            copy: ArcInvestigation = inv.Copy()
            return copy.GetWorkflow(workflow_identifier)

        return _arrow728

    def TryGetWorkflow(self, workflow_identifier: str) -> ArcWorkflow | None:
        this: ArcInvestigation = self
        def predicate(w: ArcWorkflow) -> bool:
            return w.Identifier == workflow_identifier

        return try_find(predicate, this.Workflows)

    @staticmethod
    def try_get_workflow(workflow_identifier: str) -> Callable[[ArcInvestigation], ArcWorkflow | None]:
        def _arrow729(inv: ArcInvestigation) -> ArcWorkflow | None:
            copy: ArcInvestigation = inv.Copy()
            return copy.TryGetWorkflow(workflow_identifier)

        return _arrow729

    def ContainsWorkflow(self, workflow_identifier: str) -> bool:
        this: ArcInvestigation = self
        def predicate(w: ArcWorkflow) -> bool:
            return w.Identifier == workflow_identifier

        return exists(predicate, this.Workflows)

    @staticmethod
    def contains_workflow(workflow_identifier: str) -> Callable[[ArcInvestigation], bool]:
        def _arrow730(inv: ArcInvestigation) -> bool:
            return inv.ContainsWorkflow(workflow_identifier)

        return _arrow730

    def SetWorkflowAt(self, index: int, workflow: ArcWorkflow) -> None:
        this: ArcInvestigation = self
        workflow_1: ArcWorkflow = workflow
        def predicate(x: ArcWorkflow) -> bool:
            return x.Identifier == workflow_1.Identifier

        match_value: int | None = try_find_index(predicate, remove_at(index, this.Workflows))
        if match_value is None:
            pass

        else: 
            raise Exception(((("Cannot create workflow with name " + workflow_1.Identifier) + ", as workflow names must be unique and workflow at index ") + str(match_value)) + " has the same name.")

        workflow.Investigation = this
        this.Workflows[index] = workflow

    def SetWorkflow(self, workflow_identifier: str, workflow: ArcWorkflow) -> None:
        this: ArcInvestigation = self
        index: int = this.GetWorkflowIndex(workflow_identifier) or 0
        this.SetWorkflowAt(index, workflow)

    @staticmethod
    def set_workflow(workflow_identifier: str, workflow: ArcWorkflow) -> Callable[[ArcInvestigation], ArcInvestigation]:
        def _arrow731(inv: ArcInvestigation) -> ArcInvestigation:
            copy: ArcInvestigation = inv.Copy()
            copy.SetWorkflow(workflow_identifier, workflow)
            return copy

        return _arrow731

    @staticmethod
    def set_workflow_at(index: int, workflow: ArcWorkflow) -> Callable[[ArcInvestigation], ArcInvestigation]:
        def _arrow732(inv: ArcInvestigation) -> ArcInvestigation:
            copy: ArcInvestigation = inv.Copy()
            copy.SetWorkflowAt(index, workflow)
            return copy

        return _arrow732

    @property
    def RunCount(self, __unit: None=None) -> int:
        this: ArcInvestigation = self
        return len(this.Runs)

    @property
    def RunIdentifiers(self, __unit: None=None) -> Array[str]:
        this: ArcInvestigation = self
        def mapping(x: ArcRun) -> str:
            return x.Identifier

        return to_array(map_1(mapping, this.Runs))

    def GetRunIndex(self, run_identifier: str) -> int:
        this: ArcInvestigation = self
        def _arrow733(r: ArcRun) -> bool:
            return r.Identifier == run_identifier

        index: int = find_index(_arrow733, this.Runs) or 0
        if index == -1:
            raise Exception(("Unable to find run with specified identifier \'" + run_identifier) + "\'!")

        return index

    @staticmethod
    def get_run_index(run_identifier: str) -> Callable[[ArcInvestigation], int]:
        def _arrow734(inv: ArcInvestigation) -> int:
            return inv.GetRunIndex(run_identifier)

        return _arrow734

    def AddRun(self, run: ArcRun) -> None:
        this: ArcInvestigation = self
        run_1: ArcRun = run
        def predicate(x: ArcRun) -> bool:
            return x.Identifier == run_1.Identifier

        match_value: int | None = try_find_index(predicate, this.Runs)
        if match_value is None:
            pass

        else: 
            raise Exception(((("Cannot create run with name " + run_1.Identifier) + ", as run names must be unique and run at index ") + str(match_value)) + " has the same name.")

        run.Investigation = this
        (this.Runs.append(run))

    @staticmethod
    def add_run(run: ArcRun) -> Callable[[ArcInvestigation], ArcInvestigation]:
        def _arrow735(inv: ArcInvestigation) -> ArcInvestigation:
            copy: ArcInvestigation = inv.Copy()
            copy.AddRun(run)
            return copy

        return _arrow735

    def InitRun(self, run_identifier: str) -> ArcRun:
        this: ArcInvestigation = self
        run: ArcRun = ArcRun.init(run_identifier)
        this.AddRun(run)
        return run

    @staticmethod
    def init_run(run_identifier: str) -> Callable[[ArcInvestigation], ArcRun]:
        def _arrow736(inv: ArcInvestigation) -> ArcRun:
            copy: ArcInvestigation = inv.Copy()
            return copy.InitRun(run_identifier)

        return _arrow736

    def DeleteRunAt(self, index: int) -> None:
        this: ArcInvestigation = self
        this.Runs.pop(index)

    @staticmethod
    def delete_run_at(index: int) -> Callable[[ArcInvestigation], ArcInvestigation]:
        def _arrow737(inv: ArcInvestigation) -> ArcInvestigation:
            copy: ArcInvestigation = inv.Copy()
            copy.DeleteRunAt(index)
            return copy

        return _arrow737

    def DeleteRun(self, run_identifier: str) -> None:
        this: ArcInvestigation = self
        def _arrow738(w: ArcRun) -> bool:
            return w.Identifier == run_identifier

        index: int = find_index(_arrow738, this.Runs) or 0
        this.DeleteRunAt(index)

    @staticmethod
    def delete_run(run_identifier: str) -> Callable[[ArcInvestigation], ArcInvestigation]:
        def _arrow739(inv: ArcInvestigation) -> ArcInvestigation:
            copy: ArcInvestigation = inv.Copy()
            copy.DeleteRun(run_identifier)
            return copy

        return _arrow739

    def GetRunAt(self, index: int) -> ArcRun:
        this: ArcInvestigation = self
        return this.Runs[index]

    @staticmethod
    def get_run_at(index: int) -> Callable[[ArcInvestigation], ArcRun]:
        def _arrow740(inv: ArcInvestigation) -> ArcRun:
            copy: ArcInvestigation = inv.Copy()
            return copy.GetRunAt(index)

        return _arrow740

    def GetRun(self, run_identifier: str) -> ArcRun:
        this: ArcInvestigation = self
        match_value: ArcRun | None = this.TryGetRun(run_identifier)
        if match_value is None:
            raise Exception(ArcTypesAux_ErrorMsgs_unableToFindRunIdentifier(run_identifier, this.Identifier))

        else: 
            return match_value


    @staticmethod
    def get_run(run_identifier: str) -> Callable[[ArcInvestigation], ArcRun]:
        def _arrow741(inv: ArcInvestigation) -> ArcRun:
            copy: ArcInvestigation = inv.Copy()
            return copy.GetRun(run_identifier)

        return _arrow741

    def TryGetRun(self, run_identifier: str) -> ArcRun | None:
        this: ArcInvestigation = self
        def predicate(w: ArcRun) -> bool:
            return w.Identifier == run_identifier

        return try_find(predicate, this.Runs)

    @staticmethod
    def try_get_run(run_identifier: str) -> Callable[[ArcInvestigation], ArcRun | None]:
        def _arrow742(inv: ArcInvestigation) -> ArcRun | None:
            copy: ArcInvestigation = inv.Copy()
            return copy.TryGetRun(run_identifier)

        return _arrow742

    def ContainsRun(self, run_identifier: str) -> bool:
        this: ArcInvestigation = self
        def predicate(w: ArcRun) -> bool:
            return w.Identifier == run_identifier

        return exists(predicate, this.Runs)

    @staticmethod
    def contains_run(run_identifier: str) -> Callable[[ArcInvestigation], bool]:
        def _arrow743(inv: ArcInvestigation) -> bool:
            return inv.ContainsRun(run_identifier)

        return _arrow743

    def SetRunAt(self, index: int, run: ArcRun) -> None:
        this: ArcInvestigation = self
        run_1: ArcRun = run
        def predicate(x: ArcRun) -> bool:
            return x.Identifier == run_1.Identifier

        match_value: int | None = try_find_index(predicate, remove_at(index, this.Runs))
        if match_value is None:
            pass

        else: 
            raise Exception(((("Cannot create run with name " + run_1.Identifier) + ", as run names must be unique and run at index ") + str(match_value)) + " has the same name.")

        run.Investigation = this
        this.Runs[index] = run

    def SetRun(self, run_identifier: str, run: ArcRun) -> None:
        this: ArcInvestigation = self
        index: int = this.GetRunIndex(run_identifier) or 0
        this.SetRunAt(index, run)

    @staticmethod
    def set_run_at(index: int, run: ArcRun) -> Callable[[ArcInvestigation], ArcInvestigation]:
        def _arrow744(inv: ArcInvestigation) -> ArcInvestigation:
            copy: ArcInvestigation = inv.Copy()
            copy.SetRunAt(index, run)
            return copy

        return _arrow744

    @staticmethod
    def set_run(run_identifier: str, run: ArcRun) -> Callable[[ArcInvestigation], ArcInvestigation]:
        def _arrow745(inv: ArcInvestigation) -> ArcInvestigation:
            copy: ArcInvestigation = inv.Copy()
            copy.SetRun(run_identifier, run)
            return copy

        return _arrow745

    def GetAllPersons(self, __unit: None=None) -> Array[Person]:
        this: ArcInvestigation = self
        persons: Array[Person] = []
        enumerator: Any = get_enumerator(this.Assays)
        try: 
            while enumerator.System_Collections_IEnumerator_MoveNext():
                a: ArcAssay = enumerator.System_Collections_Generic_IEnumerator_1_get_Current()
                add_range_in_place(a.Performers, persons)

        finally: 
            dispose(enumerator)

        enumerator_1: Any = get_enumerator(this.Studies)
        try: 
            while enumerator_1.System_Collections_IEnumerator_MoveNext():
                s: ArcStudy = enumerator_1.System_Collections_Generic_IEnumerator_1_get_Current()
                add_range_in_place(s.Contacts, persons)

        finally: 
            dispose(enumerator_1)

        add_range_in_place(this.Contacts, persons)
        class ObjectExpr746:
            @property
            def Equals(self) -> Callable[[Person, Person], bool]:
                return equals

            @property
            def GetHashCode(self) -> Callable[[Person], int]:
                return safe_hash

        return Array_distinct(list(persons), ObjectExpr746())

    def GetAllPublications(self, __unit: None=None) -> Array[Publication]:
        this: ArcInvestigation = self
        pubs: Array[Publication] = []
        enumerator: Any = get_enumerator(this.Studies)
        try: 
            while enumerator.System_Collections_IEnumerator_MoveNext():
                s: ArcStudy = enumerator.System_Collections_Generic_IEnumerator_1_get_Current()
                add_range_in_place(s.Publications, pubs)

        finally: 
            dispose(enumerator)

        add_range_in_place(this.Publications, pubs)
        class ObjectExpr747:
            @property
            def Equals(self) -> Callable[[Publication, Publication], bool]:
                return equals

            @property
            def GetHashCode(self) -> Callable[[Publication], int]:
                return safe_hash

        return Array_distinct(list(pubs), ObjectExpr747())

    def DeregisterMissingAssays(self, __unit: None=None) -> None:
        this: ArcInvestigation = self
        inv: ArcInvestigation = this
        existing_assays: Array[str] = inv.AssayIdentifiers
        enumerator: Any = get_enumerator(inv.Studies)
        try: 
            while enumerator.System_Collections_IEnumerator_MoveNext():
                study: ArcStudy = enumerator.System_Collections_Generic_IEnumerator_1_get_Current()
                enumerator_1: Any = get_enumerator(list(study.RegisteredAssayIdentifiers))
                try: 
                    while enumerator_1.System_Collections_IEnumerator_MoveNext():
                        registered_assay: str = enumerator_1.System_Collections_Generic_IEnumerator_1_get_Current()
                        class ObjectExpr749:
                            @property
                            def Equals(self) -> Callable[[str, str], bool]:
                                def _arrow748(x: str, y: str) -> bool:
                                    return x == y

                                return _arrow748

                            @property
                            def GetHashCode(self) -> Callable[[str], int]:
                                return string_hash

                        if not contains(registered_assay, existing_assays, ObjectExpr749()):
                            value_1: None = study.DeregisterAssay(registered_assay)
                            ignore(None)


                finally: 
                    dispose(enumerator_1)


        finally: 
            dispose(enumerator)


    @staticmethod
    def deregister_missing_assays(__unit: None=None) -> Callable[[ArcInvestigation], ArcInvestigation]:
        def _arrow750(inv: ArcInvestigation) -> ArcInvestigation:
            copy: ArcInvestigation = inv.Copy()
            copy.DeregisterMissingAssays()
            return copy

        return _arrow750

    def UpdateIOTypeByEntityID(self, __unit: None=None) -> None:
        this: ArcInvestigation = self
        def _arrow756(__unit: None=None) -> IEnumerable_1[ArcTable]:
            def _arrow751(study: ArcStudy) -> IEnumerable_1[ArcTable]:
                return study.Tables

            def _arrow755(__unit: None=None) -> IEnumerable_1[ArcTable]:
                def _arrow752(assay: ArcAssay) -> IEnumerable_1[ArcTable]:
                    return assay.Tables

                def _arrow754(__unit: None=None) -> IEnumerable_1[ArcTable]:
                    def _arrow753(run: ArcRun) -> IEnumerable_1[ArcTable]:
                        return run.Tables

                    return collect(_arrow753, this.Runs)

                return append_4(collect(_arrow752, this.Assays), delay(_arrow754))

            return append_4(collect(_arrow751, this.Studies), delay(_arrow755))

        io_map: Any = ArcTablesAux_getIOMap(list(to_list(delay(_arrow756))))
        enumerator: Any = get_enumerator(this.Studies)
        try: 
            while enumerator.System_Collections_IEnumerator_MoveNext():
                study_1: ArcStudy = enumerator.System_Collections_Generic_IEnumerator_1_get_Current()
                ArcTablesAux_applyIOMap(io_map, study_1.Tables)

        finally: 
            dispose(enumerator)

        enumerator_1: Any = get_enumerator(this.Assays)
        try: 
            while enumerator_1.System_Collections_IEnumerator_MoveNext():
                assay_1: ArcAssay = enumerator_1.System_Collections_Generic_IEnumerator_1_get_Current()
                ArcTablesAux_applyIOMap(io_map, assay_1.Tables)

        finally: 
            dispose(enumerator_1)

        enumerator_2: Any = get_enumerator(this.Runs)
        try: 
            while enumerator_2.System_Collections_IEnumerator_MoveNext():
                run_1: ArcRun = enumerator_2.System_Collections_Generic_IEnumerator_1_get_Current()
                ArcTablesAux_applyIOMap(io_map, run_1.Tables)

        finally: 
            dispose(enumerator_2)


    def Copy(self, __unit: None=None) -> ArcInvestigation:
        this: ArcInvestigation = self
        next_assays: Array[ArcAssay] = []
        next_studies: Array[ArcStudy] = []
        next_workflows: Array[ArcWorkflow] = []
        next_runs: Array[ArcRun] = []
        enumerator: Any = get_enumerator(this.Assays)
        try: 
            while enumerator.System_Collections_IEnumerator_MoveNext():
                assay: ArcAssay = enumerator.System_Collections_Generic_IEnumerator_1_get_Current()
                copy: ArcAssay = assay.Copy()
                (next_assays.append(copy))

        finally: 
            dispose(enumerator)

        enumerator_1: Any = get_enumerator(this.Studies)
        try: 
            while enumerator_1.System_Collections_IEnumerator_MoveNext():
                study: ArcStudy = enumerator_1.System_Collections_Generic_IEnumerator_1_get_Current()
                copy_1: ArcStudy = study.Copy()
                (next_studies.append(copy_1))

        finally: 
            dispose(enumerator_1)

        enumerator_2: Any = get_enumerator(this.Workflows)
        try: 
            while enumerator_2.System_Collections_IEnumerator_MoveNext():
                workflow: ArcWorkflow = enumerator_2.System_Collections_Generic_IEnumerator_1_get_Current()
                copy_2: ArcWorkflow = workflow.Copy()
                (next_workflows.append(copy_2))

        finally: 
            dispose(enumerator_2)

        enumerator_3: Any = get_enumerator(this.Runs)
        try: 
            while enumerator_3.System_Collections_IEnumerator_MoveNext():
                run: ArcRun = enumerator_3.System_Collections_Generic_IEnumerator_1_get_Current()
                copy_3: ArcRun = run.Copy()
                (next_runs.append(copy_3))

        finally: 
            dispose(enumerator_3)

        def f(c: Comment) -> Comment:
            return c.Copy()

        next_comments: Array[Comment] = ResizeArray_map(f, this.Comments)
        def f_1(c_1: Remark) -> Remark:
            return c_1.Copy()

        next_remarks: Array[Remark] = ResizeArray_map(f_1, this.Remarks)
        def f_2(c_2: Person) -> Person:
            return c_2.Copy()

        next_contacts: Array[Person] = ResizeArray_map(f_2, this.Contacts)
        def f_3(c_3: Publication) -> Publication:
            return c_3.Copy()

        next_publications: Array[Publication] = ResizeArray_map(f_3, this.Publications)
        def f_4(c_4: OntologySourceReference) -> OntologySourceReference:
            return c_4.Copy()

        next_ontology_source_references: Array[OntologySourceReference] = ResizeArray_map(f_4, this.OntologySourceReferences)
        next_study_identifiers: Array[str] = list(this.RegisteredStudyIdentifiers)
        return ArcInvestigation(this.Identifier, this.Title, this.Description, this.SubmissionDate, this.PublicReleaseDate, next_ontology_source_references, next_publications, next_contacts, next_assays, next_studies, next_workflows, next_runs, next_study_identifiers, next_comments, next_remarks)

    def StructurallyEquals(self, other: ArcInvestigation) -> bool:
        this: ArcInvestigation = self
        def predicate(x: bool) -> bool:
            return x == True

        def _arrow759(__unit: None=None) -> bool:
            a: IEnumerable_1[Publication] = this.Publications
            b: IEnumerable_1[Publication] = other.Publications
            def folder(acc: bool, e: bool) -> bool:
                if acc:
                    return e

                else: 
                    return False


            def _arrow758(__unit: None=None) -> IEnumerable_1[bool]:
                def _arrow757(i_1: int) -> bool:
                    return equals(item(i_1, a), item(i_1, b))

                return map_1(_arrow757, range_big_int(0, 1, length(a) - 1))

            return fold(folder, True, to_list(delay(_arrow758))) if (length(a) == length(b)) else False

        def _arrow762(__unit: None=None) -> bool:
            a_1: IEnumerable_1[Person] = this.Contacts
            b_1: IEnumerable_1[Person] = other.Contacts
            def folder_1(acc_1: bool, e_1: bool) -> bool:
                if acc_1:
                    return e_1

                else: 
                    return False


            def _arrow761(__unit: None=None) -> IEnumerable_1[bool]:
                def _arrow760(i_2: int) -> bool:
                    return equals(item(i_2, a_1), item(i_2, b_1))

                return map_1(_arrow760, range_big_int(0, 1, length(a_1) - 1))

            return fold(folder_1, True, to_list(delay(_arrow761))) if (length(a_1) == length(b_1)) else False

        def _arrow765(__unit: None=None) -> bool:
            a_2: IEnumerable_1[OntologySourceReference] = this.OntologySourceReferences
            b_2: IEnumerable_1[OntologySourceReference] = other.OntologySourceReferences
            def folder_2(acc_2: bool, e_2: bool) -> bool:
                if acc_2:
                    return e_2

                else: 
                    return False


            def _arrow764(__unit: None=None) -> IEnumerable_1[bool]:
                def _arrow763(i_3: int) -> bool:
                    return equals(item(i_3, a_2), item(i_3, b_2))

                return map_1(_arrow763, range_big_int(0, 1, length(a_2) - 1))

            return fold(folder_2, True, to_list(delay(_arrow764))) if (length(a_2) == length(b_2)) else False

        def _arrow768(__unit: None=None) -> bool:
            a_3: IEnumerable_1[ArcAssay] = this.Assays
            b_3: IEnumerable_1[ArcAssay] = other.Assays
            def folder_3(acc_3: bool, e_3: bool) -> bool:
                if acc_3:
                    return e_3

                else: 
                    return False


            def _arrow767(__unit: None=None) -> IEnumerable_1[bool]:
                def _arrow766(i_4: int) -> bool:
                    return equals(item(i_4, a_3), item(i_4, b_3))

                return map_1(_arrow766, range_big_int(0, 1, length(a_3) - 1))

            return fold(folder_3, True, to_list(delay(_arrow767))) if (length(a_3) == length(b_3)) else False

        def _arrow771(__unit: None=None) -> bool:
            a_4: IEnumerable_1[ArcStudy] = this.Studies
            b_4: IEnumerable_1[ArcStudy] = other.Studies
            def folder_4(acc_4: bool, e_4: bool) -> bool:
                if acc_4:
                    return e_4

                else: 
                    return False


            def _arrow770(__unit: None=None) -> IEnumerable_1[bool]:
                def _arrow769(i_5: int) -> bool:
                    return equals(item(i_5, a_4), item(i_5, b_4))

                return map_1(_arrow769, range_big_int(0, 1, length(a_4) - 1))

            return fold(folder_4, True, to_list(delay(_arrow770))) if (length(a_4) == length(b_4)) else False

        def _arrow774(__unit: None=None) -> bool:
            a_5: IEnumerable_1[ArcWorkflow] = this.Workflows
            b_5: IEnumerable_1[ArcWorkflow] = other.Workflows
            def folder_5(acc_5: bool, e_5: bool) -> bool:
                if acc_5:
                    return e_5

                else: 
                    return False


            def _arrow773(__unit: None=None) -> IEnumerable_1[bool]:
                def _arrow772(i_6: int) -> bool:
                    return equals(item(i_6, a_5), item(i_6, b_5))

                return map_1(_arrow772, range_big_int(0, 1, length(a_5) - 1))

            return fold(folder_5, True, to_list(delay(_arrow773))) if (length(a_5) == length(b_5)) else False

        def _arrow777(__unit: None=None) -> bool:
            a_6: IEnumerable_1[ArcRun] = this.Runs
            b_6: IEnumerable_1[ArcRun] = other.Runs
            def folder_6(acc_6: bool, e_6: bool) -> bool:
                if acc_6:
                    return e_6

                else: 
                    return False


            def _arrow776(__unit: None=None) -> IEnumerable_1[bool]:
                def _arrow775(i_7: int) -> bool:
                    return equals(item(i_7, a_6), item(i_7, b_6))

                return map_1(_arrow775, range_big_int(0, 1, length(a_6) - 1))

            return fold(folder_6, True, to_list(delay(_arrow776))) if (length(a_6) == length(b_6)) else False

        def _arrow780(__unit: None=None) -> bool:
            a_7: IEnumerable_1[str] = this.RegisteredStudyIdentifiers
            b_7: IEnumerable_1[str] = other.RegisteredStudyIdentifiers
            def folder_7(acc_7: bool, e_7: bool) -> bool:
                if acc_7:
                    return e_7

                else: 
                    return False


            def _arrow779(__unit: None=None) -> IEnumerable_1[bool]:
                def _arrow778(i_8: int) -> bool:
                    return item(i_8, a_7) == item(i_8, b_7)

                return map_1(_arrow778, range_big_int(0, 1, length(a_7) - 1))

            return fold(folder_7, True, to_list(delay(_arrow779))) if (length(a_7) == length(b_7)) else False

        def _arrow783(__unit: None=None) -> bool:
            a_8: IEnumerable_1[Comment] = this.Comments
            b_8: IEnumerable_1[Comment] = other.Comments
            def folder_8(acc_8: bool, e_8: bool) -> bool:
                if acc_8:
                    return e_8

                else: 
                    return False


            def _arrow782(__unit: None=None) -> IEnumerable_1[bool]:
                def _arrow781(i_9: int) -> bool:
                    return equals(item(i_9, a_8), item(i_9, b_8))

                return map_1(_arrow781, range_big_int(0, 1, length(a_8) - 1))

            return fold(folder_8, True, to_list(delay(_arrow782))) if (length(a_8) == length(b_8)) else False

        def _arrow786(__unit: None=None) -> bool:
            a_9: IEnumerable_1[Remark] = this.Remarks
            b_9: IEnumerable_1[Remark] = other.Remarks
            def folder_9(acc_9: bool, e_9: bool) -> bool:
                if acc_9:
                    return e_9

                else: 
                    return False


            def _arrow785(__unit: None=None) -> IEnumerable_1[bool]:
                def _arrow784(i_10: int) -> bool:
                    return equals(item(i_10, a_9), item(i_10, b_9))

                return map_1(_arrow784, range_big_int(0, 1, length(a_9) - 1))

            return fold(folder_9, True, to_list(delay(_arrow785))) if (length(a_9) == length(b_9)) else False

        return for_all(predicate, to_enumerable([this.Identifier == other.Identifier, equals(this.Title, other.Title), equals(this.Description, other.Description), equals(this.SubmissionDate, other.SubmissionDate), equals(this.PublicReleaseDate, other.PublicReleaseDate), _arrow759(), _arrow762(), _arrow765(), _arrow768(), _arrow771(), _arrow774(), _arrow777(), _arrow780(), _arrow783(), _arrow786()]))

    def ReferenceEquals(self, other: ArcInvestigation) -> bool:
        this: ArcInvestigation = self
        return this is other

    def __str__(self, __unit: None=None) -> str:
        this: ArcInvestigation = self
        arg: str = this.Identifier
        arg_1: str | None = this.Title
        arg_2: str | None = this.Description
        arg_3: str | None = this.SubmissionDate
        arg_4: str | None = this.PublicReleaseDate
        arg_5: Array[OntologySourceReference] = this.OntologySourceReferences
        arg_6: Array[Publication] = this.Publications
        arg_7: Array[Person] = this.Contacts
        arg_8: Array[ArcAssay] = this.Assays
        arg_9: Array[ArcStudy] = this.Studies
        arg_10: Array[ArcWorkflow] = this.Workflows
        arg_11: Array[ArcRun] = this.Runs
        arg_12: Array[str] = this.RegisteredStudyIdentifiers
        arg_13: Array[Comment] = this.Comments
        arg_14: Array[Remark] = this.Remarks
        return to_text(printf("ArcInvestigation {\r\n    Identifier = %A,\r\n    Title = %A,\r\n    Description = %A,\r\n    SubmissionDate = %A,\r\n    PublicReleaseDate = %A,\r\n    OntologySourceReferences = %A,\r\n    Publications = %A,\r\n    Contacts = %A,\r\n    Assays = %A,\r\n    Studies = %A,\r\n    Workflows = %A,\r\n    Runs = %A,\r\n    RegisteredStudyIdentifiers = %A,\r\n    Comments = %A,\r\n    Remarks = %A,\r\n}"))(arg)(arg_1)(arg_2)(arg_3)(arg_4)(arg_5)(arg_6)(arg_7)(arg_8)(arg_9)(arg_10)(arg_11)(arg_12)(arg_13)(arg_14)

    def __eq__(self, other: Any=None) -> bool:
        this: ArcInvestigation = self
        return this.StructurallyEquals(other) if isinstance(other, ArcInvestigation) else False

    def __hash__(self, __unit: None=None) -> Any:
        this: ArcInvestigation = self
        return box_hash_array([this.Identifier, box_hash_option(this.Title), box_hash_option(this.Description), box_hash_option(this.SubmissionDate), box_hash_option(this.PublicReleaseDate), box_hash_seq(this.Publications), box_hash_seq(this.Contacts), box_hash_seq(this.OntologySourceReferences), box_hash_seq(this.Assays), box_hash_seq(this.Studies), box_hash_seq(this.Workflows), box_hash_seq(this.Runs), box_hash_seq(this.RegisteredStudyIdentifiers), box_hash_seq(this.Comments), box_hash_seq(this.Remarks)])

    def GetLightHashCode(self, __unit: None=None) -> Any:
        this: ArcInvestigation = self
        return box_hash_array([this.Identifier, box_hash_option(this.Title), box_hash_option(this.Description), box_hash_option(this.SubmissionDate), box_hash_option(this.PublicReleaseDate), box_hash_seq(this.Publications), box_hash_seq(this.Contacts), box_hash_seq(this.OntologySourceReferences), box_hash_seq(this.RegisteredStudyIdentifiers), box_hash_seq(this.Comments), box_hash_seq(this.Remarks)])


ArcInvestigation_reflection = _expr787

def ArcInvestigation__ctor_Z67823F6C(identifier: str, title: str | None=None, description: str | None=None, submission_date: str | None=None, public_release_date: str | None=None, ontology_source_references: Array[OntologySourceReference] | None=None, publications: Array[Publication] | None=None, contacts: Array[Person] | None=None, assays: Array[ArcAssay] | None=None, studies: Array[ArcStudy] | None=None, workflows: Array[ArcWorkflow] | None=None, runs: Array[ArcRun] | None=None, registered_study_identifiers: Array[str] | None=None, comments: Array[Comment] | None=None, remarks: Array[Remark] | None=None) -> ArcInvestigation:
    return ArcInvestigation(identifier, title, description, submission_date, public_release_date, ontology_source_references, publications, contacts, assays, studies, workflows, runs, registered_study_identifiers, comments, remarks)


def ArcTypesAux_ErrorMsgs_unableToFindAssayIdentifier(assay_identifier: Any, investigation_identifier: Any) -> str:
    return ((("Error. Unable to find assay with identifier \'" + str(assay_identifier)) + "\' in investigation ") + str(investigation_identifier)) + "."


def ArcTypesAux_ErrorMsgs_unableToFindStudyIdentifier(study_identifer: Any, investigation_identifier: Any) -> str:
    return ((("Error. Unable to find study with identifier \'" + str(study_identifer)) + "\' in investigation ") + str(investigation_identifier)) + "."


def ArcTypesAux_ErrorMsgs_unableToFindWorkflowIdentifier(workflow_identifier: Any, investigation_identifier: Any) -> str:
    return ((("Error. Unable to find workflow with identifier \'" + str(workflow_identifier)) + "\' in investigation ") + str(investigation_identifier)) + "."


def ArcTypesAux_ErrorMsgs_unableToFindRunIdentifier(run_identifier: Any, investigation_identifier: Any) -> str:
    return ((("Error. Unable to find run with identifier \'" + str(run_identifier)) + "\' in investigation ") + str(investigation_identifier)) + "."


__all__ = ["ArcAssay_reflection", "ArcStudy_reflection", "ArcWorkflow_reflection", "ArcRun_reflection", "ArcInvestigation_reflection", "ArcTypesAux_ErrorMsgs_unableToFindAssayIdentifier", "ArcTypesAux_ErrorMsgs_unableToFindStudyIdentifier", "ArcTypesAux_ErrorMsgs_unableToFindWorkflowIdentifier", "ArcTypesAux_ErrorMsgs_unableToFindRunIdentifier"]

