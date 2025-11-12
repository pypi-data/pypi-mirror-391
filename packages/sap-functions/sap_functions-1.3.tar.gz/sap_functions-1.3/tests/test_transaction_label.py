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
   sap.select_transaction(os.getenv("transaction_5"))

def test_insert_data_transaction():
   sap.write_text_field(os.getenv("transaction_5_field_5_name"), os.getenv("transaction_5_field_5_value"))

def test_run_transaction():
   sap.run_actual_transaction()

def test_get_label():
   grid = sap.get_grid()
   exec(os.getenv("transaction_5_before_label"))
   label = sap.get_label()
   label.get_all_screen_labels()

def test_get_content():
   label = sap.get_label()
   label.get_content()
