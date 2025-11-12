from .utils import *
from .session import SAPGuiSession, SAPGridView
import warnings
from typing import Dict, List, Union


# https://help.sap.com/docs/sap_gui_for_windows/b47d018c3b9b45e897faf66a6c0885a8/4af24c3281fb4d6a809e53238562d3b2.html?locale=en-US
class Grid:
    def __init__(self, grid_obj: SAPGridView, session: SAPGuiSession):
        self._component_target_index = 0
        self.grid_obj: SAPGridView = grid_obj
        self.session = session
        self.window = active_window(self)
        self.commands_spec = [
            {
                'get_id_method_name': 'GetToolbarButtonId',
                'get_tooltip_method_name': 'GetToolbarButtonTooltip',
                'get_text_method_name': 'GetToolbarButtonText',
                'press_method_name': 'pressToolbarContextButton',
                'press_context_name': 'pressToolbarContextButton',
                'select_context_item_name': 'SelectContextMenuItemByText'
            },
            {
                'get_id_method_name': 'GetButtonId',
                'get_tooltip_method_name': 'GetButtonTooltip',
                'get_text_method_name': 'GetToolbarButtonText',
                'press_method_name': 'pressButton',
                'press_context_name': 'pressContextButton',
                'select_context_item_name': 'SelectContextMenuItemByText'
            }
        ]

    def select_layout(self, layout: str) -> None:
        """
        This function will select the desired Grid Layout when a SAP select Layout Pop up is open
        :param layout: The desired Layout name
        """
        try:
            window = active_window(self)
            grid_layout_obj = scroll_through_grid(self, f'wnd[{window}]/usr')

            if not grid_layout_obj:
                raise Exception()

            grid_layout_obj.selectColumn("VARIANT")
            grid_layout_obj.contextMenu()
            grid_layout_obj.selectContextMenuItem("&FILTER")
            self.session.findById("wnd[2]/usr/ssub%_SUBSCREEN_FREESEL:SAPLSSEL:1105/ctxt%%DYN001-LOW").text = layout
            self.session.findById("wnd[2]/tbar[0]/btn[0]").press()
            self.session.findById(
                "wnd[1]/usr/ssubD0500_SUBSCREEN:SAPLSLVC_DIALOG:0501/cntlG51_CONTAINER/shellcont/shell").selectedRows = "0"
            self.session.findById(
                "wnd[1]/usr/ssubD0500_SUBSCREEN:SAPLSLVC_DIALOG:0501/cntlG51_CONTAINER/shellcont/shell").clickCurrentCell()
        except:
            raise Exception("Select layout failed.")

    def count_rows(self) -> int:
        """
        This function will count all the rows in the current Grid
        :return: A integer with the total number of rows in the current Grid
        """
        try:
            rows = self.grid_obj.rowCount
            if rows > 0:
                visible_row = self.grid_obj.visibleRowCount
                visible_row0 = self.grid_obj.visibleRowCount
                n_page_down = rows // visible_row0
                if n_page_down > 1:
                    for j in range(1, n_page_down + 1):
                        try:
                            self.grid_obj.firstVisibleRow = visible_row - 1
                            visible_row += visible_row0
                        except:
                            break
                self.grid_obj.firstVisibleRow = 0
            return rows
        except:
            raise Exception("Count rows failed.")

    def get_column_id(self, column_name: str) -> str:
        """
        This function will return the column id based on its column name
        :param column_name: The target column's name
        :return: A string with the respective column id
        """
        grid_column = self.grid_obj.columnOrder
        cols = self.grid_obj.columnCount

        for c in range(cols):
            item = self.grid_obj.getCellValue(-1, grid_column[c])
            if column_name == item:
                return grid_column[c]

    def get_cell_value(self, index: int, column_id: str) -> str:
        """
        Get the value of a specific Grid cell
        :param index: Row number of the desired cell
        :param column_id: Grid column "Field Name" found in the respective column Technical Information tab
        :return: The value of the cell
        """
        try:
            return self.grid_obj.getCellValue(index, column_id)
        except:
            raise Exception("Get cell value failed.")

    def get_grid_columns(self, *column_id: str) -> Union[Dict[str, List[str]], list]:
        """
        Deprecated: use `Grid.get_columns` instead.

        Return each column content
        :param column_id: Grid list of columns "Field Name" found in the respective column Technical Information tab
        :return: A dictionary/list with the desired content, when more than one column is desired, a dictionary with 'header' and 'content' items will be returned
        """
        warnings.warn("Deprecated in 1.1 "
                      "Grid.get_grid_columns will be removed in 1.5 "
                      "Use Grid.get_columns instead.", DeprecationWarning, stacklevel=2)
        try:
            rows = self.count_rows()
            if len(column_id) > 1:
                header = [self.grid_obj.getCellValue(i, c) for c in column_id for i in range(-1, 0)]
                data = [[self.grid_obj.getCellValue(i, c) for c in column_id] for i in range(0, rows)]
                return {'header': header, 'content': data}
            else:
                data = [self.grid_obj.getCellValue(i, column_id[0]) for i in range(0, rows)]
                return data

        except:
            raise Exception("Get Grid Columns Failed.")

    def get_columns(self, *column_id: str) -> Union[Dict[str, List[str]], list]:
        """
        Return each column content
        :param column_id: Grid list of columns "Field Name" found in the respective column Technical Information tab
        :return: A dictionary/list with the desired content, when more than one column is desired, a dictionary with 'header' and 'content' items will be returned
        """
        try:
            rows = self.count_rows()
            if len(column_id) > 1:
                header = [self.grid_obj.getCellValue(i, c) for c in column_id for i in range(-1, 0)]
                data = [[self.grid_obj.getCellValue(i, c) for c in column_id] for i in range(0, rows)]
                return {'header': header, 'content': data}
            else:
                data = [self.grid_obj.getCellValue(i, column_id[0]) for i in range(0, rows)]
                return data

        except:
            raise Exception("Get Grid Columns Failed.")

    def get_grid_row(self, row: int) -> list:
        """
        Deprecated: use `Grid.get_row` instead.

        Get a grid row content
        :param row: The desired grid row
        :return: A list with the row content
        """
        warnings.warn("Deprecated in 1.1 "
                      "Grid.get_grid_row will be removed in 1.5 "
                      "Use Grid.get_row instead.", DeprecationWarning, stacklevel=2)
        try:
            grid_column = self.grid_obj.columnOrder
            cols = self.grid_obj.columnCount

            data = [self.grid_obj.getCellValue(row, grid_column[c]) for c in range(cols)]
            return data

        except:
            raise Exception("Get Grid Row Failed.")

    def get_row(self, row: int) -> list:
        """
        Get a grid row content
        :param row: The desired grid row
        :return: A list with the row content
        """
        try:
            grid_column = self.grid_obj.columnOrder
            cols = self.grid_obj.columnCount

            data = [self.grid_obj.getCellValue(row, grid_column[c]) for c in range(cols)]
            return data

        except:
            raise Exception("Get Grid Row Failed.")

    def get_grid_content(self) -> Dict[str, List[str]]:
        """
        Deprecated: use `Grid.get_content` instead.

        Store all the content from a SAP Grid, the data will be stored and returned in a dictionary with 'header' and
        'content' items
        :return: A dictionary with 'header' and 'content' items
        """
        warnings.warn("Deprecated in 1.1 "
                      "Grid.get_grid_content will be removed in 1.5 "
                      "Use Grid.get_content instead.", DeprecationWarning, stacklevel=2)
        try:
            grid_column = self.grid_obj.columnOrder
            rows = self.count_rows()
            cols = self.grid_obj.columnCount
            header = [self.grid_obj.getCellValue(i, grid_column[c]) for c in range(cols) for i in range(-1, 0)]
            data = [[self.grid_obj.getCellValue(i, grid_column[c]) for c in range(cols)] for i in range(0, rows)]
            return {'header': header, 'content': data}

        except:
            raise Exception("Get all Grid Content Failed.")

    def get_content(self) -> Dict[str, List[str]]:
        """
        Store all the content from a SAP Grid, the data will be stored and returned in a dictionary with 'header' and
        'content' items
        :return: A dictionary with 'header' and 'content' items
        """
        try:
            grid_column = self.grid_obj.columnOrder
            rows = self.count_rows()
            cols = self.grid_obj.columnCount
            header = [self.grid_obj.getCellValue(i, grid_column[c]) for c in range(cols) for i in range(-1, 0)]
            data = [[self.grid_obj.getCellValue(i, grid_column[c]) for c in range(cols)] for i in range(0, rows)]
            return {'header': header, 'content': data}

        except:
            raise Exception("Get all Grid Content Failed.")

    def select_all_content(self) -> None:
        """
        Select all the table, using the SAP native function to select all items
        """
        try:
            self.grid_obj.selectAll()
        except:
            raise Exception("Select All Content Failed.")

    def select_column(self, column_id: str) -> None:
        """
        Select a specific column
        :param column_id: Grid column "Field Name" found in the respective column Technical Information tab
        """
        try:
            self.grid_obj.selectColumn(column_id)
        except:
            raise Exception("Select Column Failed.")

    def click_cell(self, index: int, column_id: str) -> None:
        """
        This function will select and double-click in a SAP Grid cell
        :param index: Row number of the desired cell
        :param column_id: Grid column "Field Name" found in the respective column Technical Information tab
        """
        try:
            self.grid_obj.setCurrentCell(index, column_id)
            self.grid_obj.doubleClickCurrentCell()
        except:
            raise Exception("Click Cell Failed.")

    def open_cell_modal(self, index: int, column_id: str) -> None:
        """
        This function will select and open a cell modal in a SAP Grid cell
        :param index: Row number of the desired cell
        :param column_id: Grid column "Field Name" found in the respective column Technical Information tab
        """
        try:
            self.grid_obj.setCurrentCell(index, column_id)
            self.session.findById(f'wnd[{self.window}]').sendVKey(4)
        except:
            raise Exception("Open Cell Modal Failed.")

    def press_button(self, field_name: str, skip_error: bool = False) -> None:
        """
        This function will press any button in the SAP Grid component
        :param field_name: The button that you want to press, this text need to be inside the button or in the tooltip of the button
        :param skip_error: Skip this function if occur any error
        """
        for command_info in self.commands_spec:
            try:
                get_id_func = getattr(self.grid_obj, command_info['get_id_method_name'])
                get_tooltip_func = getattr(self.grid_obj, command_info['get_tooltip_method_name'])
                get_text_func = getattr(self.grid_obj, command_info['get_text_method_name'])
                press_func = getattr(self.grid_obj, command_info['press_method_name'])

                for i in range(self.grid_obj.toolbarButtonCount):
                    button_id = get_id_func(i)
                    button_tooltip = get_tooltip_func(i)
                    button_text = get_text_func(i)
                    if field_name in button_tooltip or field_name in button_text:
                        press_func(button_id)
                        return
            except:
                pass

        if not skip_error:
            raise Exception("Press button failed")

    def press_nested_button(self, *nested_fields: str, skip_error: bool = False) -> None:
        """
        This function needs to receive several strings that have the texts that appear written in the button destination
        that you want to press, it must be written in the order that it appears to reach the final button
        :param nested_fields: The nested path that you want to navigate to press the button
        :param skip_error: Skip this function if occur any error
        """
        for command_info in self.commands_spec:
            try:
                get_id_func = getattr(self.grid_obj, command_info['get_id_method_name'])
                get_tooltip_func = getattr(self.grid_obj, command_info['get_tooltip_method_name'])
                press_func = getattr(self.grid_obj, command_info['press_context_name'])
                select_func = getattr(self.grid_obj, command_info['select_context_item_name'])

                for i in range(100):
                    button_id = get_id_func(i)
                    button_tooltip = get_tooltip_func(i)
                    if nested_fields[0] == button_tooltip:
                        press_func(button_id)
                        select_func(nested_fields[1])
                        return
            except:
                pass

        if not skip_error:
            raise Exception("Press nested button failed")
