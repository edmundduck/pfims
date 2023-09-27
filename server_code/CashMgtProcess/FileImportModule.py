import anvil.files
from anvil.files import data_files
import anvil.secrets
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
from io import BytesIO
import pandas as pd
import numpy as np
import pdfplumber
import re
import datetime
from . import LabelModule as lbl_mod
from . import FileUploadMappingModule as fummod
from ..ServerUtils import HelperModule as helper
from ..SysProcess import LoggingModule
from ..DataObject.FinObject import ExpenseRecord as exprcd

# This is a server module. It runs on the Anvil server,
# rather than in the user's browser.
logger = LoggingModule.ServerLogger()
col_name = exprcd.data_list
regex_ymd = '(\d{4}|\d{2})[\.\-/ ]{0,1}(0[1-9]|1[0-2]|[A-Za-z]{3})[\.\-/ ]{0,1}(0[1-9]|[12][0-9]|3[01])'        # yyyy-mm-dd / yyyy-mmm-dd
regex_dmy = '(0[1-9]|[12][0-9]|3[01])[\.\-/ ]{0,1}(0[1-9]|1[0-2]|[A-Za-z]{3})[\.\-/ ]{0,1}(\d{4}|\d{2})'        # dd-mm-yyyy / dd-mmm-yyyy
regex_mdy = '(0[1-9]|1[0-2]|[A-Za-z]{3})[\.\-/ ]{0,1}(0[1-9]|[12][0-9]|3[01])[\.\-/ ]{0,1}(\d{4}|\d{2})'        # mm-dd-yyyy / mmm-dd-yyyy
datatype_regex = {
    'date': f"({regex_ymd}|{regex_dmy}|{regex_mdy})*",
    'amount': '(\d+\.(\d{3}|\d{2}))*',
    'whitespace': '\s*',
    'any': '.*'
}
# TODO - Not hard code but dynamic recognition
column_type_mapping = {
    'date': ['Date'],
    'amount': ['Paid out', 'Paid in', 'Money Out', 'Money In', 'Money Out (£)', 'Money In (£)', 'Balance', 'Balance (£)', 'Withdraw', 'Deposit']
}
pdf_table_settings = {
    "vertical_strategy": "explicit", 
    "horizontal_strategy": "text",
    "explicit_vertical_lines": [55, 100, 350, 420, 500, 550],
    "explicit_horizontal_lines": [],
    # "snap_tolerance": 0,
    "snap_x_tolerance": 6,
    # "snap_y_tolerance": 5,
    # "join_tolerance": 3,
    # "join_x_tolerance": 3,
    # "join_y_tolerance": 3,
    # "edge_min_length": 3,
    # "min_words_vertical": 1,
    # "min_words_horizontal": 2,
    # "keep_blank_chars": False,
    # "text_tolerance": 3,
    "text_x_tolerance": 5,
    # "text_y_tolerance": 5,
    # "intersection_tolerance": 15,
    # "intersection_x_tolerance": 15,
    # "intersection_y_tolerance": 3,
}

@anvil.server.callable
def preview_file(file):
    """
    Return all tabs in the uploaded Excel file.

    Parameters:
        file (object): The uploaded file object.

    Returns:
        ef.sheet_names (list): List of tab names in the uploaded Excel file.
    """
    ef = pd.ExcelFile(BytesIO(file.get_bytes()))
    return list(ef.sheet_names)

