import anvil.server
import anvil.users
from ..Utils.Constants import CacheKey, LoggingLevel

# This is a module.
# You can define variables and functions here, and use them from any form. For example, in a top-level form:

def generate_stock_journal_groups_dropdown(data=None, reload=False):
    """
    Access stock journal groups dropdown from either client cache or generate from DB data returned from server side.

    Parameters:
        data (list of RealRowDict): Optional. The data list returned from the DB table to replace the client cache, should the client cache not already contain the data.
        reload (Boolean): Optional. True if clear cache is required. False by default.

    Returns:
        cache.get_cache (list): Currency dropdown formed by currency DB table data.
    """
    from ..Utils.ClientCache import ClientCache
    cache_data = list((''.join([r['template_name'], ' [', str(r['template_id']), ']']), (r['template_id'], r['template_name'])) for r in data) if data else None
    cache = ClientCache(CacheKey.STOCK_JRN_GRP, cache_data)
    if cache.is_empty():
        rows = anvil.server.call('generate_draftring_stock_journal_groups_list')
        new_dropdown = list((''.join([r['template_name'], ' [', str(r['template_id']), ']']), (r['template_id'], r['template_name'])) for r in rows)
        cache.set_cache(new_dropdown)
    return cache.get_cache()

def get_stock_journal_group_broker(broker_dropdown_selected):
    """
    Return the broker ID of the selected stock journal group.

    Parameters:
        broker_dropdown_selected (list): The selected value in list from the broker dropdown.

    Returns:
        selected_item (list): Complete key of the selected item in broker dropdown.
    """
    from . import UserSettingController
    jrn_grp_id, _ = broker_dropdown_selected if broker_dropdown_selected else [None, None]
    jrn_grp_obj = anvil.server.call('get_stock_journal_group', jrn_grp_id) if jrn_grp_id else UserSettingController.get_user_settings().get_broker()
    selected_item = UserSettingController.get_broker_dropdown_selected_item(jrn_grp_obj.get_broker())
    return selected_item

