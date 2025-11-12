from .utils import *
import copy
from .session import SAPGuiSession
from typing import Dict, List
import win32com.client
import warnings


# https://help.sap.com/docs/sap_gui_for_windows/b47d018c3b9b45e897faf66a6c0885a8/ce1d9e64355d49568e5def5271aea2db.html?locale=en-US
class Table:
    def __init__(self, table_obj: win32com.client.CDispatch, session: SAPGuiSession, target_index: int,
                 window: int = 0):
        self._component_target_index = target_index
        self._target_index = target_index
        self.table_obj = table_obj
        self.session = session
        self.window = window

    def _return_table(self):
        self._component_target_index = copy.copy(self._target_index)
        return scroll_through_table(self, f'wnd[{self.window}]/usr')

    def get_cell_value(self, row: int, column: int, skip_error: bool = False) -> str:
        """
        Return the content of a SAP Table cell, using the relative visible table row. The desired cell needs to be
        visible for this function be able to work
        :param row: Table relative row index
        :param column: Table column index
        :param skip_error: Skip this function if occur any error
        :return: A String with the desired cell text
        """
        try:
            return self.table_obj.getCell(row, column).text
        except:
            if not skip_error:
                raise Exception("Get cell value failed.")

    def count_visible_rows(self, skip_error: bool = False) -> int:
        """
        Count all the visible rows from a SAP Table
        :param skip_error: Skip this function if occur any error
        :return: An Integer with the number of visible rows in the active SAP Table
        """
        try:
            return self.table_obj.visibleRowCount
        except:
            if not skip_error:
                raise Exception("Get cell value failed.")

    def write_cell_value(self, row: int, column: int, desired_text: str, skip_error: bool = False) -> None:
        """
        Write any value in a SAP Table cell, using the relative visible table row. The desired cell needs to be
        visible for this function be able to work
        :param row: Table relative row index
        :param column: Table column index
        :param desired_text: The text that will overwrite the cell in the SAP Table
        :param skip_error: Skip this function if occur any error
        """
        try:
            if self.table_obj.getCell(row, column).changeable:
                self.table_obj.getCell(row, column).text = desired_text
        except:
            if not skip_error:
                raise Exception("Write cell value failed.")

    def select_entire_row(self, absolute_row: int, skip_error: bool = False) -> None:
        """
        Select the entire row from a SAP Table, it uses the absolute table row. The desired cell needs to be
        visible for this function be able to work
        :param absolute_row: Table absolute row index
        :param skip_error: Skip this function if occur any error
        """
        try:
            self.table_obj.GetAbsoluteRow(absolute_row).selected = True
        except:
            if not skip_error:
                raise Exception("Select Entire Row Failed.")

    def unselect_entire_row(self, absolute_row: int, skip_error: bool = False) -> None:
        """
        Unselect the entire row from a SAP Table, it uses the absolute table row. The desired cell needs to be
        visible for this function be able to work
        :param absolute_row: Table absolute row index
        :param skip_error: Skip this function if occur any error
        """
        try:
            self.table_obj.GetAbsoluteRow(absolute_row).selected = False
        except:
            if not skip_error:
                raise Exception("Unselect Entire Row Failed.")

    def flag_cell(self, row: int, column: int, desired_operator: bool, skip_error: bool = False) -> None:
        """
        Flags a checkbox in a SAP Table cell, using the relative visible table row. The desired cell needs to be
        visible for this function be able to work
        :param row: Table relative row index
        :param column: Table column index
        :param skip_error: Skip this function if occur any error
        :param desired_operator: Boolean with the desired operator in the SAP Table cell's checkbox
        """
        try:
            if self.table_obj.getCell(row, column).changeable:
                self.table_obj.getCell(row, column).selected = desired_operator
        except:
            if not skip_error:
                raise Exception("Flag Cell Failed.")

    def click_cell(self, row: int, column: int, skip_error: bool = False) -> None:
        """
        Focus in a cell and double-click in it, using the relative visible table row. The desired cell needs to be
        visible for this function be able to work
        :param row: Table relative row index
        :param column: Table column index
        :param skip_error: Skip this function if occur any error
        """
        try:
            self.table_obj.getCell(row, column).SetFocus()
            self.session.findById(f"wnd[{self.window}]").sendVKey(2)
        except:
            if not skip_error:
                raise Exception("Click Cell Failed.")

    def get_table_content(self, skip_error: bool = False) -> Dict[str, List[str]]:
        """
        Deprecated: use `Table.get_content` instead.

        Store all the content from a SAP Table, the data will be stored and returned in a dictionary with 'header' and
        'content' items
        :param skip_error: Skip this function if occur any error
        :return: A dictionary with 'header' and 'content' items
        """
        warnings.warn("Deprecated in 1.1 "
                      "Table.get_table_content will be removed in 1.5 "
                      "Use Table.get_content instead.", DeprecationWarning, stacklevel=2)

        try:
            self._return_table().VerticalScrollbar.Position = 0
            obj_now = self._return_table()
            added_rows = []

            header = []
            content = []

            columns = obj_now.columns.count
            visible_rows = obj_now.visibleRowCount
            rows = obj_now.rowCount / visible_rows

            iteration_plus = 0
            if obj_now.rowCount > visible_rows and self.session.info.transaction != 'MD04':
                iteration_plus = 1

            absolute_row = 0
            visible_row = 0

            for c in range(columns):
                col_name = obj_now.columns.elementAt(c).title
                header.append(col_name)

            for i in range(0, int(rows) + iteration_plus):
                obj_now.VerticalScrollbar.Position = (visible_row + 1) * i
                obj_now = self._return_table()
                for visible_row in range(visible_rows):
                    active_row = []
                    for c in range(columns):
                        try:
                            active_row.append(obj_now.getCell(visible_row, c).text)
                        except:
                            active_row.append(None)

                    absolute_row += 1

                    if not all(value is None for value in active_row) and absolute_row not in added_rows:
                        added_rows.append(absolute_row)
                        content.append(active_row)

                obj_now.VerticalScrollbar.Position = (visible_row + 1) * i
                obj_now = self._return_table()
            return {'header': header, 'content': content}

        except:
            if not skip_error:
                raise Exception("Get table content failed.")

    def get_content(self, skip_error: bool = False) -> Dict[str, List[str]]:
        """
        Store all the content from a SAP Table, the data will be stored and returned in a dictionary with 'header' and
        'content' items
        :param skip_error: Skip this function if occur any error
        :return: A dictionary with 'header' and 'content' items
        """

        try:
            self._return_table().VerticalScrollbar.Position = 0
            obj_now = self._return_table()
            added_rows = []

            header = []
            content = []

            columns = obj_now.columns.count
            visible_rows = obj_now.visibleRowCount
            rows = obj_now.rowCount / visible_rows

            iteration_plus = 0
            if obj_now.rowCount > visible_rows and self.session.info.transaction != 'MD04':
                iteration_plus = 1

            absolute_row = 0
            visible_row = 0

            for c in range(columns):
                col_name = obj_now.columns.elementAt(c).title
                header.append(col_name)

            for i in range(0, int(rows) + iteration_plus):
                obj_now.VerticalScrollbar.Position = (visible_row + 1) * i
                obj_now = self._return_table()
                for visible_row in range(visible_rows):
                    active_row = []
                    for c in range(columns):
                        try:
                            active_row.append(obj_now.getCell(visible_row, c).text)
                        except:
                            active_row.append(None)

                    absolute_row += 1

                    if not all(value is None for value in active_row) and absolute_row not in added_rows:
                        added_rows.append(absolute_row)
                        content.append(active_row)

                obj_now.VerticalScrollbar.Position = (visible_row + 1) * i
                obj_now = self._return_table()
            return {'header': list(header), 'content': list(content)}

        except:
            if not skip_error:
                raise Exception("Get table content failed.")

    def get_columns(self, *column_text: str, skip_error: bool = False) -> Union[Dict[str, List[str]], list]:
        """
        Return each column content
        :param column_id: Table list of columns
        :param skip_error: Skip this function if occur any error
        :return: A dictionary/list with the desired content, when more than one column is desired, a dictionary with 'header' and 'content' items will be returned
        """
        try:
            self._return_table().VerticalScrollbar.Position = 0
            obj_now = self._return_table()
            added_rows = []

            header = []
            content = []

            columns = obj_now.columns.count
            visible_rows = obj_now.visibleRowCount
            rows = obj_now.rowCount / visible_rows

            iteration_plus = 0
            if obj_now.rowCount > visible_rows:
                iteration_plus = 1

            absolute_row = 0

            for c in range(columns):
                col_name = obj_now.columns.elementAt(c).title
                if col_name in column_text:
                    header.append(col_name)

            for i in range(int(rows) + iteration_plus):
                for visible_row in range(visible_rows):
                    active_row = []
                    for c in range(columns):
                        if obj_now.columns.elementAt(c).title in header:
                            if len(header) > 1:
                                    try:
                                        active_row.append(obj_now.getCell(visible_row, c).text)
                                    except:
                                        active_row.append(None)
                            else:
                                try:
                                    content.append(obj_now.getCell(visible_row, c).text)
                                except:
                                    content.append(None)

                    absolute_row += 1

                    if not all(value is None for value in active_row) and absolute_row not in added_rows:
                        added_rows.append(absolute_row)
                        if len(header) > 1:
                            content.append(active_row)

                obj_now.VerticalScrollbar.Position = (visible_row + 1) * i
                obj_now = self._return_table()

            if len(header) > 1:
                return {'header': list(header), 'content': list(content)}
            else:
                return list(content)
        except:
            if not skip_error:
                raise Exception("Get table content failed.")
