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

@anvil.server.callable
def preview_file(file, fid):
    ef = pd.ExcelFile(BytesIO(file.get_bytes()))
    # frules = anvil.server.call('select_filter_labels_rules', fid)
    # xls = pd.read_excel(ef, sheet_name=None, usecols="B", index_col=0)
    return list(ef.sheet_names)

def get_xls_tabs(f):
    return list(f.keys())
