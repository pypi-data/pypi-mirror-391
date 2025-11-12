import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.sap_functions import SAP
import pytest
from dotenv import load_dotenv
import os

load_dotenv()
sap = SAP()

def test_transaction():
   sap.select_transaction(os.getenv("transaction_2"))

def test_insert_data_transaction():
   sap.write_text_field(os.getenv("transaction_2_field_1_name"), os.getenv("transaction_2_field_1_value"))
   sap.write_text_field(os.getenv("transaction_2_field_2_name"), os.getenv("transaction_2_field_2_value"))

def test_run_transaction():
   sap.run_actual_transaction()

table = None
def test_get_table():
   global table
   table = sap.get_table()

def test_table_count_visible_rows():
   rows = table.count_visible_rows()
   assert type(rows).__name__ == "int"

def test_table_cell_value():
   cell_value = table.get_cell_value(0, 1)
   assert type(cell_value).__name__ == "str"
   
def test_table_select_actions():
   table.select_entire_row(0)
   table.unselect_entire_row(0)
   table.click_cell(0, 0, True)   
   exec(os.getenv("transaction_2_after_cell_click"))

def test_table_get_content():
   content = table.get_content()
   assert type(content.get("header")).__name__ == "list"
   assert type(content.get("content")).__name__ == "list"

def test_table_internal_methods():
   table_obj = table._return_table()
   assert type(table_obj).__name__ == "CDispatch"
