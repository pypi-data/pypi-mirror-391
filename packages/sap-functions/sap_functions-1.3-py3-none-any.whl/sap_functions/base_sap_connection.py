from .utils import *
from .session import SAPGuiSession


class BaseSapConnection:
    def __init__(self, window: int = 0):

        connection = get_sap_connection()
        count_and_create_sap_screens(connection, window)
        if connection.Children(0).info.user == '':
            raise Exception(
                "SAP user is logged out!\nYou need to log in to SAP to run this script! Please log in and try again.")

        if connection.Children(0).info.systemName == 'EQ0':
            print("You're with SAP Quality Assurance open, (SAP QA)\nMany things may not happen as desired!")
        self.session: SAPGuiSession = connection.Children(window)
        self.window = active_window(self)
