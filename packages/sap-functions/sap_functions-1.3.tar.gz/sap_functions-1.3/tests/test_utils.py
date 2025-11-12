import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.sap_functions import SAP
import pytest
from dotenv import load_dotenv
from src.sap_functions.utils import *
import os

load_dotenv()

def test_sap_session_related():
   con = get_sap_connection()
   count_and_create_sap_screens(con, 4)
   sap = SAP(4)
   current_window = active_window(sap)
   assert current_window == 0