@anvil.server.callable("import_file")
@logger.log_function
def import_file(file, tablist, rules, extra):
    """
    Import Excel file data into a Dataframe for further processing.

    Parameters:
        file (object): The uploaded file object.
        tablist (list): The list of Excel tabs to be imported.
        rules (list of list): A mapping matrix for how Excel columns map to Expense module repeating panel to display.
        extra (list of dict): Extra mapping action per rule.

    Returns:
        new_df (dataframe): Processed dataframe.
    """
    ef = pd.ExcelFile(BytesIO(file.get_bytes()))
    df = pd.read_excel(ef, sheet_name=tablist)
    extra_dl = helper.to_dict_of_list(extra)


    new_df = None
    for i in rules:
        # Convert column in character ID to number for Pandas read_excel
        col = list(map(lambda x: ord(i[x].lower()) - 97 if 'a' <= i[x].lower() <= 'z' else None , col_name))
        common_col = set(i.values()).intersection(extra_dl.get('col'))
                
        nonNanList, nanList = ([c for c in col_name if i[c] not in (None, '')], [c for c in col_name if i[c] in (None, '')])
        for t in tablist:
            # iloc left one is row, right one is column
            # 1) Filter required columns
            tmp_df = df[t].iloc[:, [x for x in col if x is not None]]
            logger.trace("1) Filter required columns, tmp_df=", tmp_df)
            
            # 2) Rename columns
            tmp_df = tmp_df.rename(dict([(tmp_df.columns[x], nonNanList[x]) for x in range(len(nonNanList))]), axis='columns')
            logger.trace("2) Rename columns, tmp_df=", tmp_df)
            
            # 3) Add 'not in rule' fields to the end
            tmp_df.loc[:, nanList] = None

            # 4) Map extra action logic
            for c in common_col:
                extra_dl_pointer = extra_dl.get('col').index(c)
                if extra_dl.get('eaction')[extra_dl_pointer] == 'A':
                    tmp_df[exprcd.Account] = int(extra_dl.get('etarget')[extra_dl_pointer])
                elif extra_dl.get('eaction')[extra_dl_pointer] == 'L':
                    tmp_df[exprcd.Labels] = extra_dl.get('etarget')[extra_dl_pointer] if tmp_df[exprcd.Labels] in (None, '') else tmp_df[exprcd.Labels] + extra_dl.get('etarget')[extra_dl_pointer]
                logger.trace("4) Map extra action logic, tmp_df=", tmp_df)
            
            # 5) Concat temp DF to the resultant DF
            new_df = pd.concat([tmp_df.loc[:, col_name]], ignore_index=True, join="outer") if new_df is None else pd.concat([new_df, tmp_df.loc[:, col_name]], ignore_index=True, join="outer")
            logger.trace("5) Concat temp DF to the resultant DF, new_df=", new_df)

    # Ref - how to transform Pandas Dataframe to Anvil datatable
    # https://anvil.works/forum/t/add-row-to-data-table/2766/2
    lbl_df = new_df.loc[:, [exprcd.Labels]]
    lbl_df.loc[:, ['Unnamed1', 'Unnamed2']] = None
    return (new_df.dropna(subset=[exprcd.Amount, exprcd.Date], ignore_index=True)).to_dict(orient='records'), lbl_df[exprcd.Labels].dropna().unique()

