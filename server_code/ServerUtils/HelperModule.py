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
    """
    Change the key(s) in a dict to be upper case.

    If key_list is None, then all keys in a dict will be changed to upper case, otherwise only change those found in key_list.

    Parameters:
        key_list (list): List of key requiring to be upper case.

    Returns:
        result (list of dict): List of dict containing keys in upper case.
    """
    DL = {}
    for k in rows[0].keys():
        if k.upper() in key_list or not key_list:
            DL[k.upper()] = [row[k] for row in rows]
        else:
            DL[k] = [row[k] for row in rows]
    result = [dict(zip(DL, col)) for col in zip(*DL.values())]
    return result
