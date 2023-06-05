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
    combined_df = None
    for x in tablist:
        combined_df = combined_df + xls[x] if combined_df is not None else xls[x]

    new_xls = None
    for i in rules:
        date = convertCharToLoc(i["date"])
        lbl = convertCharToLoc(i['lbl'])
        amt = convertCharToLoc(i['amt'])
        remarks = convertCharToLoc(i['remarks'])
        # iloc left one is row, right one is column
        test1 = combined_df.iloc[:,[date, lbl, amt, remarks]]
        test1.rename(columns={test1.columns[0]: "C0", test1.columns[1]: "C1", test1.columns[2]: "C2", test1.columns[3]: "C3"}, inplace=True)
        new_xls = pd.concat([test1], ignore_index=True) if new_xls is None else pd.concat([new_xls, test1], ignore_index=True)
    print(new_xls.dropna(subset=['C2'], ignore_index=True))
