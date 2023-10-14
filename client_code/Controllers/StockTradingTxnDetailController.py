import anvil.server
import anvil.users
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
    cache = ClientCache(CacheKey.DD_STOCK_JRN_GRP, cache_data)
    if cache.is_empty():
        rows = anvil.server.call('generate_draftring_stock_journal_groups_list')
        new_dropdown = list((''.join([r['template_name'], ' [', str(r['template_id']), ']']), (r['template_id'], r['template_name'])) for r in rows)
        cache.set_cache(new_dropdown)
    return cache.get_cache()

@logger.log_function
def __get_stock_journal_group__(group_dropdown_selected):
    """
    Return the stock journal group object of the selected stock journal group.

    Parameters:
        group_dropdown_selected (list): The selected value in list from the broker dropdown.

    Returns:
        jrn_grp (StockJournalGroup): A stock journal group object.
    """
    from ..Utils.ClientCache import ClientCache
    jrn_grp_id, _ = group_dropdown_selected if group_dropdown_selected else [None, None]
    cache = ClientCache(CacheKey.OBJ_STOCK_JRN_GRP, None)
    if jrn_grp_id:
        if not cache.is_empty() and cache.get_cache().get(jrn_grp_id, None):
            jrn_grp = cache.get_cache().get(jrn_grp_id, None)
        else:
            jrn_grp = anvil.server.call('select_stock_journal_group', jrn_grp_id)
            jrn_list = anvil.server.call('select_stock_journals', jrn_grp_id)
            jrn_grp = jrn_grp.set_journals(jrn_list)
            cache.set_cache({jrn_grp_id: jrn_grp})
            logger.trace(f'jrn_grp_id={jrn_grp_id} / jrn_grp={jrn_grp} / journals={list(str(j) for j in jrn_grp.get_journals()) if jrn_grp.get_journals() else []}')
    else:
        from . import UserSettingController
        from ..Entities.StockJournalGroup import StockJournalGroup
        blank_jrn_grp = StockJournalGroup()
        jrn_grp = blank_jrn_grp.set_broker(UserSettingController.get_user_settings().get_broker())
        logger.trace(f'jrn_grp_id={jrn_grp_id} / blank_jrn_grp={blank_jrn_grp}')
    return jrn_grp

@logger.log_function
def get_group_name(group_dropdown_selected):
    """
    Return the stock journal group name of the selected stock journal group.

    Parameters:
        group_dropdown_selected (list): The selected value in list from the broker dropdown.

    Returns:
        jrn_grp.get_name (string): Selected stock journal group's name.
    """
    jrn_grp = __get_stock_journal_group__(group_dropdown_selected)
    return jrn_grp.get_name()

@logger.log_function
def get_journals(group_dropdown_selected):
    """
    Return all journals under the selected stock journal group.

    Parameters:
        group_dropdown_selected (list): The selected value in list from the broker dropdown.

    Returns:
        jrn_grp.get_serialized_journals (string): Selected stock journal group's journals in serialized form for frontend.
    """
    jrn_grp = __get_stock_journal_group__(group_dropdown_selected)
    return list(j.get_dict() for j in jrn_grp.get_journals()) if jrn_grp.get_journals() else []

def get_stock_journal_group_dropdown_selected_item(group_dropdown_selected):
    """
    Return a complete key based on a partial broker ID which is a part of the key in a dropdown list.

    Parameters:
        group_dropdown_selected (list): The selected value in list from the broker dropdown.

    Returns:
        selected_item (list): Complete key of the selected item in broker dropdown.
    """
    from ..Utils.ClientCache import ClientCache
    jrn_grp_dropdown = ClientCache(CacheKey.DD_STOCK_JRN_GRP, None)
    jrn_grp = __get_stock_journal_group__(group_dropdown_selected)
    if jrn_grp_dropdown.is_empty():
        generate_stock_journal_groups_dropdown()
    selected_item = jrn_grp_dropdown.get_complete_key(jrn_grp.get_broker())
    return selected_item

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

def save_stock_journal_group(jrn_grp_dropdown_selected, jrn_grp_name, broker_dropdown_selected, journals):
    """
    Convert the fields from the form for saving the stock journal group change in backend.

    Parameters:
        jrn_grp_dropdown_selected (list): The selected value in list from the stock journal group dropdown.
        jrn_grp_name (string): The name of the selected stock journal group.
        broker_dropdown_selected (list): The selected value in list from the broker dropdown.
        journals (list): A list of journals from repeating panel to be inserted or updated.
        
    Returns:
        result (list): A list of all functions return required by the save.
    """
    from datetime import date, datetime
    from ..Entities.StockJournal import StockJournal
    from ..Entities.StockJournalGroup import StockJournalGroup
    from ..Utils.ClientCache import ClientCache
    cache = ClientCache(const.CacheKey.STOCK_INPUT_DEL_IID, None)

    # Reflect updates in the row first
    # *** ESSENTIAL ***
    # Update child items from repeating panel to parent form items
    # Refer to the following reference links for detail
    # https://anvil.works/forum/t/is-it-possible-to-access-a-repeating-panels-methods-from-the-parent-form/3028/2
    # https://anvil.works/forum/t/refresh-data-bindings-when-any-key-in-self-items-changes/1141/3
    # https://anvil.works/forum/t/repeating-panel-to-collect-new-information/356/3
    self.input_repeating_panel.items = [c.input_data_panel_readonly.item for c in self.input_repeating_panel.get_components()]

    jrn_grp_id_ori, jrn_grp_name_ori = jrn_grp_dropdown_selected if jrn_grp_dropdown_selected is not None else [None, None]
    broker_id, _, _ = broker_dropdown_selected if broker_dropdown_selected is not None else [None, None, None]

    currenttime = datetime.now()
    jrn_grp = StockJournalGroup()
    jrn_grp = jrn_grp.set_id(jrn_grp_id_ori).set_name(jrn_grp_name).set_broker(broker_id).set_journals(journals)

    if not jrn_grp_id_ori:
        jrn_grp = jrn_grp.set_submitted_status(False).set_created_time(currenttime).set_lastsaved_time(currenttime)
        jrn_grp = anvil.server.call('proc_save_group_and_journals', jrn_grp)
    if not jrn_grp:
        raise RuntimeError(f"Error occurs in proc_save_group_and_journals.")
    else:
        logger.trace('jrn_grp=', jrn_grp)
        cache.clear_cache()
    return jrn_grp
