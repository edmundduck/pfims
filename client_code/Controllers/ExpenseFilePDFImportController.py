import anvil.server
from ..Utils.Constants import CacheKey
from ..Utils.Logger import ClientLogger

# This is a module.
# You can define variables and functions here, and use them from any form. For example, in a top-level form:

logger = ClientLogger()

@logger.log_function
def generate_expense_tabs_dropdown(data=None, reload=False):
    """
    Access expense tabs dropdown from either client cache or generate from DB data returned from server side.

    Parameters:
        data (list of RealRowDict): Optional. The data list returned from the DB table to replace the client cache, should the client cache not already contain the data.
        reload (Boolean): Optional. True if clear cache is required. False by default.

    Returns:
        cache.get_cache (list): Expense tabs dropdown formed by expense tabs DB table data.
    """
    from . import ExpenseInputController
    return ExpenseInputController.generate_expense_tabs_dropdown(data, reload)

def generate_accounts_dropdown(data=None, reload=False):
    """
    Access accounts dropdown from either client cache or generate from DB data returned from server side.

    Parameters:
        data (list of RealRowDict): Optional. The data list returned from the DB table to replace the client cache, should the client cache not already contain the data.
        reload (Boolean): Optional. True if clear cache is required. False by default.

    Returns:
        cache.get_cache (list): Accounts dropdown formed by accounts DB table data.
    """
    from . import AccountMaintController
    return AccountMaintController.generate_accounts_dropdown(data, reload)

def generate_labels_dropdown(data=None, reload=False):
    """
    Access labels dropdown from either client cache or generate from DB data returned from server side.

    Parameters:
        data (list of RealRowDict): Optional. The data list returned from the DB table to replace the client cache, should the client cache not already contain the data.
        reload (Boolean): Optional. True if clear cache is required. False by default.

    Returns:
        cache.get_cache (list): Labels dropdown formed by labels DB table data.
    """
    from . import LabelMaintController
    return LabelMaintController.generate_labels_dropdown(data, reload)

def get_account_dropdown_selected_item(acct_id):
    """
    Return a complete key based on a partial account ID which is a part of the key in a dropdown list.

    Parameters:
        acct_id (int): The account ID.

    Returns:
        selected_item (list): Complete key of the selected item in account dropdown.
    """
    from . import AccountMaintController
    return AccountMaintController.get_account_dropdown_selected_item(acct_id)

def populate_repeating_panel_items(data=None):
    """
    Populate repeating panel items with data padded with a list of blank items.

    Parameters:
        data (pdfplumber.PDF): pdfplumber.PDF object for transformation.

    Returns:
        result (list of dict): A list of data to populate to repeating panel.
    """
    DL = {
        'srccol': data[0] if data is not None else None,
        'tgtcol': [None for i in range(len(data[0]))] if data is not None else [None],
        'sign': [None for i in range(len(data[0]))] if data is not None else [None]
    }
    logger.trace("DL=", DL)
    result = [dict(zip(DL, col)) for col in zip(*DL.values())]
    return result

@logger.log_function
def update_pdf_import_mapping(data, rp_items, account_selection, label_selection):
    """
    2nd process of PDF file import which is cropping the required statement detail part and then mapping accordingly.

    Parameters:
        data (dataframe/pdfplumber.PDF): The dataframe or PDF object to be updated with the mapping.
        rp_items (list of dict): The list of column headers mapping from user's input.
        account_selection (int): The selected account dropdown value requiring extra mapping.
        label_selection (int): The selected label dropdown value requiring extra mapping.

    Returns:
        df (dataframe): Processed dataframe.
    """
    df = anvil.server.call('update_pdf_mapping', data=data, mapping=rp_items, account=account_selection, labels=label_selection)
    logger.trace("df=", df)
    return df