import anvil.files
from anvil.files import data_files
import anvil.secrets
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server

# This is a server module. It runs on the Anvil server,
# rather than in the user's browser.

def upper_dict_keys(rows, key_list=None):
    DL = {}
    for k in rows[0].keys():
        if k.upper() in key_list or not key_list:
            DL[k.upper()] = [row[k] for row in rows]
        else:
            DL[k] = [row[k] for row in rows]
    result = [dict(zip(DL, col)) for col in zip(*DL.values())]
    return result
