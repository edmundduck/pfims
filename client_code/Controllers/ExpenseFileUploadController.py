import anvil.server
from ..Utils.Constants import CacheKey
from ..Utils.Logger import ClientLogger

# This is a module.
# You can define variables and functions here, and use them from any form. For example, in a top-level form:

logger = ClientLogger()

def generate_file_mapping_type_dropdown():
    """
    Access reference data - file mapping type dropdown from either client cache or generate from DB data returned from server side.

    Returns:
        cache.get_cache (list): File mapping type dropdown formed by import file type DB table data.
    """
    from ..Utils.ClientCache import ClientCache
    cache = ClientCache(CacheKey.DD_IMPORT_FILE_TYPE, None)
    if cache.is_empty():
        rows = anvil.server.call('generate_mapping_type_list')
        new_dropdown = list((r['name'], [r['id'], r['name']]) for r in rows)
        cache.set_cache(new_dropdown)
    return cache.get_cache()

@logger.log_function
def generate_file_mapping_group_dropdown(selected_filetype):
    """
    Access file mapping groups dropdown from either client cache or generate from DB data returned from server side.

    Parameters:
        selected_filetype (string): The selected file type ID.

    Returns:
        cache.get_cache (list): File mapping group dropdown formed by mapping group DB table data.
    """
    from ..Utils.ClientCache import ClientCache
    cache = ClientCache(CacheKey.DD_IMPORT_MAPPING_GRP, None)
    if cache.is_empty():
        rows = anvil.server.call('generate_mapping_list', selected_filetype)
        new_dropdown = list((r['name'], r['id']) for r in rows)
        cache.set_cache(new_dropdown)
    return cache.get_cache()

def get_file_mapping_type_dropdown_selected_item(filetype):
    """
    Return a complete key based on a partial file type which is a part of the key in a dropdown list.

    Parameters:
        filetype (string): The key of the file type.

    Returns:
        selected_item (list): Complete key of the selected item in import file type dropdown.
    """
    from ..Utils.ClientCache import ClientCache
    cache = ClientCache(CacheKey.DD_IMPORT_FILE_TYPE, None)
    if cache.is_empty():
        generate_file_mapping_type_dropdown()
    selected_item = cache.get_complete_key(filetype)
    return selected_item

@logger.log_function
def preview_excel_file(file):
    """
    Preview the uploaded Excel file.

    Parameters:
        file (object): The uploaded file object.

    Returns:
        sheets (list): List of tab names in the uploaded Excel file.
    """
    sheets = anvil.server.call('preview_file', file=file)
    logger.trace("sheets=", sheets)
    return sheets

@logger.log_function
def preprocess_excel_import(selected_rule, file, components):
    """
    Pre-process of Excel file import.

    Parameters:
        selected_rule (int): The ID of a mapping rule.
        file (object): The uploaded file object.
        components (list of component): A list of UI components which contain checkboxes for tabs to import.

    Returns:
        data_df (dataframe): Processed dataframe containing all transactions.
        lbl_df (dataframe): Processed dataframe containing all labels.
        acct_df (dataframe): Processed dataframe containing all accounts.
    """
    from anvil import CheckBox
    
    tablist = []
    for i in components:
        if isinstance(i, CheckBox) and i.checked:
            tablist.append(i.text)
    logger.info(f"{len(tablist)} tabs are chosen in {__name__}.")
    
    data_df, lbls_df, acct_df = anvil.server.call('proc_preprocess_excel_import', selected_rule, file, tablist)
    logger.trace("data_df=", data_df)
    logger.debug("lbls_df=", lbls_df)
    logger.debug("acct_df=", acct_df)
    return data_df, lbls_df, acct_df

@logger.log_function
def preprocess_pdf_import(file):
    """
    Pre-process of PDF file import.

    Parameters:
        file (object): The uploaded file object.

    Returns:
        pdf_tbl (pdfplumber.PDF): Processed pdfplumber.PDF object.
    """
    pdf_tbl = anvil.server.call('import_pdf_file', file=file)
    logger.trace("pdf_tbl=", pdf_tbl)
    return pdf_tbl