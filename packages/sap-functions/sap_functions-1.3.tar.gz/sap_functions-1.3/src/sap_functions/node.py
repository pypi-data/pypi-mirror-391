import win32com.client
import warnings


# https://help.sap.com/docs/sap_gui_for_windows/b47d018c3b9b45e897faf66a6c0885a8/8f08be87b0194d9882d0382eae798617.html?locale=en-US
class Node:
    def __init__(self, node_obj: win32com.client.CDispatch):
        self.node_obj = node_obj

    def select_node(self, node_text: str, target_index: int = 0, skip_error: bool = False):
        """
        Select a specific Node based on the text inside of it
        :param node_text: The text in the desired Node
        :param target_index: Target index, determines how many occurrences precede the desired field
        :param skip_error: Skip this function if occur any error
        """
        parent = self.node_obj.GetAllNodeKeys()
        for item in parent:
            text = self.node_obj.GetNodeTextByKey(item)
            if node_text in text:
                if target_index == 0:
                    self.node_obj.SelectNode(item)
                    return
                else:
                    target_index -= 1
        if not skip_error:
            raise Exception(f"Node with text {node_text} was not found!")

    def click_selected_node(self):
        """
        Double-click the Node selected previously
        """
        node_id = self.node_obj.SelectedNode
        self.node_obj.doubleClickNode(node_id)

    def expand_selected_node(self):
        """
        Expand the Node selected previously
        """
        node_id = self.node_obj.SelectedNode
        self.node_obj.expandNode(node_id)

    def get_node_content(self) -> list:
        """
        Deprecated: use `Node.get_content` instead.

        Get all Nodes names in a list format
        :return: A list of string with every Node text
        """
        warnings.warn("Deprecated in 1.1 "
                      "Node.get_node_content will be removed in 1.5 "
                      "Use Node.get_content instead.", DeprecationWarning, stacklevel=2)
        results = []
        parent = self.node_obj.GetAllNodeKeys()
        for item in parent:
            text = self.node_obj.GetNodeTextByKey(item)
            results.append(text)

        return results

    def get_content(self) -> list:
        """
        Get all Nodes names in a list format
        :return: A list of string with every Node text
        """

        results = []
        parent = self.node_obj.GetAllNodeKeys()
        for item in parent:
            text = self.node_obj.GetNodeTextByKey(item)
            results.append(text)

        return results
