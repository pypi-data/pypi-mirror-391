from typing import Union
from .session import GuiComponent, SAPGridView
import win32com.client
import time
import re


def get_sap_connection() -> win32com.client.CDispatch:
    try:
        sapguiauto = win32com.client.GetObject('SAPGUI')
        application = sapguiauto.GetScriptingEngine
        return application.Children(0)
    except:
        raise Exception(
            "SAP is not open!\nSAP must be open to run this script! Please, open it and try to run again.")


def count_and_create_sap_screens(connection: win32com.client.CDispatch, window: int):
    while len(connection.sessions) < window + 1:
        connection.Children(0).createSession()
        time.sleep(3)


def active_window(sap) -> int:
    regex = re.compile('[0-9]')
    matches = regex.findall(sap.session.activeWindow.name)
    for match in matches:
        return int(match)


def scroll_through_tabs_by_id(sap, area: GuiComponent, extension: str,
                              selected_tab: int) -> GuiComponent:
    children = area.children
    for child in children:
        if child.type == "GuiTabStrip":
            extension = extension + "/tabs" + child.name
            return scroll_through_tabs_by_id(sap, sap.session.findById(extension), extension, selected_tab)
        if child.type == "GuiTab":
            extension = extension + "/tabp" + str(children[selected_tab].name)
            sap._selected_tab_id = selected_tab
            sap._selected_tab_name = children[selected_tab].text
            return scroll_through_tabs_by_id(sap, sap.session.findById(extension), extension, selected_tab)
        if child.type == "GuiSimpleContainer":
            extension = extension + "/sub" + child.name
            return scroll_through_tabs_by_id(sap, sap.session.findById(extension), extension, selected_tab)
        if child.type == "GuiScrollContainer" and 'tabp' in extension:
            extension = extension + "/ssub" + child.name
            area = sap.session.findById(extension)
            return area
    return area


def scroll_through_tabs_by_name(sap, area: GuiComponent, extension: str,
                                tab_name: str) -> GuiComponent:
    children = area.children
    for i, child in enumerate(children):
        if child.type == "GuiTabStrip":
            extension = extension + "/tabs" + child.name
            return scroll_through_tabs_by_name(sap, sap.session.findById(extension), extension, tab_name)
        if child.type == "GuiTab":
            temp_extension = extension + "/tabp" + str(child.name)
            if str(sap.session.findById(temp_extension).text).strip() == tab_name:
                extension = extension + "/tabp" + str(child.name)
                sap._selected_tab_id = i
                sap._selected_tab_name = child.text
                return scroll_through_tabs_by_name(sap, sap.session.findById(extension), extension, tab_name)
        if child.type == "GuiSimpleContainer":
            extension = extension + "/sub" + child.name
            return scroll_through_tabs_by_name(sap, sap.session.findById(extension), extension, tab_name)
        if child.type == "GuiScrollContainer" and 'tabp' in extension:
            extension = extension + "/ssub" + child.name
            area = sap.session.findById(extension)
            return area
    return area


def scroll_through_grid(sap, extension: str) -> Union[bool, SAPGridView]:
    if sap.session.findById(extension).Type == 'GuiShell':
        try:
            var = sap.session.findById(extension).RowCount
            if sap._component_target_index == 0:
                return sap.session.findById(extension)
            else:
                sap._component_target_index -= 1
        except:
            pass

        try:
            for i in range(100):
                button_id = sap.session.findById(extension).GetButtonId(i)
                if '&' in button_id:
                    return sap.session.findById(extension)
        except:
            pass

    children = sap.session.findById(extension).Children
    result = False
    for i in range(len(children)):
        if result:
            break
        if children[i].Type == 'GuiCustomControl':
            result = scroll_through_grid(sap, extension + '/cntl' + children[i].name)
        if children[i].Type == 'GuiSimpleContainer':
            result = scroll_through_grid(sap, extension + '/sub' + children[i].name)
        if children[i].Type == 'GuiScrollContainer':
            result = scroll_through_grid(sap, extension + '/ssub' + children[i].name)
        if children[i].Type == 'GuiTableControl':
            result = scroll_through_grid(sap, extension + '/tbl' + children[i].name)
        if children[i].Type == 'GuiTab':
            result = scroll_through_grid(sap, extension + '/tabp' + children[i].name)
        if children[i].Type == 'GuiTabStrip':
            result = scroll_through_grid(sap, extension + '/tabs' + children[i].name)
        if children[
            i].Type in ("GuiShell GuiSplitterShell GuiContainerShell GuiDockShell GuiMenuBar GuiToolbar "
                        "GuiUserArea GuiTitlebar"):
            result = scroll_through_grid(sap, extension + '/' + children[i].name)
    return result


