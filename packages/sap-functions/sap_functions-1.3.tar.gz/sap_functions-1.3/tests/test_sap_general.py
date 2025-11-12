import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.sap_functions import SAP
import pytest
import os
from dotenv import load_dotenv

load_dotenv()

def test_sap_start():
   SAP()
   SAP(1)

sap = SAP()
def test_transaction():
   with pytest.raises(Exception):
      sap.select_transaction(os.getenv("not_existant_transaction"))

def test_sap_footer_message():
   assert sap.get_footer_message() == os.getenv("not_existant_transaction_footer_message")

def test_selecte_main_screen():
   sap.select_main_screen()