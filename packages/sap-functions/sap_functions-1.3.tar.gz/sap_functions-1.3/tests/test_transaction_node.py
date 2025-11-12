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
   sap.select_transaction(os.getenv("transaction_4"))

def test_select_project():
   sap.press_button(os.getenv("transaction_4_open_pop_up"))
   exec(os.getenv("transaction_4_pep_element"))
   sap.run_actual_transaction()


node = None
def test_get_node():
   global node
   node = sap.get_node()
   
def test_expand_node():
   node.expand_selected_node()

def test_select_node():
   node.select_node(os.getenv("transaction_4_selected_node"))

def test_click_selected_node():
   node.click_selected_node()

def test_node_get_content():
   content = node.get_content()
   assert type(content).__name__ == "list"