def scroll_through_tree(sap, extension: str) -> Union[bool, win32com.client.CDispatch]:
    if sap.session.findById(extension).Type == 'GuiShell':
        try:
            var = sap.session.findById(extension).GetAllNodeKeys()
            return sap.session.findById(extension)
        except:
            pass
    children = sap.session.findById(extension).Children
    result = False
    for i in range(len(children)):
        if result:
            break
        if children[i].Type == 'GuiCustomControl':
            result = scroll_through_tree(sap, extension + '/cntl' + children[i].name)
        if children[i].Type == 'GuiSimpleContainer':
            result = scroll_through_tree(sap, extension + '/sub' + children[i].name)
        if children[i].Type == 'GuiScrollContainer':
            result = scroll_through_tree(sap, extension + '/ssub' + children[i].name)
        if children[i].Type == 'GuiTableControl':
            result = scroll_through_tree(sap, extension + '/tbl' + children[i].name)
        if children[i].Type == 'GuiTab':
            result = scroll_through_tree(sap, extension + '/tabp' + children[i].name)
        if children[i].Type == 'GuiTabStrip':
            result = scroll_through_tree(sap, extension + '/tabs' + children[i].name)
        if children[
            i].Type in ("GuiShell GuiSplitterShell GuiContainerShell GuiDockShell GuiMenuBar GuiToolbar "
                        "GuiUserArea GuiTitlebar"):
            result = scroll_through_tree(sap, extension + '/' + children[i].name)
    return result


def scroll_through_node(sap, extension: str) -> Union[bool, win32com.client.CDispatch]:
    if sap.session.findById(extension).Type == 'GuiShell':
        try:
            var = sap.session.findById(extension).GetHierarchyTitle()
            if sap._component_target_index == 0:
                return sap.session.findById(extension)
            else:
                sap._component_target_index -= 1
        except:
            pass
    children = sap.session.findById(extension).Children
    result = False
    for i in range(len(children)):
        if result:
            break
        if children[i].Type == 'GuiCustomControl':
            result = scroll_through_node(sap, extension + '/cntl' + children[i].name)
        if children[i].Type == 'GuiSimpleContainer':
            result = scroll_through_node(sap, extension + '/sub' + children[i].name)
        if children[i].Type == 'GuiScrollContainer':
            result = scroll_through_node(sap, extension + '/ssub' + children[i].name)
        if children[i].Type == 'GuiTableControl':
            result = scroll_through_node(sap, extension + '/tbl' + children[i].name)
        if children[i].Type == 'GuiTab':
            result = scroll_through_node(sap, extension + '/tabp' + children[i].name)
        if children[i].Type == 'GuiTabStrip':
            result = scroll_through_node(sap, extension + '/tabs' + children[i].name)
        if children[
            i].Type in ("GuiShell GuiSplitterShell GuiContainerShell GuiDockShell GuiMenuBar GuiToolbar "
                        "GuiUserArea GuiTitlebar"):
            result = scroll_through_node(sap, extension + '/' + children[i].name)
    return result


def scroll_through_table(sap, extension: str) -> Union[bool, win32com.client.CDispatch]:
    if 'tbl' in extension:
        try:
            if sap._component_target_index == 0:
                return sap.session.findById(extension)
            else:
                sap._component_target_index -= 1
        except Exception as e:
            print(e)
    children = sap.session.findById(extension).Children
    result = False
    for i in range(len(children)):
        if result:
            break
        if children[i].Type == 'GuiCustomControl':
            result = scroll_through_table(sap, extension + '/cntl' + children[i].name)
        if children[i].Type == 'GuiSimpleContainer':
            result = scroll_through_table(sap, extension + '/sub' + children[i].name)
        if children[i].Type == 'GuiScrollContainer':
            result = scroll_through_table(sap, extension + '/ssub' + children[i].name)
        if children[i].Type == 'GuiTableControl':
            result = scroll_through_table(sap, extension + '/tbl' + children[i].name)
        if children[i].Type == 'GuiTab':
            result = scroll_through_table(sap, extension + '/tabp' + children[i].name)
        if children[i].Type == 'GuiTabStrip':
            result = scroll_through_table(sap, extension + '/tabs' + children[i].name)
        if children[
            i].Type in ("GuiShell GuiSplitterShell GuiContainerShell GuiDockShell GuiMenuBar GuiToolbar "
                        "GuiUserArea GuiTitlebar"):
            result = scroll_through_table(sap, extension + '/' + children[i].name)
    return result


def scroll_through_fields(sap, extension: str, objective: str) -> bool:
    selected_tab = sap._selected_tab_id
    children = sap.session.findById(extension).Children
    result = False
    for i in range(len(children)):
        if not result:
            result = generic_conditionals(sap, i, children, objective)

        if result:
            break

        if not result and children[i].Type == "GuiTabStrip" and 'ssub' not in extension:
            result = scroll_through_fields(sap, extension + "/tabs" + children[i].name, objective)

        if not result and children[i].Type == "GuiTab" and 'tabp' not in extension:
            if objective != 'select_tab_by_name':
                result = scroll_through_fields(sap, extension + "/tabp" + str(children[selected_tab].name),
                                               objective)
            else:
                result = scroll_through_fields(sap, extension + "/tabp" + str(children[i].name), objective)

        if not result and children[i].Type == "GuiSimpleContainer":
            result = scroll_through_fields(sap, extension + "/sub" + children[i].name, objective)

        if not result and children[i].Type == "GuiScrollContainer":
            result = scroll_through_fields(sap, extension + "/ssub" + children[i].name, objective)

        if not result and children[i].Type == "GuiCustomControl":
            result = scroll_through_fields(sap, extension + "/cntl" + children[i].name, objective)

        if not result and children[i].Type in (
                "GuiShell GuiSplitterShell GuiContainerShell GuiDockShell GuiMenuBar GuiToolbar GuiUserArea GuiTitlebar"):
            result = scroll_through_fields(sap, extension + "/" + children[i].name, objective)

    return result


