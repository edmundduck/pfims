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

# Internal function to get the list of included column names in mapping matrix
def divMappingColumnNameLists(matrix):
    col_name = ['trandate', 'account_id', 'amount', 'remarks', 'stmt_dtl', 'labels']
    nonNanList = []
    nanList = []
    for c in col_name:
        print("c=", c, ", matrix[c]=", matrix[c])
        if matrix[c] in (None, ''):
            nanList.append(c)
        else:
            nonNanList.append(c)
    return col_name, nonNanList, nanList

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
    for i in rules:
        col = [convertCharToLoc(i['trandate']), convertCharToLoc(i['account_id']), convertCharToLoc(i['amount']),\
               convertCharToLoc(i['remarks']), convertCharToLoc(i['stmt_dtl']), convertCharToLoc(i['labels'])]
        print("col=", col)
        col_def, nonNanList, nanList = divMappingColumnNameLists(i)
        # test2 = pd.DataFrame(data=None, columns=nanList)
        for t in tablist:
            # iloc left one is row, right one is column
            # test1 = df[t].iloc[:,[date, lbl, amt, remarks]]
            print("df=", df[t].to_string())
            test1 = df[t].iloc[:, filter(None, col)]
            test1.loc[:, nanList] = None
            colobj = {}
            for x in nonNanList:
                colobj[f"Unnamed: {convertCharToLoc(i[x])}"] = x
            print("colobj=", colobj)
            # test2 = test1.reindex(columns=test1.columns.tolist() + nanList, fill_value=None)
            # test1.rename(columns={test1.columns[0]: "trandate", \
            #                       test1.columns[1]: "account_id", \
            #                       test1.columns[2]: "amount", \
            #                       test1.columns[3]: "remarks", \
            #                       test1.columns[4]: "stmt_dtl", \
            #                       test1.columns[5]: "labels"}, \
            #              inplace=True)
            test1.rename(columns=colobj, inplace=True)
            print("TEST1", test1.to_string())
            test2 = test1.loc[:, col_def]
            print("TEST2", test2)
            # new_df = pd.concat([test1], ignore_index=True) if new_df is None else pd.concat([new_df, test1], ignore_index=True)
            new_df = pd.concat([test2], ignore_index=True, join="outer") if new_df is None else pd.concat([new_df, test2], ignore_index=True, join="outer")
    # Ref - how to transform Pandas Dataframe to Anvil datatable
    # https://anvil.works/forum/t/add-row-to-data-table/2766/2
    test = pd.DataFrame(
        data={"trandate": ["2020-01-02", "2022-05-09"], 
              "labels": ["801,", "0,"],
              "amount": [30, 100],
              "remarks": ["TEST", "AAAG"]
             }
    )
    return (new_df.dropna(subset=['amount'], ignore_index=True)).to_dict(orient='records')
    # return test.to_dict(orient='records')
