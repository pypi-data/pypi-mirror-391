
# sap_functions
Library with utility classes and functions to facilitate the development of SAP automations in python.

This module is built on top of SAP Scripting and aims to making the development of automated workflows easier and quicker.

## Implementation example
```python
from sap_functions import SAP

sap = SAP()
sap.select_transaction("COOIS")
```
This script:

Checks for existant SAP GUI instances.
Connects to that instance.
Write "COOIS" in the transaction field.
# Classes overview


## Module `src.sap_functions.base_sap_connection`

### Class `BaseSapConnection`

**Methods:**
- `__init__(self, window: int = 0)`: Initialize self.  See help(type(self)) for accurate signature.


## Module `src.sap_functions.grid`

### Class `Grid`

**Methods:**
- `__init__(self, grid_obj: SAPGridView, session: SAPGuiSession)`: Initialize self.  See help(type(self)) for accurate signature.
- `click_cell(self, index: int, column_id: str) -> None`: This function will select and double-click in a SAP Grid cell
- `count_rows(self) -> int`: This function will count all the rows in the current Grid
- `get_cell_value(self, index: int, column_id: str) -> str`: Get the value of a specific Grid cell
- `get_column_id(self, column_name: str) -> str`: This function will return the column id based on its column name
- `get_columns(self, *column_id: str) -> Union`: Return each column content
- `get_content(self) -> Dict`: Store all the content from a SAP Grid, the data will be stored and returned in a dictionary with 'header' and
- `get_grid_columns(self, *column_id: str) -> Union`: Deprecated: use `Grid.get_columns` instead.
- `get_grid_content(self) -> Dict`: Deprecated: use `Grid.get_content` instead.
- `get_grid_row(self, row: int) -> list`: Deprecated: use `Grid.get_row` instead.
- `get_row(self, row: int) -> list`: Get a grid row content
- `open_cell_modal(self, index: int, column_id: str) -> None`: This function will select and open a cell modal in a SAP Grid cell
- `press_button(self, field_name: str, skip_error: bool = False) -> None`: This function will press any button in the SAP Grid component
- `press_nested_button(self, *nested_fields: str, skip_error: bool = False) -> None`: This function needs to receive several strings that have the texts that appear written in the button destination
- `select_all_content(self) -> None`: Select all the table, using the SAP native function to select all items
- `select_column(self, column_id: str) -> None`: Select a specific column
- `select_layout(self, layout: str) -> None`: This function will select the desired Grid Layout when a SAP select Layout Pop up is open


## Module `src.sap_functions.label`

### Class `Label`

**Methods:**
- `__init__(self, session: SAPGuiSession, window: int = 0)`: Initialize self.  See help(type(self)) for accurate signature.
- `get_all_screen_labels(self) -> list`: This function will return each label row in the SAP Screen
- `get_content(self) -> Dict`: Store all the content from a SAP Label, the data will be stored and returned in a dictionary with
- `get_label_content(self) -> Dict`: Deprecated: use `Label.get_content` instead.


## Module `src.sap_functions.node`

### Class `Node`

**Methods:**
- `__init__(self, node_obj: CDispatch)`: Initialize self.  See help(type(self)) for accurate signature.
- `click_selected_node(self)`: Double-click the Node selected previously
- `expand_selected_node(self)`: Expand the Node selected previously
- `get_content(self) -> list`: Get all Nodes names in a list format
- `get_node_content(self) -> list`: Deprecated: use `Node.get_content` instead.
- `select_node(self, node_text: str, target_index: int = 0, skip_error: bool = False)`: Select a specific Node based on the text inside of it


## Module `src.sap_functions.sap`

### Class `SAP`