def generic_conditionals(sap, index: int, children: win32com.client.CDispatch, objective: str) -> bool:
    if objective == 'select_tab_by_name':
        if str(children(index).Text).strip() == sap._target_tab:
            try:
                sap._selected_tab_id = index
                sap._selected_tab_name = sap._field_name
                children(index).Select()
                return True
            except:
                return False

    if objective == 'write_text_field':
        if children(index).Text == sap._field_name:
            if sap._target_index == 0:
                try:
                    cont_ind = index + 1
                    while children(cont_ind).type not in ['GuiCTextField', 'GuiTextField']:
                        cont_ind += 1
                    children(cont_ind).Text = sap._desired_text
                    return True
                except:
                    return False
            else:
                sap._target_index -= 1

    if objective == 'write_text_field_until':
        if children(index).Text == sap._field_name:
            if sap._target_index == 0:
                try:
                    cont_ind = index + 3
                    while children(cont_ind).type not in ['GuiCTextField', 'GuiTextField']:
                        cont_ind += 1
                    children(cont_ind).Text = sap._desired_text
                    return True
                except:
                    return False
            else:
                sap._target_index -= 1

    if objective == 'find_text_field':
        child = children(index)
        if (sap._field_name in child.Text or
                ('HTMLControl' in child.Text and sap._field_name in child.BrowserHandle.document.all(
                    0).innerText)):
            return True
        return False

    if objective == 'multiple_selection_field':
        if children(index).Text == sap._field_name:
            if sap._target_index == 0:
                try:
                    field = children(index).name
                    initial_position = field.find("%") + 1
                    final_position = field.find("-", initial_position)
                    field = field[initial_position:final_position] + "-VALU_PUSH"
                    for j in range(index, len(children)):
                        Obj = children[j]
                        if field in Obj.name or 'V_BTN_RANGE' in Obj.name:
                            Obj.press()
                            return True
                except:
                    return False
                return False
            else:
                sap._target_index -= 1

    if objective == 'flag_field':
        if children(index).Text == sap._field_name:
            if sap._target_index == 0:
                try:
                    children(index).Selected = sap._desired_operator
                    return True
                except:
                    return False
            else:
                sap._target_index -= 1

    if objective == 'flag_field_at_side':
        if children(index).Text == sap._field_name:
            if sap._target_index == 0:
                try:
                    children(index + sap._side_index).Selected = sap._desired_operator
                    return True
                except:
                    return False
            else:
                sap._target_index -= 1

    if objective == 'option_field':
        if children(index).Text == sap._field_name:
            if sap._target_index == 0:
                try:
                    children(index).Select()
                    return True
                except:
                    return False
            else:
                sap._target_index -= 1

    if objective == 'option_field_at_side':
        if children(index).Text == sap._field_name:
            if sap._target_index == 0:
                try:
                    children(index + sap._side_index).Select()
                    return True
                except:
                    return False
            else:
                sap._target_index -= 1

    if objective == 'press_button':
        try:
            if sap._field_name in children(index).Text or sap._field_name in children(index).Tooltip:
                children(index).press()
                return True
            if sap.session.info.transaction == 'CJ20N' or sap.session.info.transaction == 'MD04':
                try:
                    for i in range(101):
                        if children(index).GetButtonTooltip(i) != '':
                            id_button = children(index).GetButtonId(i)
                            tooltip_button = children(index).GetButtonTooltip(i)
                            if sap._field_name in tooltip_button:
                                children(index).pressButton(id_button)
                                return True
                except:
                    return False
        except:
            return False
        return False

    if objective == 'choose_text_combo':
        if children(index).Text == sap._field_name:
            if sap._target_index == 0:
                try:
                    entries = children(index + 1).Entries
                    for cont in range(len(entries)):
                        entry = entries.Item(cont)
                        if sap._desired_text == str(entry.Value):
                            children(index + 1).key = entry.key
                            return True
                except:
                    return False
                return False
            else:
                sap._target_index -= 1

    if objective == 'set_focus':
        if children(index).Text == sap._field_name:
            if sap._target_index == 0:
                try:
                    children(index + sap._side_index).setFocus()
                    return True
                except:
                    return False
            else:
                sap._target_index -= 1

    if objective == 'get_text_at_side':
        if children(index).Text == sap._field_name:
            if sap._target_index == 0:
                try:
                    sap._found_text = children(index + sap._side_index).Text
                    return True
                except:
                    return False
            else:
                sap._target_index -= 1
    return False
