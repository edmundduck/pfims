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
import pdfplumber
import re
from . import LabelModule as lbl_mod
from . import FileUploadMappingModule as mapping_mod
from ..SysProcess.Constants import ExpenseDBTableDefinion as exptbl
from ..SysProcess import LoggingModule
from . import FileUploadMappingModule as fummod

# This is a server module. It runs on the Anvil server,
# rather than in the user's browser.
logger = LoggingModule.ServerLogger()
col_name = exptbl.def_namelist
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
    ef = pd.ExcelFile(BytesIO(file.get_bytes()))
    return list(ef.sheet_names)

@anvil.server.callable
def get_labels_list(file, lblcol):
    ef = pd.ExcelFile(BytesIO(file.get_bytes()))
    
@anvil.server.callable("import_file")
@logger.log_function
def import_file(file, tablist, rules, extra):
    ef = pd.ExcelFile(BytesIO(file.get_bytes()))
    df = pd.read_excel(ef, sheet_name=tablist)
    extra_dl = {k: [dic[k] for dic in extra] for k in extra[0]}

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
                    tmp_df[exptbl.Account] = int(extra_dl.get('etarget')[extra_dl_pointer])
                elif extra_dl.get('eaction')[extra_dl_pointer] == 'L':
                    tmp_df[exptbl.Labels] = extra_dl.get('etarget')[extra_dl_pointer] if tmp_df[exptbl.Labels] in (None, '') else tmp_df[exptbl.Labels] + extra_dl.get('etarget')[extra_dl_pointer]
                logger.trace("4) Map extra action logic, tmp_df=", tmp_df)
            
            # 5) Concat temp DF to the resultant DF
            new_df = pd.concat([tmp_df.loc[:, col_name]], ignore_index=True, join="outer") if new_df is None else pd.concat([new_df, tmp_df.loc[:, col_name]], ignore_index=True, join="outer")
            logger.trace("5) Concat temp DF to the resultant DF, new_df=", new_df)

    # Ref - how to transform Pandas Dataframe to Anvil datatable
    # https://anvil.works/forum/t/add-row-to-data-table/2766/2
    lbl_df = new_df.loc[:, [exptbl.Labels]]
    lbl_df.loc[:, ['Unnamed1', 'Unnamed2']] = None
    return (new_df.dropna(subset=[exptbl.Amount, exptbl.Date], ignore_index=True)).to_dict(orient='records'), lbl_df[exptbl.Labels].dropna().unique()

@anvil.server.callable("update_mapping")
@logger.log_function
def update_mapping(data, mapping):
    try:
        # 1. Get all items with action = 'C', and grab new field to create new labels
        # DL = Dict of Lists
        DL = {k: [dic[k] for dic in mapping] for k in mapping[0]}
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
        LD = [dict(zip(DL, col)) for col in zip(*DL.values())]
        if df is not None and LD is not None:
            for lbl_mapping in LD:
                if lbl_mapping is not None:
                    if lbl_mapping.get('action')[0] == "S":
                        df[exptbl.Labels].replace(lbl_mapping['srclbl'], None, inplace=True)                    
                    elif lbl_mapping.get('tgtlbl') is not None:
                        # Case 001 - string dict key handling review
                        id = eval(lbl_mapping['tgtlbl'])['id'] if isinstance(lbl_mapping.get('tgtlbl'), str) else lbl_mapping['tgtlbl']['id']
                        df[exptbl.Labels].replace(lbl_mapping['srclbl'], id, inplace=True)
        logger.trace("3) Replace labels with action = 'M' and 'C' to the target label codes in df")
        logger.trace("df=", df)
        # df.fillna(value={exptbl.Remarks:None, exptbl.StmtDtl:None, exptbl.Amount:0}, inplace=True)
        # Sorting ref: https://stackoverflow.com/questions/28161356/convert-column-to-date-format-pandas-dataframe
        return df.sort_values(by=exptbl.Date, key=pd.to_datetime, ascending=False, ignore_index=True).to_dict(orient='records')
    except (Exception) as err:
        logger.error(f"{__name__}.{type(err).__name__}: {err}")
    return None

# Internal function to format words in column headers and pdf lines to be single comparable format
def format_comparable_word(word):
    return word.lower().replace(' ', '')

