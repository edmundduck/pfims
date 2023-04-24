import anvil.secrets
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
from io import BytesIO
import pandas as pd

# This is a server module. It runs on the Anvil server,
# rather than in the user's browser.
#
# To allow anvil.server.call() to call functions here, we mark
# them with @anvil.server.callable.
# Here is an example - you can replace it with your own:
#
# @anvil.server.callable
# def say_hello(name):
#   print("Hello, " + name + "!")
#   return 42
#

@anvil.server.callable
def import_file(file):
    ef = pd.ExcelFile(BytesIO(file.get_bytes()))
    print(ef.)
    xls = pd.read_excel(ef)
    # xls = pd.read_excel(BytesIO(file.get_bytes()), sheet_name=None)
    print(xls)
    return list(xls.keys())

def get_xls_tabs(f):
    return list(f.keys())
