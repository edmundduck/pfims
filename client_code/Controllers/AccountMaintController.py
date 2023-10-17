import anvil.server
from ..Utils.Constants import CacheKey
from ..Utils.Logger import ClientLogger

# This is a module.
# You can define variables and functions here, and use them from any form. For example, in a top-level form:

logger = ClientLogger()

@logger.log_function
def generate_accounts_dropdown(data=None, reload=False):
    """
    Access accounts dropdown from either client cache or generate from DB data returned from server side.

    Parameters:
        data (list of RealRowDict): Optional. The data list returned from the DB table to replace the client cache, should the client cache not already contain the data.
        reload (Boolean): Optional. True if clear cache is required. False by default.

    Returns:
        cache.get_cache (list): Accounts dropdown formed by accounts DB table data.
    """
    from ..Utils.ClientCache import ClientCache
    cache_data = list((r['name'] + " (" + str(r['id']) + ")", [r['id'], r['name']]) for r in data) if data else None
    cache = ClientCache(CacheKey.DD_ACCOUNT, cache_data)
    if reload:
        cache.clear_cache()
    if cache.is_empty():
        rows = anvil.server.call('generate_accounts_list')
        new_dropdown = list((r['name'] + " (" + str(r['id']) + ")", [r['id'], r['name']]) for r in rows)
        cache.set_cache(new_dropdown)
    return cache.get_cache()

def generate_currency_dropdown(data=None):
    """
    Access currency dropdown from either client cache or generate from DB data returned from server side.

    Parameters:
        data (list of RealRowDict): Optional. The data list returned from the DB table to replace the client cache, should the client cache not already contain the data.

    Returns:
        cache.get_cache (list): Currency dropdown formed by currency DB table data.
    """
    from . import UserSettingController
    return UserSettingController.generate_currency_dropdown(data)

def get_account_dropdown_selected_item(acct_id):
    """
    Return a complete key based on a partial account ID which is a part of the key in a dropdown list.

    Parameters:
        acct_id (int): The account ID.

    Returns:
        selected_item (list): Complete key of the selected item in account dropdown.
    """
    from ..Utils.ClientCache import ClientCache
    cache = ClientCache(CacheKey.DD_ACCOUNT, None)
    if cache.is_empty():
        generate_accounts_dropdown()
    selected_item = cache.get_complete_key(acct_id)
    return selected_item
