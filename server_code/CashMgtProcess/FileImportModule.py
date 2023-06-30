import anvil.secrets
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
from io import BytesIO
import pandas as pd
from . import LabelModule as lbl_mod
from . import FileUploadMappingModule as mapping_mod
from ..System import SystemModule as sysmod

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
def get_labels_list(file, lblcol):
    ef = pd.ExcelFile(BytesIO(file.get_bytes()))
    
@anvil.server.callable
def import_file(file, tablist, rules, extra):
    ef = pd.ExcelFile(BytesIO(file.get_bytes()))
    df = pd.read_excel(ef, sheet_name=tablist)
    extra_dl = {k: [dic[k] for dic in extra] for k in extra[0]}

    new_df = None
    for i in rules:
        col = [convertCharToLoc(i['trandate']), convertCharToLoc(i['account_id']), convertCharToLoc(i['amount']),\
               convertCharToLoc(i['remarks']), convertCharToLoc(i['stmt_dtl']), convertCharToLoc(i['labels'])]
        common_col = set(i.values()).intersection(extra_dl.get('col'))
                
        nonNanList, nanList = divMappingColumnNameLists(i)
        for t in tablist:
            # iloc left one is row, right one is column
            # 1) Filter required columns
            tmp_df = df[t].iloc[:, [x for x in col if x is not None]]
            
            # 2) Rename columns
            tmp_df = tmp_df.rename(dict([(tmp_df.columns[x], nonNanList[x]) for x in range(len(nonNanList))]), axis='columns')
            
            # 3) Add 'not in rule' fields to the end
            tmp_df.loc[:, nanList] = None

            # 4) Map extra action logic
            for c in common_col:
                extra_dl_pointer = extra_dl.get('col').index(c)
                if extra_dl.get('eaction')[extra_dl_pointer] == 'A':
                    tmp_df['account_id'] = int(extra_dl.get('etarget')[extra_dl_pointer])
                elif extra_dl.get('eaction')[extra_dl_pointer] == 'L':
                    tmp_df['labels'] = extra_dl.get('etarget')[extra_dl_pointer] if tmp_df['labels'] in (None, '') else tmp_df['labels'] + extra_dl.get('etarget')[extra_dl_pointer]

            tmp_df['trandate'] = pd.to_datetime(tmp_df.trandate, exact=False, unit='D')
            # 5) Concat temp DF to the resultant DF
            new_df = pd.concat([tmp_df.loc[:, col_name]], ignore_index=True, join="outer") if new_df is None else pd.concat([new_df, tmp_df.loc[:, col_name]], ignore_index=True, join="outer")

    # Ref - how to transform Pandas Dataframe to Anvil datatable
    # https://anvil.works/forum/t/add-row-to-data-table/2766/2
    lbl_df = new_df.loc[:, ['labels']]
    lbl_df.loc[:, ['Unnamed1', 'Unnamed2']] = None
    return (new_df.dropna(subset=['amount', 'trandate'], ignore_index=True)).sort_values(by='trandate').to_dict(orient='records'), lbl_df['labels'].dropna().unique()

@anvil.server.callable
def update_mapping(data, mapping):
    try:
        # 1. Get all items with action = 'C', and grab new field to create new labels
        # DL = Dict of Lists
        DL = {k: [dic[k] for dic in mapping] for k in mapping[0]}
        DL_action = {k: [dic[k] for dic in DL['action']] for k in DL['action'][0]}
        pos_create = [x for x in range(len(DL_action['id'])) if DL_action['id'][x] == 'C']
        lbl_mogstr = {
            'name': [DL['new'][x] for x in pos_create],
            'keywords': [ None for i in range(len(pos_create)) ],
            'status': [ True for i in range(len(pos_create)) ]
        }
        # labels param is transposed from DL to LD (List of Dicts)
        lbl_id = lbl_mod.create_label(labels=[dict(zip(lbl_mogstr, col)) for col in zip(*lbl_mogstr.values())])
    
        # TODO no f/e logoc in b/e
        if lbl_id is None:
            raise Exception("Fail to create label.")
    
        # 2. Replace labels with action = 'C' to the newly created label codes in step 1
        for lbl_loc in range(len(lbl_id)):
            DL['tgtlbl'][pos_create[lbl_loc]] = {'id': lbl_id[lbl_loc], 'text': None}
    
        # 3. Replace labels with action = 'M' and 'C' to the target label codes in df
        # df_transpose = {k: [dic[k] for dic in self.tag.get('dataframe')] for k in self.tag.get('dataframe')[0]}
        df = pd.DataFrame({k: [dic[k] for dic in data] for k in data[0]})
        LD = [dict(zip(DL, col)) for col in zip(*DL.values())]
        if df is not None and LD is not None:
            for lbl_mapping in LD:
                if lbl_mapping is not None:
                    if lbl_mapping.get('action').get('id') == "S":
                        df['labels'].replace(lbl_mapping['srclbl'], None, inplace=True)                    
                    elif lbl_mapping.get('tgtlbl') is not None:
                        # Case 001 - string dict key handling review
                        id = eval(lbl_mapping['tgtlbl'])['id'] if isinstance(lbl_mapping.get('tgtlbl'), str) else lbl_mapping['tgtlbl']['id']
                        df['labels'].replace(lbl_mapping['srclbl'], id, inplace=True)
        # df.fillna(value={'remarks':None, 'stmt_dtl':None, 'amount':0}, inplace=True)
        return df.sort_values(by='trandate', ascending=False, ignore_index=True).to_dict(orient='records')
    except (Exception) as err:
        sysmod.print_data_debug("OperationalError in " + update_mapping.__name__, err)
    return None