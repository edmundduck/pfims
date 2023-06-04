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

# Internal function to convert column in character ID to number for Pandas read_excel
def convertCharToLoc(char):
    if 'a' <= char.lower() <= 'z':
            return ord(char.lower()) - 97
    return None

@anvil.server.callable
def preview_file(file):
    ef = pd.ExcelFile(BytesIO(file.get_bytes()))
    return list(ef.sheet_names)

@anvil.server.callable
def import_file(file, tablist, rules):
    ef = pd.ExcelFile(BytesIO(file.get_bytes()))
    # xls = pd.read_excel(ef, sheet_name=tablist, usecols=rules)
    xls = pd.read_excel(ef, sheet_name=tablist)

    new_xls = None
    for i in rules:
        date = convertCharToLoc(i["date"])
        # iloc left one is row, right one is column
        test1 = ef.iloc[:,[convertCharToLoc(filter["date"]), convertCharToLoc(filter["acct"]), convertCharToLoc(i), convertCharToLoc(filter["remarks"])]]
        test1.rename(columns={test1.columns[0]: "Date", test1.columns[1]: "Lbl", test1.columns[2]: "Amt", test1.columns[3]: "Remarks"}, inplace=True)
        new_xls = pd.concat([test1], ignore_index=True) if new_xls is None else pd.concat([new_xls, test1], ignore_index=True)
    print(new_xls)
    print(new_xls.dropna(subset=['Amt'], ignore_index=True))