# Internal function to generate a dynamic regular expression string based on pdf table column type
def get_regex_str(str_list, mandatory_type=None):
    trimmed_str_list = list(map(lambda x: x.lower().replace(' ', ''), str_list))
    trx_regex = ""
    isMandatorySet = False
    for i in trimmed_str_list:
        # This list comprehension is NOT working, to find out why
        # column_type = (key for key, value in column_type_mapping.items() if i in list(map(lambda x: x.lower().replace(' ', ''), value)))
        column_type = next((key for key, value in column_type_mapping.items() if i in list(map(lambda x: x.lower().replace(' ', ''), value))), None)
        logger.trace(f"column_type={column_type}")
        if mandatory_type and not isMandatorySet and column_type == mandatory_type:
            trx_regex = trx_regex + (datatype_regex.get(column_type, datatype_regex.get('any')))[:-1] + '+' + datatype_regex.get('whitespace')
            isMandatorySet = True
        else:
            trx_regex = trx_regex + datatype_regex.get(column_type, datatype_regex.get('any')) + datatype_regex.get('whitespace')
    logger.debug(f"trx_regex={trx_regex}")
    return trx_regex

@anvil.server.callable("import_pdf_file")
def import_pdf_file(file):
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
                        for header in column_headers:
                            pdf_word = format_comparable_word(word['text'])
                            header_word = format_comparable_word(header)
                            logger.trace(f"header_word=\"{header_word}\"/pdf_word=\"{pdf_word}\"")
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
                print("header_word_dict=", header_word_dict)
                explicit_lines = []
                for ch in column_headers:
                    explicit_lines.append(header_word_dict.get(format_comparable_word(ch)).get('x0')-5)
                explicit_lines.append(header_word_dict.get(format_comparable_word(column_headers[len(column_headers)-1])).get('x1'))
                bbox_top = header_word_dict.get(format_comparable_word(column_headers[len(column_headers)-1])).get('top')
                logger.debug("explicit_lines=", explicit_lines)
                print("explicit_lines=", explicit_lines)
                
                pdf_table_settings['explicit_vertical_lines'] = explicit_lines
                # bounding box (x0, y0, x1, y1)
                bounding_box = [explicit_lines[0], bbox_top, explicit_lines[-1]+10, page.height]
                crop_area = page.crop(bounding_box)
                crop_table = crop_area.extract_table(pdf_table_settings)
                logger.trace("crop_table=", crop_table)
                print("crop_table=", crop_table)
    
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
                            print("OOO=\"", row_to_check)
                            grace_search = 3
                        else:
                            logger.debug("XXX=\"", row_to_check)
                            print("XXX=\"", row_to_check)
                            crop_table.remove(row)
                            grace_search -= 1
                    else:
                        crop_table.remove(row)
                logger.trace("new crop_table=", crop_table)
                print("new crop_table=", crop_table)
                result_table += crop_table
        return result_table

@anvil.server.callable("update_pdf_mapping")
@logger.log_function
def update_pdf_mapping(data, mapping, account, labels):
    try:
        column_headers, unwantedList = [], []
        col_num = 0
        df = pd.DataFrame(data=data)
        matrix = {}
        logger.debug("mapping=", mapping)
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
        # Generate mapping matrix which has unique columns each
        # Sample - mapping_matrix= [[0, 3, 2], [0, 4, 2]]
        mapping_matrix = fummod.generate_mapping_matrix(matrix, nonNanList.copy())

        new_df = None
        for m in mapping_matrix:
            # 1) Filter required columns per mapping matrix
            tmp_df = df.iloc[:, m]
            logger.trace(f"tmp_df={tmp_df.to_string()}")
            # 2) Rename columns
            tmp_df = tmp_df.rename(dict([(tmp_df.columns[x], nonNanList[x]) for x in range(len(nonNanList))]), axis='columns')
            # 3) Add 'not in rule' fields to the end
            tmp_df.loc[:, nanList] = None
            new_df = pd.concat([tmp_df.loc[:, col_name]], ignore_index=True, join="outer") if new_df is None else pd.concat([new_df, tmp_df.loc[:, col_name]], ignore_index=True, join="outer")
        df = new_df

        # 4) Format date and other columns data accordingly
        df[exptbl.Date] = pd.to_datetime(df[exptbl.Date], errors='coerce').dt.date
        if account is not None: df[exptbl.Account] = account
        if labels is not None: df[exptbl.Labels] = labels
        logger.trace("df=", df.to_string())
        df = df.dropna(subset=[exptbl.Amount, exptbl.Date], ignore_index=True)
        return df.sort_values(by=exptbl.Date, key=pd.to_datetime, ascending=False, ignore_index=True).to_dict(orient='records')
    except (Exception) as err:
        logger.error(f"{__name__}.{type(err).__name__}: {err}")
    return None