@anvil.server.callable("update_mapping")
@logger.log_function
def update_mapping(data, mapping):
    """
    Update labels mapping from the imported Dataframe.

    Parameters:
        data (dataframe): The dataframe to be updated with the mapping.
        mapping (list): The list of labels mapping from user's input.

    Returns:
        df (dataframe): Processed dataframe.
    """
    try:
        # 1. Get all items with action = 'C', and grab new field to create new labels
        # DL = Dict of Lists
        DL = helper.to_dict_of_list(mapping)
        # DL_action = {k: [dic[k] for dic in DL['action']] for k in DL['action'][0]}   // dict id,text structure
        DL_action = {'id': [dic[0] for dic in DL['action']]}
        pos_create = [x for x in range(len(DL_action['id'])) if DL_action['id'][x] == 'C']
        logger.debug("pos_create=", pos_create)
        lbl_mogstr = {
            'name': [DL['new'][x] for x in pos_create],
            'keywords': [ None for i in range(len(pos_create)) ],
            'status': [ True for i in range(len(pos_create)) ]
        }
        # labels param is transposed from DL to LD (List of Dicts)
        lbl_id = lbl_mod.create_label(labels=[dict(zip(lbl_mogstr, col)) for col in zip(*lbl_mogstr.values())])
        logger.debug("Label created with ID lbl_id=", lbl_id)
        if lbl_id is None: raise Exception("Fail to create label.")
    
        # 2. Replace labels with action = 'C' to the newly created label codes in step 1
        for lbl_loc in range(len(lbl_id)): DL['tgtlbl'][pos_create[lbl_loc]] = {'id': lbl_id[lbl_loc], 'text': None}
        logger.trace("2) Replace labels with action = 'C' to the newly created label codes in step 1")
        logger.trace("DL['tgtlbl']=", DL['tgtlbl'])
    
        # 3. Replace labels with action = 'M' and 'C' to the target label codes in df
        # df_transpose = {k: [dic[k] for dic in self.tag.get('dataframe')] for k in self.tag.get('dataframe')[0]}
        df = pd.DataFrame({k: [dic[k] for dic in data] for k in data[0]})
        
        LD = helper.to_list_of_dict(DL)
        if df is not None and LD is not None:
            for lbl_mapping in LD:
                if lbl_mapping is not None:
                    if lbl_mapping.get('action')[0] == "S":
                        df[exprcd.Labels].replace(lbl_mapping['srclbl'], None, inplace=True)                    
                    elif lbl_mapping.get('tgtlbl') is not None:
                        id = lbl_mapping['tgtlbl'][0]
                        df[exprcd.Labels].replace(lbl_mapping['srclbl'], id, inplace=True)
        logger.trace("3) Replace labels with action = 'M' and 'C' to the target label codes in df")
        logger.trace("df=", df)
        # df.fillna(value={exprcd.Remarks:None, exprcd.StmtDtl:None, exprcd.Amount:0}, inplace=True)
        # Sorting ref: https://stackoverflow.com/questions/28161356/convert-column-to-date-format-pandas-dataframe
        return df.replace([np.nan], [None]).sort_values(by=exprcd.Date, key=pd.to_datetime, ascending=False, ignore_index=True).to_dict(orient='records')
    except (Exception) as err:
        logger.error(err)
    return None

def format_comparable_word(word):
    """
    Format words in column headers and pdf lines to be single comparable format.

    Parameters:
        word (string): The word to be formatted.

    Returns:
        word (string): Formatted word for comparison.
    """
    return word.lower().replace(' ', '')

def get_regex_str(str_list, mandatory_type=None):
    """
    Generate a dynamic regular expression string based on pdf table column type.

    Parameters:
        str_list (string): PDF column names to be diagnosed.
        mandatory_type (string): Data type to be checked which regular expression to be added to the result.

    Returns:
        trx_regex (string): Resultant regular expression which will be used for finding the column header in the imported file.
    """
    trimmed_str_list = list(map(lambda x: x.lower().replace(' ', ''), str_list))
    trx_regex = ""
    isMandatorySet = False
    for i in trimmed_str_list:
        # This list comprehension is NOT working, to find out why
        # column_type = (key for key, value in column_type_mapping.items() if i in list(map(lambda x: x.lower().replace(' ', ''), value)))
        column_type = next((key for key, value in column_type_mapping.items() if i in list(map(lambda x: x.lower().replace(' ', ''), value))), None)
        if mandatory_type and not isMandatorySet and column_type == mandatory_type:
            trx_regex = trx_regex + (datatype_regex.get(column_type, datatype_regex.get('any')))[:-1] + '+' + datatype_regex.get('whitespace')
            isMandatorySet = True
        else:
            trx_regex = trx_regex + datatype_regex.get(column_type, datatype_regex.get('any')) + datatype_regex.get('whitespace')
    logger.trace(f"trx_regex={trx_regex}")
    return trx_regex

