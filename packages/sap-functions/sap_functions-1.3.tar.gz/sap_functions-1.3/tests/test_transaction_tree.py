import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.sap_functions import SAP
import pytest
from dotenv import load_dotenv
import os

load_dotenv()

sap = SAP()
tree = None
   
def test_transaction():
   sap.select_transaction(os.getenv("transaction_3"))
   exec(os.getenv("transaction_3_fill_fields"))
   sap.run_actual_transaction()

def test_get_tree():
   global tree
   tree = sap.get_tree()

def test_tree_get_content():
   content = tree.get_content()
   assert type(content.get("header")).__name__ == "list"
   assert type(content.get("content")).__name__ == "list"

def test_tree_columns():
   columns = tree.get_columns()
   assert type(columns).__name__ == "list"
