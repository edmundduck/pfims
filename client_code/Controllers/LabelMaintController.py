import anvil.server
import anvil.users
from ..Utils.Constants import CacheKey
from ..Utils.Logger import ClientLogger

# This is a module.
# You can define variables and functions here, and use them from any form. For example, in a top-level form:

logger = ClientLogger()

@logger.log_function
def generate_labels_dropdown(data=None, reload=False):
    """
    Access labels dropdown from either client cache or generate from DB data returned from server side.

    Parameters:
        data (list of RealRowDict): Optional. The data list returned from the DB table to replace the client cache, should the client cache not already contain the data.
        reload (Boolean): Optional. True if clear cache is required. False by default.

    Returns:
        cache.get_cache (list): Labels dropdown formed by labels DB table data.
    """
    from ..Utils.ClientCache import ClientCache
    cache_data = list((r['name'] + " (" + str(r['id']) + ")", (r['id'], r['name'])) for r in data) if data else None
    cache = ClientCache(CacheKey.DD_LABEL, cache_data)
    if reload:
        cache.clear_cache()
    if cache.is_empty():
        rows = anvil.server.call('generate_labels_list')
        new_dropdown = list((r['name'] + " (" + str(r['id']) + ")", (r['id'], r['name'])) for r in rows)
        cache.set_cache(new_dropdown)
    return cache.get_cache()

def get_label_dropdown_selected_item(lbl_id):
    """
    Return a complete key based on a partial label ID which is a part of the key in a dropdown list.

    Parameters:
        lbl_id (int): The label ID.

    Returns:
        selected_item (list): Complete key of the selected item in label dropdown.
    """
    from ..Utils.ClientCache import ClientCache
    cache = ClientCache(CacheKey.DD_LABEL, None)
    if cache.is_empty():
        generate_labels_dropdown()
    selected_item = cache.get_complete_key(lbl_id)
    return selected_item

@logger.log_function
def __get_label__(label_dropdown_selected, reload=False):
    """
    Return the label object of the selected label.

    Parameters:
        label_dropdown_selected (list): The selected value in list from the label dropdown.
        reload (Boolean): Optional. True if clear cache is required. False by default.

    Returns:
        lbl (Label): Label object corresponding to the selected label ID.
    """
    from ..Utils.ClientCache import ClientCache
    lbl_id, _ = label_dropdown_selected if label_dropdown_selected else [None, None]
    cache = ClientCache(CacheKey.OBJ_LABEL, None)
    if not reload and not cache.is_empty() and cache.get_cache().get(lbl_id, None):
        lbl = cache.get_cache().get(lbl_id, None)
    else:
        lbl = anvil.server.call('select_label', lbl_id)
        cache.set_cache({lbl_id: lbl})
        logger.trace(f'lbl_id={lbl.get_id()} / lbl={str(lbl)}')
    return lbl

def enable_label_update_button(label_selection):
    """
    Enable or disable the label update button.

    Parameters:
        label_selection (list): The selected value in list from the label dropdown.
        
    Returns:
        Boolean: True for enable, false for disable.
    """
    label_id = label_selection[0] if isinstance(label_selection, (list, tuple)) else label_selection
    return False if label_id in (None, '') or str(label_id).isspace() else True

def enable_label_delete_button(label_selection):
    """
    Enable or disable the label delete button.

    Parameters:
        label_selection (list): The selected value in list from the label dropdown.
        
    Returns:
        Boolean: True for enable, false for disable.
    """
    label_id = label_selection[0] if isinstance(label_selection, (list, tuple)) else label_selection
    return False if label_id in (None, '') or str(label_id).isspace() else True