@anvil.server.callable("import_pdf_file")
def import_pdf_file(file):
    """
    Import PDF file data into a Dataframe for further processing.

    Parameters:
        file (object): The uploaded file object.

    Returns:
        result_table (pdfplumber.PDF): Processed pdfplumber.PDF object.
    """
    with pdfplumber.open(BytesIO(file.get_bytes())) as pdf:
        # compiled_column_headers = re.compile('.*'.join(ch.replace(' ', '.*') for ch in column_headers))
        result_table = []
        for pagenum in range(len(pdf.pages)):
            page = pdf.pages[pagenum]
            text = page.extract_text(layout=True, x_density=4.5, y_density=10)
    
            # Find column header by regex
            compiled_column_headers = re.compile(r'.*Date.*Balance.*')
            result = compiled_column_headers.search(text)
            if result:
                # Finding column headers
                # column_headers = ['Date', 'Payment type and details', 'Paid out', 'Paid in', 'Balance']
                # column_headers = ['Date', 'Pmnt', 'Details', 'Money Out (£)', 'Money In (£)', 'Balance (£)']
                # column_headers = result.group(0).split()
                column_headers = list(filter(lambda x: x.strip() not in (None, ''), result.group(0).split('   ')))
                logger.debug("column_headers=", column_headers)
                
                # Word object comparison
                header_word_dict = {}
                partial_word_list = []
                for word in page.extract_words():
                    if len(header_word_dict.keys()) < len(column_headers):
                        patternNotFound = True
                        pdf_word = format_comparable_word(word['text'])
                        logger.trace(f"pdf_word=\"{pdf_word}\"")
                        for header in column_headers:
                            header_word = format_comparable_word(header)
                            if pdf_word == header_word:
                                # Case 1
                                # word = date, header = date
                                # Case 2
                                # word = paidout, header = paid out
                                # word = paidin, header = paid in
                                # header_word_dict[word['text']] = {
                                header_word_dict[pdf_word] = {
                                    'x0': word['x0'],
                                    'x1': word['x1'],
                                    'top': word['top'],
                                    'bottom': word['bottom']
                                }
                                partial_word_list = []
                                patternNotFound = False
                            elif pdf_word in header_word:
                                # Case 3
                                # word = payment, header = payment type and details
                                # word = type, header = payment type and details
                                # word = and, header = payment type and details
                                # word = details,  header = payment type and details
                                partial_word_list.append({
                                    # 'text': word['text'],
                                    'text': pdf_word,
                                    'x0': word['x0'],
                                    'x1': word['x1'],
                                    'top': word['top'],
                                    'bottom': word['bottom']
                                })
                                combined_text = "".join(w.get('text') for w in partial_word_list)
                                if combined_text == header_word:
                                    header_word_dict[combined_text] = {
                                        'x0': partial_word_list[0].get('x0'),
                                        'x1': partial_word_list[len(partial_word_list)-1].get('x1'),
                                        'top': word['top'],
                                        'bottom': word['bottom']
                                    }
                                    partial_word_list = []
                                patternNotFound = False
                        if patternNotFound:
                            header_word_dict.clear()
                            partial_word_list = []
    
                logger.debug("header_word_dict=", header_word_dict)
                explicit_lines = []
                for ch in column_headers:
                    explicit_lines.append(header_word_dict.get(format_comparable_word(ch)).get('x0')-5)
                explicit_lines.append(header_word_dict.get(format_comparable_word(column_headers[len(column_headers)-1])).get('x1'))
                bbox_top = header_word_dict.get(format_comparable_word(column_headers[len(column_headers)-1])).get('top')
                logger.debug("explicit_lines=", explicit_lines)
                
                pdf_table_settings['explicit_vertical_lines'] = explicit_lines
                # bounding box (x0, y0, x1, y1)
                bounding_box = [explicit_lines[0], bbox_top, explicit_lines[-1]+10, page.height]
                crop_area = page.crop(bounding_box)
                crop_table = crop_area.extract_table(pdf_table_settings)
                logger.trace("crop_table=", crop_table)
    
                # Returning best match table by filtering unwanted rows
                grace_search = 3
                # Skip the table header row
                for row in crop_table[1:]:
                    if grace_search >= 0:
                        row_to_check = ' '.join(cell for cell in row)
                        compiled_date = re.compile(get_regex_str(column_headers, 'date'))
                        compiled_amt = re.compile(get_regex_str(column_headers, 'amount'))
                        if re.match(r'^\s*$', row_to_check):
                            crop_table.remove(row)
                        elif re.search(compiled_date, row_to_check) or re.search(compiled_amt, row_to_check) :
                            logger.debug("OOO=\"", row_to_check)
                            grace_search = 3
                        else:
                            logger.debug("XXX=\"", row_to_check)
                            # crop_table.remove(row)
                            grace_search -= 1
                    else:
                        crop_table.remove(row)
                logger.trace("new crop_table=", crop_table)
                result_table += crop_table
        return result_table