**Methods:**
- `__init__(self, window: int = 0) -> None`: Initialize self.  See help(type(self)) for accurate signature.
- `change_active_tab(self, selected_tab: Union, skip_error: bool = False) -> None`: This function will try to select the transaction tab using the number "selected_tab"
- `choose_text_combo(self, field_name: str, desired_text: str, target_index: int = 0, selected_tab: Union = 0, skip_error: bool = False) -> None`: This function has the ability to choose a specific text that is found within a combo box component
- `clean_all_fields(self, selected_tab: Union = 0, skip_error = False) -> None`: Clean all the input fields in the actual screen
- `find_text_field(self, field_name: str, selected_tab: Union = 0) -> bool`: Verify if a text exists in the SAP screen
- `flag_field(self, field_name: str, desired_operator: bool, target_index: int = 0, selected_tab: Union = 0, skip_error: bool = False) -> None`: This function can flag and unflag checkboxes based on the field_name, it will flag/unflag the checkbox in the
- `flag_field_at_side(self, field_name: str, desired_operator: bool, side_index: int = 0, target_index: int = 0, selected_tab: Union = 0, skip_error: bool = False) -> None`: This function can flag and unflag checkboxes based on the field_name, it will flag/unflag the checkbox at the
- `get_footer_message(self) -> str`: Get the message text that is in the SAP Footer
- `get_grid(self, target_index: int = 0) -> Grid`: Get the SAP Grid object from the current SAP Grid Window
- `get_label(self) -> Label`: Get the SAP Label object from the current SAP Label Window
- `get_node(self, target_index: int = 0) -> Node`: Get the SAP Node object from the current SAP Node Window
- `get_table(self, target_index: int = 0) -> Table`: Get the SAP Table object from the current SAP Table Window
- `get_text_at_side(self, field_name, side_index: int, target_index: int = 0, selected_tab: Union = 0) -> str`: This function will return the text next to the text received as a parameter
- `get_tree(self) -> Tree`: Get the SAP Tree object from the current SAP Tree Window
- `insert_variant(self, variant_name: str, skip_error: bool = False) -> None`: This function will try to press the "Get Variant" button in the transaction, after that it will overwrite the
- `multiple_selection_field(self, field_name: str, target_index: int = 0, selected_tab: Union = 0, skip_error: bool = False) -> None`: This function will press the "Multiple Selection" button in the respective field
- `multiple_selection_paste_data(self, data: list, delete_values: bool = False, skip_error: bool = False) -> None`: With the Multiple Selection window open, it's possible to execute this function to easily paste all the data
- `navigate_into_menu_header(self, *nested_path: str) -> None`: This function needs to receive several strings that have the texts that appear written in the header destination
- `open_focused_field_modal(self)`: This function will open the modal of a focused field
- `option_field(self, field_name: str, target_index: int = 0, selected_tab: Union = 0, skip_error: bool = False) -> None`: This function will select an option field
- `option_field_at_side(self, field_name: str, side_index: int = 0, target_index: int = 0, selected_tab: Union = 0, skip_error: bool = False) -> None`: This function will select an option field
- `press_button(self, field_name: str, target_index: int = 0, selected_tab: Union = 0, skip_error: bool = False) -> None`: Press any button in the SAP screens, except in shells and tables components
- `run_actual_transaction(self, skip_error: bool = False) -> None`: Run the active transaction, this function will try to press Enter, and after that will try to press F8
- `save_file(self, file_name: str, path: str, option: int = 0, type_of_file: str = 'txt', skip_error: bool = False) -> None`: This function will easily navigate into SAP menu header to save the current transaction data, commonly used to
- `select_main_screen(self, skip_error: bool = False) -> None`: Navigate to the SAP main Screen
- `select_transaction(self, transaction: str) -> None`: Navigate to a transaction in SAP GUI
- `set_focus(self, field_name, side_index: int = 0, target_index: int = 0, selected_tab: Union = 0)`: This function will select/focus in the field with the text received as a parameter
- `write_text_field(self, field_name: str, desired_text: str, target_index: int = 0, selected_tab: Union = 0, skip_error: bool = False) -> None`: This function will write the desired text in the respective input at the side of the field name
- `write_text_field_until(self, field_name: str, desired_text: str, target_index: int = 0, selected_tab: Union = 0, skip_error: bool = False) -> None`: This function will write the desired text in the "until" field in the respective input at the side of the


## Module `src.sap_functions.session`

### Class `GuiComponent`

**Methods:**
- `Select(self) -> None`: 
- `__annotate__(format)`: 
- `__getitem__(self, index: int) -> GuiComponent`: 
- `__iter__(self) -> Iterator`: 
- `change(self) -> None`: 
- `clickCurrentCell(self)`: 
- `containerType(self) -> str`: 
- `press(self) -> None`: 
- `sendVKey(self, key: int) -> None`: 
- `setFocus(self) -> None`: 
- `visualize(self) -> None`: 

### Class `SAPGridView`

**Methods:**
- `__annotate__(format)`: 
- `clearSelection(self) -> None`: Calling clearSelection removes all row, column and cell selections
- `clickCurrentCell(self) -> None`: This function emulates a mouse click on the current cell
- `contextMenu(self) -> None`: Calling contextMenu emulates the context menu request
- `doubleClickCurrentCell(self) -> None`: This function emulates a mouse double click on the current cell
- `getCellValue(self, row: int, column: str) -> str`: Returns the value of the cell as a string
- `selectAll(self) -> None`: This function selects the whole grid content (i.e. all rows and all columns).
- `selectColumn(self, column: str) -> None`: This function adds the specified column to the collection of the selected columns
- `selectContextMenuItem(self, item: str) -> None`: Select an item from the control’s context menu
- `setCurrentCell(self, row: int, column: str) -> None`: If row and column identify a valid cell, this cell becomes the current cell. Otherwise, an exception is raised.

