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
    # df = pd.read_excel(ef, sheet_name=tablist, usecols=rules)
    df = pd.read_excel(ef, sheet_name=tablist)

    new_df = None
    for t in tablist:
        for i in rules:
            date = convertCharToLoc(i['date'])
            lbl = convertCharToLoc(i['lbl'])
            amt = convertCharToLoc(i['amt'])
            remarks = convertCharToLoc(i['remarks'])
            # iloc left one is row, right one is column
            test1 = df[t].iloc[:,[date, lbl, amt, remarks]]
            test1.rename(columns={test1.columns[0]: "C0", test1.columns[1]: "C1", test1.columns[2]: "C2", test1.columns[3]: "C3"}, inplace=True)
            new_df = pd.concat([test1], ignore_index=True) if new_df is None else pd.concat([new_df, test1], ignore_index=True)
    # TODO - Error "TypeError: DataFrame.dropna() got an unexpected keyword argument 'ignore_index'", due to version issue?
    # return new_df.dropna(subset=['C2'], ignore_index=True)
    return new_df.dropna(subset=['C2'])