@anvil.server.callable("update_pdf_mapping")
@logger.log_function
def update_pdf_mapping(data, mapping, account, labels):
    """
    Update various data mapping from the imported Dataframe.

    Parameters:
        data (dataframe/pdfplumber.PDF): The dataframe or PDF object to be updated with the mapping.
        mapping (list): The list of column headers mapping from user's input.
        account (int): The selected account ID requiring extra mapping.
        labels (int): The selected label ID requiring extra mapping.

    Returns:
        df (dataframe): Processed dataframe.
    """
    # Logic of merging all amount columns
    def merge_amt_cols(row):
        logger.trace(f"merge_amt_cols row={row}")
        if all(pd.isna(row[c]) for c in matrix.get(exprcd.Amount, None)):
            return np.nan
        else:
            for c in matrix.get(exprcd.Amount, None):
                logger.trace(f"merge_amt_cols c={c}/row[c]={row[c]}/float(row[c])={float(row[c])}")
                if pd.notna(row[c]) and float(row[c]):
                    return row[c]

    # Logic of merging relevant rows into one row
    def merge_rows(row, start, end, dateId):
        result = None
        logger.trace(f"merge_rows row=\n{row[start:end+1]}")
        if all(pd.isna(c) for c in row[start:end+1]):
            return np.nan
        else:
            for c in row[start:end+1]:
                if pd.notna(c):
                    if result is None:
                        result = c
                    else:
                        if not isinstance(c, (int, float)) and not isinstance(c, (datetime.date, datetime.datetime)):
                            result = ' '.join((result, c))
                        elif isinstance(c, (datetime.date, datetime.datetime)) and start != dateId:
                            # Special date handling - where multiple rows in amount associate to only one date row
                            result = row[dateId]
            logger.trace(f"merge_rows result=\n{result}")
            return pd.Series(result)
            
    try:
        column_headers, unwantedList = [], []
        col_num = 0
        df = pd.DataFrame(data=data)
        matrix = {}
        logger.debug(f"data={data}")
        logger.debug(f"mapping={mapping}")
        for x in mapping:
            # Amount sign handling
            if x.get('sign') is not None:
                df[col_num] = -(pd.to_numeric(df[col_num].astype(str).str.replace(',',''), errors='coerce')) if x.get('sign') == '-' else pd.to_numeric(df[col_num].astype(str).str.replace(',',''), errors='coerce')
            if x.get('tgtcol') is not None:
                column_headers.append(x.get('tgtcol')[0])
                if matrix.get(x.get('tgtcol')[0], None) is None:
                    matrix[x.get('tgtcol')[0]] = [col_num]
                else:
                    matrix[x.get('tgtcol')[0]].append(col_num)
            else:
                unwantedList.append(col_num)
            col_num += 1
                
        logger.debug(f"matrix={matrix}, column_headers={column_headers}")
        nonNanList, nanList = ([c for c in col_name if c in column_headers], [c for c in col_name if c not in column_headers])
        
        # Merge all amount columns into one for later row merge actions
        df[exprcd.Amount] = df.apply(merge_amt_cols, axis='columns')
        matrix[exprcd.Amount] = [exprcd.Amount]
        
        # Generate mapping matrix which has unique columns each
        # Sample - mapping_matrix= [[0, 3, 2], [0, 4, 2]]
        logger.debug(f"nonNanList={nonNanList}, nanList={nanList}")
        mapping_matrix = fummod.generate_mapping_matrix(matrix, nonNanList.copy())

        new_df = None
        for m in mapping_matrix:
            # 1) Filter required columns per mapping matrix
            tmp_df = df.loc[:, m]
            logger.trace(f"tmp_df={tmp_df.to_string()}")
            # 2) Rename columns
            tmp_df = tmp_df.rename(dict([(tmp_df.columns[x], nonNanList[x]) for x in range(len(nonNanList))]), axis='columns')
            # 3) Add 'not in rule' fields to the end
            tmp_df.loc[:, nanList] = None
            new_df = pd.concat([tmp_df.loc[:, col_name]], ignore_index=True, join="outer") if new_df is None else pd.concat([new_df, tmp_df.loc[:, col_name]], ignore_index=True, join="outer")
        df = new_df

        # 4) Format date and other columns data accordingly and merge rows
        df[exprcd.Date] = pd.to_datetime(df[exprcd.Date], errors='coerce').dt.date
        date_not_null_df = df[df[exprcd.Date].notnull()]
        amt_not_null_df = df[df[exprcd.Amount].notnull()]
        logger.trace(f"date_not_null_df=\n{date_not_null_df}")
        new_df = None
        firstAmtId = int(amt_not_null_df.iloc[0].name) if amt_not_null_df is not None and amt_not_null_df.size > 0 else None
        for i in range(date_not_null_df.index.size):
            curRowId = int(date_not_null_df.iloc[i].name)
            dateId = curRowId
            try:
                nextRowId = int(date_not_null_df.iloc[i+1].name)
            except (IndexError) as err:
                nextRowId = None
            while amt_not_null_df is not None and amt_not_null_df.size > 0 and firstAmtId and nextRowId and firstAmtId < nextRowId:
                logger.trace(f"amt_not_null_df=\n{amt_not_null_df}")
                logger.trace(f"curRowId={curRowId}, nextRowId={nextRowId}, firstAmtId={firstAmtId}")
                # Deal with a row in date_not_null_df without a date (e.g. multiple transactions in one date but only one date found in date column)
                if pd.isna(df.loc[curRowId, exprcd.Date]):
                    df.loc[curRowId, exprcd.Date] = df.loc[dateId][exprcd.Date]                
                if firstAmtId != curRowId and firstAmtId in range(curRowId, nextRowId):
                    tmp_df = df.apply(merge_rows, args=(curRowId, firstAmtId, dateId), axis='index', result_type=None)
                    new_df = pd.concat(tmp_df, ignore_index=True, join="outer") if new_df is None else pd.concat([new_df, tmp_df], ignore_index=True, join="outer")
                    print(f"Case 1 - Diff index names for 1st date and 1st amt, merge all rows in between - new_df=\n{new_df.to_string()}")
                    amt_not_null_df = amt_not_null_df.drop(firstAmtId, axis='index')
                    curRowId = firstAmtId + 1
                    firstAmtId = int(amt_not_null_df.iloc[0].name) if not amt_not_null_df.empty else None
                elif firstAmtId == curRowId:
                    oneline_df = df.loc[[firstAmtId]]
                    amt_not_null_df = amt_not_null_df.drop(firstAmtId, axis='index')
                    firstAmtId = int(amt_not_null_df.iloc[0].name) if not amt_not_null_df.empty else None
                    if firstAmtId and min(firstAmtId, nextRowId) - curRowId > 1:
                        tmp_df = df.apply(merge_rows, args=(curRowId, min(firstAmtId, nextRowId)-1, dateId), axis='index', result_type=None)
                        new_df = pd.concat(tmp_df, ignore_index=True, join="outer") if new_df is None else pd.concat([new_df, tmp_df], ignore_index=True, join="outer")
                        print(f"Case 2a - Same index names for both 1st row in date df and amt df (nexN row without date and amt require to merge) - new_df=\n{new_df.to_string()}")
                    else:
                        new_df = pd.concat([oneline_df], ignore_index=True, join="outer") if new_df is None else pd.concat([new_df, oneline_df], ignore_index=True, join="outer")
                        print(f"Case 2b - Same index names for both 1st row in date df and amt df (No next row to merge) - new_df=\n{new_df.to_string()}")
                else:
                    pass
        df = new_df
        
        if account is not None: df[exprcd.Account] = account
        if labels is not None: df[exprcd.Labels] = labels
        return df.dropna(subset=[exprcd.Amount, exprcd.Date], ignore_index=True).replace([np.nan], [None])\
            .sort_values(by=exprcd.Date, key=pd.to_datetime, ascending=False, ignore_index=True).to_dict(orient='records')
    except (Exception) as err:
        logger.error(err)
    return None