### Class `SAPGuiFrameWindow`

**Methods:**
- `__annotate__(format)`: 
- `close(self) -> None`: The function attempts to close the window. Trying to close the last main window of a session will not succeed immediately; the dialog ‘Do you really want to log off?’ will be displayed first

### Class `SAPGuiInfo`

**Methods:**
- `__annotate__(format)`: 

### Class `SAPGuiScrollbar`

**Methods:**
- `__annotate__(format)`: 

### Class `SAPGuiSession`

**Methods:**
- `CreateSession(self) -> None`: 
- `EndTransaction(self) -> None`: 
- `__annotate__(format)`: 
- `findById(self, identifier: str) -> GuiComponent`: 
- `startTransaction(self, transaction: str) -> None`: 


## Module `src.sap_functions.table`

### Class `Table`

**Methods:**
- `__init__(self, table_obj: CDispatch, session: SAPGuiSession, target_index: int, window: int = 0)`: Initialize self.  See help(type(self)) for accurate signature.
- `_return_table(self)`: 
- `click_cell(self, row: int, column: int, skip_error: bool = False) -> None`: Focus in a cell and double-click in it, using the relative visible table row. The desired cell needs to be
- `count_visible_rows(self, skip_error: bool = False) -> int`: Count all the visible rows from a SAP Table
- `flag_cell(self, row: int, column: int, desired_operator: bool, skip_error: bool = False) -> None`: Flags a checkbox in a SAP Table cell, using the relative visible table row. The desired cell needs to be
- `get_cell_value(self, row: int, column: int, skip_error: bool = False) -> str`: Return the content of a SAP Table cell, using the relative visible table row. The desired cell needs to be
- `get_columns(self, *column_text: str, skip_error: bool = False) -> Union`: Return each column content
- `get_content(self, skip_error: bool = False) -> Dict`: Store all the content from a SAP Table, the data will be stored and returned in a dictionary with 'header' and
- `get_table_content(self, skip_error: bool = False) -> Dict`: Deprecated: use `Table.get_content` instead.
- `select_entire_row(self, absolute_row: int, skip_error: bool = False) -> None`: Select the entire row from a SAP Table, it uses the absolute table row. The desired cell needs to be
- `unselect_entire_row(self, absolute_row: int, skip_error: bool = False) -> None`: Unselect the entire row from a SAP Table, it uses the absolute table row. The desired cell needs to be
- `write_cell_value(self, row: int, column: int, desired_text: str, skip_error: bool = False) -> None`: Write any value in a SAP Table cell, using the relative visible table row. The desired cell needs to be


## Module `src.sap_functions.tree`

### Class `Tree`

**Methods:**
- `__init__(self, tree_obj: CDispatch)`: Initialize self.  See help(type(self)) for accurate signature.
- `get_columns(self, *column_text: str) -> Union`: Return each column content
- `get_content(self, skip_error: bool = False) -> Dict`: Store all the content from a SAP Tree, the data will be stored and returned in a dictionary with 'header' and
- `get_tree_columns(self, *column_text: str) -> Union`: Deprecated: use `Tree.get_columns` instead.
- `get_tree_content(self, skip_error: bool = False) -> Dict`: Deprecated: use `Tree.get_content` instead.


## Module `src.sap_functions.utils`

### Top-level Functions

- `active_window(sap) -> int`: 
- `count_and_create_sap_screens(connection: CDispatch, window: int)`: 
- `generic_conditionals(sap, index: int, children: CDispatch, objective: str) -> bool`: 
- `get_sap_connection() -> CDispatch`: 
- `scroll_through_fields(sap, extension: str, objective: str) -> bool`: 
- `scroll_through_grid(sap, extension: str) -> Union`: 
- `scroll_through_node(sap, extension: str) -> Union`: 
- `scroll_through_table(sap, extension: str) -> Union`: 
- `scroll_through_tabs_by_id(sap, area: GuiComponent, extension: str, selected_tab: int) -> GuiComponent`: 
- `scroll_through_tabs_by_name(sap, area: GuiComponent, extension: str, tab_name: str) -> GuiComponent`: 
- `scroll_through_tree(sap, extension: str) -> Union`: 
