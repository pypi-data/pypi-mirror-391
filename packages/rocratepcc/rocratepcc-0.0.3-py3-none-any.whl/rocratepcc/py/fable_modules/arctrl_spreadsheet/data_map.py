from __future__ import annotations
from ..arctrl_core.data_map import DataMap
from ..fable_library.seq import (try_pick, for_all)
from ..fable_library.string_ import (to_fail, printf)
from ..fable_library.types import Array
from ..fs_spreadsheet.fs_workbook import FsWorkbook
from ..fs_spreadsheet.fs_worksheet import FsWorksheet
from .DataMapTable.data_map_table import (try_from_fs_worksheet, to_fs_worksheet)

def from_fs_workbook(doc: FsWorkbook) -> DataMap:
    try: 
        worksheets: Array[FsWorksheet] = doc.GetWorksheets()
        data_map_table: DataMap | None = try_pick(try_from_fs_worksheet, worksheets)
        if data_map_table is None:
            def sheet_is_empty(sheet: FsWorksheet) -> bool:
                return sheet.CellCollection.Count == 0

            if for_all(sheet_is_empty, worksheets):
                return DataMap.init()

            else: 
                raise Exception("No DataMapTable was found in any of the sheets of the workbook")


        else: 
            return data_map_table


    except Exception as err:
        arg: str = str(err)
        return to_fail(printf("Could not parse datamap: \n%s"))(arg)



def to_fs_workbook(data_map: DataMap) -> FsWorkbook:
    doc: FsWorkbook = FsWorkbook()
    sheet: FsWorksheet = to_fs_worksheet(data_map)
    doc.AddWorksheet(sheet)
    return doc


__all__ = ["from_fs_workbook", "to_fs_workbook"]

