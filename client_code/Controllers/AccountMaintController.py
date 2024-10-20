import anvil.server
from ..Utils.Constants import CacheKey
from ..Utils.Logger import ClientLogger

# This is a module.
# You can define variables and functions here, and use them from any form. For example, in a top-level form:

logger = ClientLogger()

@logger.log_function
def generate_accounts_dropdown(reload=False):
    """
    Access accounts dropdown from either client cache or generate from DB data returned from server side.

    Parameters:
        reload (Boolean): Optional. True if clear cache is required. False by default.

    Returns:
        cache.get_cache (list): Accounts dropdown formed by accounts DB table data.
    """
    from ..Utils.ClientCache import ClientDropdownCache
    cache = ClientDropdownCache(CacheKey.DD_ACCOUNT)
    if reload:
        cache.clear_cache()
    return cache.get_cache()

def generate_currency_dropdown():
    """
    Access currency dropdown from either client cache or generate from DB data returned from server side.

    Returns:
        cache.get_cache (list): Currency dropdown formed by currency DB table data.
    """
    from . import UserSettingController
    return UserSettingController.generate_currency_dropdown()

def get_account_dropdown_selected_item(acct_id):
    """
    Return a complete key based on a partial account ID which is a part of the key in a dropdown list.

    Parameters:
        acct_id (int): The account ID.

    Returns:
        selected_item (list): Complete key of the selected item in account dropdown.
    """
    from ..Utils.ClientCache import ClientDropdownCache
    cache = ClientDropdownCache(CacheKey.DD_ACCOUNT)
    selected_item = cache.get_complete_key(acct_id)
    return selected_item

def get_currency_dropdown_selected_item(ccy):
    """
    Return a complete key based on a partial currency ID which is a part of the key in a dropdown list.

    Parameters:
        ccy (string): The currency abbreviation.

    Returns:
        selected_item (list): Complete key of the selected item in currency dropdown.
    """
    from ..Utils.ClientCache import ClientDropdownCache
    cache = ClientDropdownCache(CacheKey.DD_CURRENCY)
    selected_item = cache.get_complete_key(ccy)
    return selected_item

@logger.log_function
def __get_account__(account_dropdown_selected, reload=False):
    """
    Return the account object of the selected account.

    Parameters:
        account_dropdown_selected (list): The selected value in list from the account dropdown.
        reload (Boolean): Optional. True if clear cache is required. False by default.

    Returns:
        acct (Account): Account object corresponding to the selected account ID.
    """
    from ..Utils.ClientCache import ClientCache
    acct_id = account_dropdown_selected[0] if account_dropdown_selected and len(account_dropdown_selected) > 0 else None
    cache = ClientCache(CacheKey.OBJ_ACCOUNT)
    if not reload and not cache.is_empty() and not cache.is_expired() and cache.get_cache().get(acct_id, None):
        acct = cache.get_cache().get(acct_id, None)
    else:
        acct = anvil.server.call('select_account', acct_id)
        cache.set_cache({acct_id: acct})
        logger.trace(f'acct_id={acct.get_id()} / acct={str(acct)}')
    return acct

def get_account_name(account_dropdown_selected, reload=False):
    """
    Return the account name of the selected account.

    Parameters:
        account_dropdown_selected (list): The selected value in list from the account dropdown.
        reload (Boolean): Optional. True if clear cache is required. False by default.

    Returns:
        acct.get_name (string): Selected account's name.
    """
    acct = __get_account__(account_dropdown_selected, reload)
    return acct.get_name()

def get_account_base_currency(account_dropdown_selected, reload=False):
    """
    Return the account base currency of the selected account.

    Parameters:
        account_dropdown_selected (list): The selected value in list from the account dropdown.
        reload (Boolean): Optional. True if clear cache is required. False by default.

    Returns:
        acct.get_base_currency (string): Selected account's base currency.
    """
    acct = __get_account__(account_dropdown_selected, reload)
    return acct.get_base_currency()

def get_account_valid_from_date(account_dropdown_selected, reload=False):
    """
    Return the account valid from date of the selected account.

    Parameters:
        account_dropdown_selected (list): The selected value in list from the account dropdown.
        reload (Boolean): Optional. True if clear cache is required. False by default.

    Returns:
        acct.get_valid_datefrom (date): Selected account's valid from date.
    """
    acct = __get_account__(account_dropdown_selected, reload)
    return acct.get_valid_datefrom()

def get_account_valid_to_date(account_dropdown_selected, reload=False):
    """
    Return the account valid to date of the selected account.

    Parameters:
        account_dropdown_selected (list): The selected value in list from the account dropdown.
        reload (Boolean): Optional. True if clear cache is required. False by default.

    Returns:
        acct.get_valid_dateto (date): Selected account's valid to date.
    """
    acct = __get_account__(account_dropdown_selected, reload)
    return acct.get_valid_dateto()

