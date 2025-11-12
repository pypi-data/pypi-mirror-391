import os
import uuid
from .tree import Tree
from .node import Node
from .grid import Grid
from .table import Table
from .label import Label
from .utils import *
from .base_sap_connection import BaseSapConnection
from typing import Union


# SAP Scripting Documentation:
# https://help.sap.com/docs/sap_gui_for_windows/b47d018c3b9b45e897faf66a6c0885a8/a2e9357389334dc89eecc1fb13999ee3.html

# module SAP Functions, development started in 2024/03/01
class SAP(BaseSapConnection):

    def __init__(self, window: int = 0) -> None:
        BaseSapConnection.__init__(self, window)
        self._component_target_index = None
        self._desired_operator = None
        self._selected_tab_id = None
        self._desired_text = None
        self._target_index = None
        self._target_tab = None
        self._side_index = None
        self._field_name = None
        self._found_text = None
        self._selected_tab_name = ''
        if self.session.info.transaction == 'S000':
            self.select_main_screen()

    def select_transaction(self, transaction: str) -> None:
        """
        Navigate to a transaction in SAP GUI
        :param transaction: The name of the desired transaction
        """
        try:
            transaction_upper = transaction.upper()
            self.session.startTransaction(transaction_upper)
            if self.session.activeWindow.name == 'wnd[1]' and 'CN' in transaction_upper:
                self.session.findById("wnd[1]/usr/ctxtTCNT-PROF_DB").Text = "000000000001"
                self.session.findById("wnd[1]/tbar[0]/btn[0]").press()
            if not self.session.info.transaction == transaction_upper:
                raise Exception()
        except:
            raise Exception("Select transaction failed.\n" + self.get_footer_message())

    def select_main_screen(self, skip_error: bool = False) -> None:
        """
        Navigate to the SAP main Screen
        :param skip_error: Skip this function if occur any error
        """
        try:
            if not self.session.info.transaction == "SESSION_MANAGER":
                self.session.startTransaction('SESSION_MANAGER')
                if self.session.activeWindow.name == "wnd[1]":
                    self.session.findById("wnd[1]/tbar[0]/btn[0]").press()
        except:
            if not skip_error: raise Exception("Select main screen failed.")

    def clean_all_fields(self, selected_tab: Union[int, str] = 0, skip_error=False) -> None:
        """
        Clean all the input fields in the actual screen
        :param selected_tab: Transaction desired tab
        :param skip_error: Skip this function if occur any error
        """
        try:
            self.window = active_window(self)
            if type(selected_tab).__name__ == 'int':
                area = scroll_through_tabs_by_id(self, self.session.findById(f"wnd[{self.window}]/usr"),
                                                 f"wnd[{self.window}]/usr", selected_tab)
            else:
                area = scroll_through_tabs_by_name(self, self.session.findById(f"wnd[{self.window}]/usr"),
                                                   f"wnd[{self.window}]/usr", selected_tab)

            children = area.children
            for child in children:
                if child.type == "GuiCTextField":
                    try:
                        child.Text = ""
                    except:
                        pass
        except:
            if not skip_error: raise Exception("Clean all fields failed.")

    def run_actual_transaction(self, skip_error: bool = False) -> None:
        """
        Run the active transaction, this function will try to press Enter, and after that will try to press F8
        :param skip_error: Skip this function if occur any error
        """
        try:
            self.window = active_window(self)
            screen_title = self.session.activeWindow.text
            self.session.findById(f'wnd[{self.window}]').sendVKey(0)
            if screen_title == self.session.activeWindow.text:
                self.session.findById(f'wnd[{self.window}]').sendVKey(8)
        except:
            if not skip_error:
                raise Exception("Run actual transaction failed.")

    def insert_variant(self, variant_name: str, skip_error: bool = False) -> None:
        """
        This function will try to press the "Get Variant" button in the transaction, after that it will overwrite the
        "Created By" field with an empty string, and fill the "Variant" field with the variant_name param, THIS FUNCTION
        DOESN'T WORK IN EVERY TRANSACTION
        :param variant_name: The transaction variant name
        :param skip_error: Skip this function if occur any error
        """
        try:
            self.session.findById("wnd[0]/tbar[1]/btn[17]").press()
            if self.session.activeWindow.name == 'wnd[1]':
                self.session.findById("wnd[1]/usr/txtV-LOW").Text = variant_name
                self.session.findById("wnd[1]/usr/txtENAME-LOW").Text = ""
                self.session.findById("wnd[1]/tbar[0]/btn[8]").press()
                if self.session.activeWindow.name == 'wnd[1]':
                    raise Exception()
        except:
            if not skip_error: raise Exception("Insert variant failed.")

    def change_active_tab(self, selected_tab: Union[int, str], skip_error: bool = False) -> None:
        """
        This function will try to select the transaction tab using the number "selected_tab"
        :param selected_tab: Tab desired number, the SAP default tab is 0
        :param skip_error: Skip this function if occur any error
        """
        try:
            self.window = active_window(self)
            if type(selected_tab).__name__ == 'int':
                area = scroll_through_tabs_by_id(self, self.session.findById(f"wnd[{self.window}]/usr"),
                                                 f"wnd[{self.window}]/usr", selected_tab)
                try:
                    area.Select()
                except:
                    pass
            else:
                self._target_tab = selected_tab
                scroll_through_fields(self, f"wnd[{self.window}]/usr", 'select_tab_by_name')

        except:
            if not skip_error: raise Exception("Change active tab failed.")

    def write_text_field(self, field_name: str, desired_text: str, target_index: int = 0,
                         selected_tab: Union[int, str] = 0,
                         skip_error: bool = False) -> None:
        """
        This function will write the desired text in the respective input at the side of the field name
        :param field_name: The text that precedes the desired text field box
        :param desired_text: The text that will overwrite the actual text in the field box
        :param target_index: Target index, determines how many occurrences precede the desired field
        :param selected_tab: Desired Tab, where this field can be found, the SAP default tab is 0
        :param skip_error: Skip this function if occur any error
        """
        try:
            self.window = active_window(self)
            self._field_name = field_name
            self._desired_text = desired_text
            self._target_index = target_index
            if selected_tab != self._selected_tab_id and selected_tab != self._selected_tab_name:
                self.change_active_tab(selected_tab)
            if not scroll_through_fields(self, f"wnd[{self.window}]/usr", 'write_text_field'):
                raise Exception()
        except:
            if not skip_error: raise Exception("Write text field failed.")

    def write_text_field_until(self, field_name: str, desired_text: str, target_index: int = 0,
                               selected_tab: Union[int, str] = 0,
                               skip_error: bool = False) -> None:
        """
        This function will write the desired text in the "until" field in the respective input at the side of the
        field name
        :param field_name: The text that precedes the desired text field box
        :param desired_text: The text that will overwrite the actual text in the field box
        :param target_index: Target index, determines how many occurrences precede the desired field
        :param selected_tab: Desired Tab, where this field can be found, the SAP default tab is 0
        :param skip_error: Skip this function if occur any error
        """
        try:
            self.window = active_window(self)
            self._field_name = field_name
            self._desired_text = desired_text
            self._target_index = target_index
            if selected_tab != self._selected_tab_id and selected_tab != self._selected_tab_name:
                self.change_active_tab(selected_tab)
            if not scroll_through_fields(self, f"wnd[{self.window}]/usr", 'write_text_field_until'):
                raise Exception()
        except:
            if not skip_error: raise Exception("Write text field until failed.")

    def choose_text_combo(self, field_name: str, desired_text: str, target_index: int = 0,
                          selected_tab: Union[int, str] = 0,
                          skip_error: bool = False) -> None:
        """
        This function has the ability to choose a specific text that is found within a combo box component
        :param field_name: The text that precedes the desired combo box
        :param desired_text: The text that will be selected in the combo box
        :param target_index: Target index, determines how many occurrences precede the desired field
        :param selected_tab: Desired Tab, where this field can be found, the SAP default tab is 0
        :param skip_error: Skip this function if occur any error
        """
        try:
            self.window = active_window(self)
            self._field_name = field_name
            self._desired_text = desired_text
            self._target_index = target_index
            if selected_tab != self._selected_tab_id and selected_tab != self._selected_tab_name:
                self.change_active_tab(selected_tab)
            if not scroll_through_fields(self, f"wnd[{self.window}]/usr", 'choose_text_combo'):
                raise Exception()
        except:
            if not skip_error: raise Exception("Choose text combo failed.")

    def flag_field(self, field_name: str, desired_operator: bool, target_index: int = 0,
                   selected_tab: Union[int, str] = 0,
                   skip_error: bool = False) -> None:
        """
        This function can flag and unflag checkboxes based on the field_name, it will flag/unflag the checkbox in the
        respective field_name
        :param field_name: The text with the checkbox you want to flag/unflag
        :param desired_operator: Boolean to say if you want to flag or unflag the checkbox
        :param target_index: Target index, determines how many occurrences precede the desired field
        :param selected_tab: Desired Tab, where this field can be found, the SAP default tab is 0
        :param skip_error: Skip this function if occur any error
        """
        try:
            self.window = active_window(self)
            self._field_name = field_name
            self._desired_operator = desired_operator
            self._target_index = target_index
            if selected_tab != self._selected_tab_id and selected_tab != self._selected_tab_name:
                self.change_active_tab(selected_tab)
            if not scroll_through_fields(self, f"wnd[{self.window}]/usr", 'flag_field'):
                raise Exception()
        except:
            if not skip_error: raise Exception("Flag field failed.")

    def flag_field_at_side(self, field_name: str, desired_operator: bool, side_index: int = 0, target_index: int = 0,
                           selected_tab: Union[int, str] = 0, skip_error: bool = False) -> None:
        """
        This function can flag and unflag checkboxes based on the field_name, it will flag/unflag the checkbox at the
        side of the respective field_name
        :param field_name: The text at the side of the checkbox you want to flag/unflag
        :param desired_operator: Boolean to say if you want to flag or unflag the checkbox
        :param side_index: Number of components at the side of the respective field_name, with positive numbers the code will go through components at right, if negative it will go through components at left
        :param target_index: Target index, determines how many occurrences precede the desired field
        :param selected_tab: Desired Tab, where this field can be found, the SAP default tab is 0
        :param skip_error: Skip this function if occur any error
        """
        try:
            self.window = active_window(self)
            self._field_name = field_name
            self._desired_operator = desired_operator
            self._target_index = target_index
            self._side_index = side_index
            if selected_tab != self._selected_tab_id and selected_tab != self._selected_tab_name:
                self.change_active_tab(selected_tab)
            if not scroll_through_fields(self, f"wnd[{self.window}]/usr", 'flag_field_at_side'):
                raise Exception()
        except:
            if not skip_error: raise Exception("Flag field at side failed.")

    def option_field(self, field_name: str, target_index: int = 0, selected_tab: Union[int, str] = 0,
                     skip_error: bool = False) -> None:
        """
        This function will select an option field
        :param field_name: The text with the option field you want to select
        :param target_index: Target index, determines how many occurrences precede the desired field
        :param selected_tab: Desired Tab, where this field can be found, the SAP default tab is 0
        :param skip_error: Skip this function if occur any error
        """
        try:
            self.window = active_window(self)
            self._field_name = field_name
            self._target_index = target_index
            if selected_tab != self._selected_tab_id and selected_tab != self._selected_tab_name:
                self.change_active_tab(selected_tab)
            if not scroll_through_fields(self, f"wnd[{self.window}]/usr", 'option_field'):
                raise Exception()
        except:
            if not skip_error: raise Exception("Option field failed.")

    def option_field_at_side(self, field_name: str, side_index: int = 0, target_index: int = 0,
                             selected_tab: Union[int, str] = 0, skip_error: bool = False) -> None:
        """
        This function will select an option field
        :param field_name: The text with the option field you want to select
        :param side_index: Number of components at the side of the respective field_name, with positive numbers the code will go through components at right, if negative it will go through components at left
        :param target_index: Target index, determines how many occurrences precede the desired field
        :param selected_tab: Desired Tab, where this field can be found, the SAP default tab is 0
        :param skip_error: Skip this function if occur any error
        """
        try:
            self.window = active_window(self)
            self._field_name = field_name
            self._target_index = target_index
            self._side_index = side_index
            if selected_tab != self._selected_tab_id and selected_tab != self._selected_tab_name:
                self.change_active_tab(selected_tab)
            if not scroll_through_fields(self, f"wnd[{self.window}]/usr", 'option_field_at_side'):
                raise Exception()
        except:
            if not skip_error: raise Exception("Option field failed.")

    def press_button(self, field_name: str, target_index: int = 0, selected_tab: Union[int, str] = 0,
                     skip_error: bool = False) -> None:
        """
        Press any button in the SAP screens, except in shells and tables components
        :param field_name: The button that you want to press, this text need to be inside the button or in the tooltip of the button
        :param target_index: Target index, determines how many occurrences precede the desired field
        :param selected_tab: Desired Tab, where this field can be found, the SAP default tab is 0
        :param skip_error: Skip this function if occur any error
        """
        try:
            self.window = active_window(self)
            self._field_name = field_name
            self._target_index = target_index
            if selected_tab != self._selected_tab_id and selected_tab != self._selected_tab_name:
                self.change_active_tab(selected_tab)
            if not scroll_through_fields(self, f"wnd[{self.window}]", 'press_button'):
                raise Exception()
        except:
            if not skip_error: raise Exception("Press button failed.")

    def multiple_selection_field(self, field_name: str, target_index: int = 0, selected_tab: Union[int, str] = 0,
                                 skip_error: bool = False) -> None:
        """
        This function will press the "Multiple Selection" button in the respective field
        :param field_name: The text that precedes the desired text field box
        :param target_index: Target index, determines how many occurrences precede the desired field
        :param selected_tab: Desired Tab, where this field can be found, the SAP default tab is 0
        :param skip_error: Skip this function if occur any error
        """
        try:
            self.window = active_window(self)
            self._field_name = field_name
            self._target_index = target_index
            if selected_tab != self._selected_tab_id and selected_tab != self._selected_tab_name:
                self.change_active_tab(selected_tab)
            if not scroll_through_fields(self, f"wnd[{self.window}]/usr", 'multiple_selection_field'):
                raise Exception()
        except:
            if not skip_error: raise Exception("Multiple selection field failed.")

    def find_text_field(self, field_name: str, selected_tab: Union[int, str] = 0) -> bool:
        """
        Verify if a text exists in the SAP screen
        :param field_name: The text that you want to search
        :param selected_tab: Desired Tab, where this field can be found, the SAP default tab is 0
        :return: A boolean, True if the text was found and False if it was not found
        """
        self.window = active_window(self)
        self._field_name = field_name
        if selected_tab != self._selected_tab_id and selected_tab != self._selected_tab_name:
            self.change_active_tab(selected_tab)
        return scroll_through_fields(self, f"wnd[{self.window}]/usr", 'find_text_field')

    def get_text_at_side(self, field_name, side_index: int, target_index: int = 0,
                         selected_tab: Union[int, str] = 0) -> str:
        """
        This function will return the text next to the text received as a parameter
        :param field_name: The text that you want to search
        :param side_index: Number of components at the side of the respective field_name, with positive numbers the code will go through components at right, if negative it will go through components at left
        :param target_index: Target index, determines how many occurrences precede the desired field
        :param selected_tab: Desired Tab, where this field can be found, the SAP default tab is 0
        :return: A string with the text at the side of the searched text
        """
        self.window = active_window(self)
        self._field_name = field_name
        self._target_index = target_index
        self._side_index = side_index
        if selected_tab != self._selected_tab_id and selected_tab != self._selected_tab_name:
            self.change_active_tab(selected_tab)
        if scroll_through_fields(self, f"wnd[{self.window}]", 'get_text_at_side'):
            return self._found_text

    def set_focus(self, field_name, side_index: int = 0, target_index: int = 0, selected_tab: Union[int, str] = 0):
        """
        This function will select/focus in the field with the text received as a parameter
        :param field_name: The text that you want to focus
        :param side_index: Number of components at the side of the respective field_name, with positive numbers the code will go through components at right, if negative it will go through components at left
        :param target_index: Target index, determines how many occurrences precede the desired field
        :param selected_tab: Desired Tab, where this field can be found, the SAP default tab is 0
        """
        self.window = active_window(self)
        self._field_name = field_name
        self._target_index = target_index
        self._side_index = side_index
        if selected_tab != self._selected_tab_id and selected_tab != self._selected_tab_name:
            self.change_active_tab(selected_tab)
        scroll_through_fields(self, f"wnd[{self.window}]", 'set_focus')

    def open_focused_field_modal(self):
        """
        This function will open the modal of a focused field
        """
        self.session.findById(f'wnd[{self.window}]').sendVKey(4)

    def multiple_selection_paste_data(self, data: list[str], delete_values: bool = False,
                                      skip_error: bool = False) -> None:
        """
        With the Multiple Selection window open, it's possible to execute this function to easily paste all the data
        from a list
        :param data: An array with the data that you want to insert in the multiple selection
        :param delete_values: Boolean to determine if you want to insert the list to delete it from the final result
        :param skip_error: Skip this function if occur any error
        """
        uid = str(uuid.uuid4())
        self.window = active_window(self)

        if delete_values:
            self.change_active_tab(2)

        try:
            with open(f'C:/Temp/{uid}.txt', 'w') as file:
                file.write('\n'.join(data))
            self.session.findById(f"wnd[{self.window}]/tbar[0]/btn[23]").press()
            self.session.findById(f"wnd[{self.window + 1}]/usr/ctxtDY_PATH").text = 'C:/Temp'
            self.session.findById(f"wnd[{self.window + 1}]/usr/ctxtDY_FILENAME").text = f"{uid}.txt"
            self.session.findById(f"wnd[{self.window + 1}]/tbar[0]/btn[0]").press()
            self.session.findById(f"wnd[{self.window}]/tbar[0]/btn[8]").press()
            if os.path.exists(f'C:/Temp/{uid}.txt'):
                os.remove(f'C:/Temp/{uid}.txt')
        except:
            if not skip_error: raise Exception("Multiple selection paste data failed.")

    def navigate_into_menu_header(self, *nested_path: str) -> None:
        """
        This function needs to receive several strings that have the texts that appear written in the header destination
        that you want to press, it must be written in the order that it appears in the SAP header
        :param nested_path: The nested path that you want to navigate into the header
        """
        id_path = 'wnd[0]/mbar'
        for active_path in nested_path:
            children = self.session.findById(id_path).children
            for i in range(children.count):
                Obj = children[i]
                if active_path in Obj.text:
                    menu_address = Obj.id.split("/")[-1]
                    id_path += f'/{menu_address}'
                    break
        self.session.findById(id_path).Select()

    def save_file(self, file_name: str, path: str, option: int = 0, type_of_file: str = 'txt',
                  skip_error: bool = False) -> None:
        """
        This function will easily navigate into SAP menu header to save the current transaction data, commonly used to
        extract data Labels
        :param file_name: The name of the file that you want to save
        :param path: The path that you want to save the file
        :param option: The txt option of save format 0=>Unconverted,1=>Text with Tabs,2=>Rich text format
        :param type_of_file: The extension that you want for the file
        :param skip_error: Skip this function if occur any error
        """
        try:
            if 'xls' in type_of_file:
                self.session.findById("wnd[0]/mbar/menu[0]/menu[1]/menu[1]").Select()
                self.session.findById("wnd[1]/tbar[0]/btn[0]").press()
            else:
                self.session.findById("wnd[0]/mbar/menu[0]/menu[1]/menu[2]").Select()
                self.session.findById(
                    f"wnd[1]/usr/subSUBSCREEN_STEPLOOP:SAPLSPO5:0150/sub:SAPLSPO5:0150/radSPOPLI-SELFLAG[{option},0]").Select()
                self.session.findById("wnd[1]/tbar[0]/btn[0]").press()

            self.session.findById("wnd[1]/usr/ctxtDY_PATH").Text = path
            self.session.findById("wnd[1]/usr/ctxtDY_FILENAME").Text = f'{file_name}.{type_of_file}'
            self.session.findById("wnd[1]/tbar[0]/btn[11]").press()
        except:
            if not skip_error: raise Exception("Save file failed.")

    def get_label(self) -> Label:
        """
        Get the SAP Label object from the current SAP Label Window
        :return: A SAP Label object, that can be used to extract data from Label components in SAP
        """
        try:
            self.window = active_window(self)
            label = Label(self.session, self.window)
            return label
        except:
            raise Exception("Get label failed.")

    def get_table(self, target_index: int = 0) -> Table:
        """
        Get the SAP Table object from the current SAP Table Window
        :param target_index: Target index, determines how many occurrences precede the desired component
        :return: A SAP Table object, that can be used to extract data from Table components in SAP
        """
        try:
            self.window = active_window(self)
            self._component_target_index = target_index
            table_obj = scroll_through_table(self, f'wnd[{self.window}]/usr')
            if not table_obj:
                raise Exception()
            table = Table(table_obj, self.session, target_index)
            return table
        except:
            raise Exception("Get table failed.")

    def get_tree(self) -> Tree:
        """
        Get the SAP Tree object from the current SAP Tree Window
        :return: A SAP Tree object, that can be used to extract data from Tree tables in SAP
        """
        try:
            self.window = active_window(self)
            tree_obj = scroll_through_tree(self, f'wnd[{self.window}]')

            if not tree_obj:
                raise Exception("Tree Object not found")

            tree = Tree(tree_obj)
            return tree
        except:
            raise Exception("Get Tree failed.")

    def get_grid(self, target_index: int = 0) -> Grid:
        """
        Get the SAP Grid object from the current SAP Grid Window
        :param target_index: Target index, determines how many occurrences precede the desired component
        :return: A SAP Grid object, that can be used to extract data from Grid tables in SAP
        """
        try:
            self.window = active_window(self)
            self._component_target_index = target_index
            grid_obj = scroll_through_grid(self, f'wnd[{self.window}]')

            if not grid_obj:
                raise Exception()

            grid = Grid(grid_obj, self.session)
            return grid
        except:
            raise Exception("Get grid failed.")

    def get_node(self, target_index: int = 0) -> Node:
        """
        Get the SAP Node object from the current SAP Node Window
        :param target_index: Target index, determines how many occurrences precede the desired component
        :return: A SAP Node object, that can be used to extract data from Node components in SAP
        """
        try:
            self.window = active_window(self)
            self._component_target_index = target_index
            node_obj = scroll_through_node(self, f'wnd[{self.window}]')

            if not node_obj:
                raise Exception()

            node = Node(node_obj)
            return node

        except:
            raise Exception("Get node failed.")

    def get_footer_message(self) -> str:
        """
        Get the message text that is in the SAP Footer
        :return: A String with the footer message
        """
        try:
            return self.session.findById("wnd[0]/sbar").text
        except:
            raise Exception("Get footer message failed.")
