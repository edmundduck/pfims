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
col_name = ['trandate', 'account_id', 'amount', 'remarks', 'stmt_dtl', 'labels']

# Internal function to convert column in character ID to number for Pandas read_excel
def convertCharToLoc(char):
    return ord(char.lower()) - 97 if 'a' <= char.lower() <= 'z' else None

# Internal function to get the list of included column names in mapping matrix
def divMappingColumnNameLists(matrix):
    nanList, nonNanList = [], []
    for c in col_name: nanList.append(c) if matrix[c] in (None, '') else nonNanList.append(c)
    return nonNanList, nanList

@anvil.server.callable
def preview_file(file):
    ef = pd.ExcelFile(BytesIO(file.get_bytes()))
    return list(ef.sheet_names)

@anvil.server.callable
def import_file(file, tablist, rules):
    ef = pd.ExcelFile(BytesIO(file.get_bytes()))
    df = pd.read_excel(ef, sheet_name=tablist)

    new_df = None
    for i in rules:
        col = [convertCharToLoc(i['trandate']), convertCharToLoc(i['account_id']), convertCharToLoc(i['amount']),\
               convertCharToLoc(i['remarks']), convertCharToLoc(i['stmt_dtl']), convertCharToLoc(i['labels'])]
        nonNanList, nanList = divMappingColumnNameLists(i)
        for t in tablist:
            # iloc left one is row, right one is column
            # 1) Filter required columns
            tmp_df = df[t].iloc[:, [x for x in col if x is not None]]
            # 2) Rename columns
            tmp_df = tmp_df.rename(dict([(tmp_df.columns[x], nonNanList[x]) for x in range(len(nonNanList))]), axis='columns')
            # 3) Add 'not in rule' fields to the end
            tmp_df.loc[:, nanList] = None
            # 4) Concat temp DF to the resultant DF
            new_df = pd.concat([tmp_df.loc[:, col_name]], ignore_index=True, join="outer") if new_df is None else pd.concat([new_df, tmp_df.loc[:, col_name]], ignore_index=True, join="outer")
    # Ref - how to transform Pandas Dataframe to Anvil datatable
    # https://anvil.works/forum/t/add-row-to-data-table/2766/2
    return (new_df.dropna(subset=['amount'], ignore_index=True)).to_dict(orient='records')