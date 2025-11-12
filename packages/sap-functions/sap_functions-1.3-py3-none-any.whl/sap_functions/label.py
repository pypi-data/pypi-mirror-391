from .session import SAPGuiSession
import warnings
from typing import Dict, List


# https://help.sap.com/docs/sap_gui_for_windows/b47d018c3b9b45e897faf66a6c0885a8/2e44c4f890524686977e9729565f7824.html?locale=en-US
class Label:
    def __init__(self, session: SAPGuiSession, window: int = 0):
        self.session = session
        self.window = window

    def get_all_screen_labels(self) -> list:
        """
        This function will return each label row in the SAP Screen
        :return: A list with lists
        """
        self.session.findById(f"wnd[{self.window}]/usr").verticalScrollbar.position = 0
        content = []
        columns = []
        children = self.session.findById(f"wnd[0]/usr").children
        for field in children:
            if field.type == 'GuiLabel':
                if field.charLeft not in columns:
                    columns.append(field.charLeft)

        while True:
            for i in range(2, 100):
                active_row = []
                for c in columns:
                    try:
                        cell = self.session.findById(f"wnd[{self.window}]/usr/lbl[{c},{i}]").text.strip()
                        active_row.append(cell)
                    except:
                        pass

                if not all(value is None for value in active_row):
                    content.append(active_row)

            max_scroll = self.session.findById(f"wnd[{self.window}]/usr").verticalScrollbar.maximum
            pos_scroll = self.session.findById(f"wnd[{self.window}]/usr").verticalScrollbar.position

            if max_scroll == pos_scroll:
                break
            else:
                self.session.findById(f"wnd[{self.window}]").sendVKey(82)
        return content

    def get_label_content(self) -> Dict[str, List]:
        """
        Deprecated: use `Label.get_content` instead.

        Store all the content from a SAP Label, the data will be stored and returned in a dictionary with
        'header' and 'content' items
        :return: A dictionary with 'header' and 'content' items
        """
        warnings.warn("Deprecated in 1.1 "
                      "Label.get_label_content will be removed in 1.5 "
                      "Use Label.get_content instead.", DeprecationWarning, stacklevel=2)
        self.session.findById(f"wnd[{self.window}]/usr").verticalScrollbar.position = 0
        finished_collecting = False
        header = []
        content = []
        columns = []

        children = self.session.findById(f"wnd[{self.window}]/usr").children
        for field in children:
            if field.type == 'GuiLabel':
                if field.charLeft not in columns:
                    columns.append(field.charLeft)

        for header_row_index in range(1, 4):
            for c in columns:
                try:
                    cell = self.session.findById(f"wnd[{self.window}]/usr/lbl[{c},{header_row_index}]").text.strip()
                    header.append(cell)
                except:
                    pass
            if len(header) > 0:
                break

        while True:
            if finished_collecting:
                break
            for i in range(2, 100):
                active_row = []
                for c in columns:
                    try:
                        cell = self.session.findById(f"wnd[{self.window}]/usr/lbl[{c},{i}]").text.strip()
                        active_row.append(cell)
                    except:
                        pass

                if not all(value is None for value in active_row):
                    content.append(active_row)

            max_scroll = self.session.findById(f"wnd[{self.window}]/usr").verticalScrollbar.maximum
            pos_scroll = self.session.findById(f"wnd[{self.window}]/usr").verticalScrollbar.position

            if max_scroll == pos_scroll:
                break
            else:
                self.session.findById(f"wnd[{self.window}]").sendVKey(82)

        return {'header': header, 'content': content}

    def get_content(self) -> Dict[str, List]:
        """
        Store all the content from a SAP Label, the data will be stored and returned in a dictionary with
        'header' and 'content' items
        :return: A dictionary with 'header' and 'content' items
        """
        self.session.findById(f"wnd[{self.window}]/usr").verticalScrollbar.Position = 0
        finished_collecting = False
        header = []
        content = []
        columns = []

        children = self.session.findById(f"wnd[{self.window}]/usr").children
        for field in children:
            if field.type == 'GuiLabel':
                if field.charLeft not in columns:
                    columns.append(field.charLeft)

        for header_row_index in range(1, 4):
            for c in columns:
                try:
                    cell = self.session.findById(f"wnd[{self.window}]/usr/lbl[{c},{header_row_index}]").text.strip()
                    header.append(cell)
                except:
                    pass
            if len(header) > 0:
                break

        while True:
            if finished_collecting:
                break
            for i in range(2, 100):
                active_row = []
                for c in columns:
                    try:
                        cell = self.session.findById(f"wnd[{self.window}]/usr/lbl[{c},{i}]").text.strip()
                        active_row.append(cell)
                    except:
                        pass

                if not all(value is None for value in active_row):
                    content.append(active_row)

            max_scroll = self.session.findById(f"wnd[{self.window}]/usr").verticalScrollbar.maximum
            pos_scroll = self.session.findById(f"wnd[{self.window}]/usr").verticalScrollbar.position

            if max_scroll == pos_scroll:
                break
            else:
                self.session.findById(f"wnd[{self.window}]").sendVKey(82)

        return {'header': header, 'content': content}