def get_account_status(account_dropdown_selected, reload=False):
    """
    Return the account status of the selected account.

    Parameters:
        account_dropdown_selected (list): The selected value in list from the account dropdown.
        reload (Boolean): Optional. True if clear cache is required. False by default.

    Returns:
        acct.get_status (date): Selected account's status.
    """
    acct = __get_account__(account_dropdown_selected, reload)
    if acct.get_status() is None:
        acct = acct.set_status(True)
    return acct.get_status()

def enable_account_update_button(account_selection):
    """
    Enable or disable the account update button.

    Parameters:
        account_selection (list): The selected value in list from the account dropdown.
        
    Returns:
        Boolean: True for enable, false for disable.
    """
    account_id = account_selection[0] if isinstance(account_selection, (list, tuple)) else account_selection
    return False if account_id in (None, '') or str(account_id).isspace() else True

def enable_account_delete_button(account_selection):
    """
    Enable or disable the account delete button.

    Parameters:
        account_selection (list): The selected value in list from the account dropdown.
        
    Returns:
        Boolean: True for enable, false for disable.
    """
    account_id = account_selection[0] if isinstance(account_selection, (list, tuple)) else account_selection
    return False if account_id in (None, '') or str(account_id).isspace() else True

@logger.log_function
def create_account(acct_name, currency_dropdown_selected, date_validfrom, date_validto, status):
    """
    Convert the fields from the form for creating the account change in backend.

    Parameters:
        acct_name (string): The name of the selected account.
        currency_dropdown_selected (list): The selected value in list from the currency dropdown.
        date_validfrom (date): The valid from date of the selected account.
        date_validto (date): The valid to date of the selected account.
        status (string): The status of the selected account.
        
    Returns:
        acct (Account): An account object.
    """
    from .. import Global
    from ..Entities.Account import Account
    from ..Utils.ClientCache import ClientCache
    cache = ClientCache(CacheKey.OBJ_ACCOUNT)

    ccy = currency_dropdown_selected if currency_dropdown_selected is not None else None
    acct = Account().set_user_id(Global.userid).set_name(acct_name).set_base_currency(ccy).set_valid_datefrom(date_validfrom).set_valid_dateto(date_validto).set_status(status)
    id = anvil.server.call('create_account', acct)
    if not id:
        raise RuntimeError(f"Error occurs in create_account.")
    else:
        logger.trace('id=', id)
        acct = acct.set_id(id)
        cache.set_cache({acct.get_id(): acct})
    return acct

@logger.log_function
def update_account(account_dropdown_selected, acct_name, currency_dropdown_selected, date_validfrom, date_validto, status):
    """
    Convert the fields from the form for updating the account change in backend.

    Parameters:
        account_dropdown_selected (list): The selected value in list from the account dropdown.
        acct_name (string): The name of the selected account.
        currency_dropdown_selected (list): The selected value in list from the currency dropdown.
        date_validfrom (date): The valid from date of the selected account.
        date_validto (date): The valid to date of the selected account.
        status (string): The status of the selected account.
        
    Returns:
        acct (Account): An account object.
    """
    from .. import Global
    from ..Entities.Account import Account
    from ..Utils.ClientCache import ClientCache
    cache = ClientCache(CacheKey.OBJ_ACCOUNT)

    acct_id, _ = account_dropdown_selected if account_dropdown_selected is not None else [None, None]
    ccy = currency_dropdown_selected if currency_dropdown_selected is not None else None
    acct = Account().set_user_id(Global.userid).set_id(acct_id).set_name(acct_name).set_base_currency(ccy).set_valid_datefrom(date_validfrom).set_valid_dateto(date_validto).set_status(status)
    result = anvil.server.call('update_account', acct)
    if not result:
        raise RuntimeError(f"Error occurs in update_account.")
    else:
        logger.trace('result=', result)
        cache.set_cache({acct.get_id(): acct})
    return acct

@logger.log_function
def delete_account(account_dropdown_selected):
    """
    Convert the fields from the form for deleting the account change in backend.

    Parameters:
        account_dropdown_selected (list): The selected value in list from the account dropdown.
        
    Returns:
        result (int): Successful delete row count, otherwise None.
    """
    from .. import Global
    from ..Entities.Account import Account
    from ..Utils.ClientCache import ClientCache
    cache = ClientCache(CacheKey.OBJ_ACCOUNT)

    acct_id, acct_name = account_dropdown_selected if account_dropdown_selected is not None else [None, None]
    acct = Account().set_user_id(Global.userid).set_id(acct_id).set_name(acct_name)
    result = anvil.server.call('delete_account', acct)
    if not result:
        raise RuntimeError(f"Error occurs in delete_account.")
    else:
        logger.trace('result=', result)
        cache.clear_cache()
    return result
