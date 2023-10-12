import anvil.server
import anvil.users
from ..Entities.StockJournalGroup import StockJournalGroup
from ..Utils.Constants import CacheKey, LoggingLevel
from ..Utils.Logger import ClientLogger

# This is a module.
# You can define variables and functions here, and use them from any form. For example, in a top-level form:

logger = ClientLogger()

@logger.log_function
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

@logger.log_function
def get_stock_journal_group(group_dropdown_selected):
    """
    Return the stock journal group object of the selected stock journal group.

    Parameters:
        group_dropdown_selected (list): The selected value in list from the broker dropdown.

    Returns:
        jrn_grp_obj (StockJournalGroup): A stock journal group object.
    """
    from . import UserSettingController
    blank_jrn_grp = StockJournalGroup()
    jrn_grp_id, _ = group_dropdown_selected if group_dropdown_selected else [None, None]
    logger.trace(f'jrn_grp_id={jrn_grp_id}')
    jrn_grp_obj = anvil.server.call('select_stock_journal_group', jrn_grp_id) if jrn_grp_id else blank_jrn_grp.set_broker(UserSettingController.get_user_settings().get_broker())
    logger.trace(f'jrn_grp_obj={jrn_grp_obj}')
    return jrn_grp_obj

def enable_stock_journal_group_submit_button(jrn_grp_dropdown_selected):
    """
    Enable or disable the stock journal group submit button.

    Parameters:
        jrn_grp_dropdown_selected (list): The selected value in list from the stock journal group dropdown.

    Returns:
        Boolean: True for enable, false for disable.
    """
    jrn_grp_id = jrn_grp_dropdown_selected[0] if isinstance(jrn_grp_dropdown_selected, (list, tuple)) else jrn_grp_dropdown_selected
    return False if str(jrn_grp_id) in (None, '') or str(jrn_grp_id).isspace() else True

