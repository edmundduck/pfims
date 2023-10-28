import anvil.server
import anvil.users
from ..Utils.Constants import CacheKey
from ..Utils.Logger import ClientLogger

# This is a module.
# You can define variables and functions here, and use them from any form. For example, in a top-level form:

logger = ClientLogger()

@logger.log_function
def generate_labels_dropdown(reload=False):
    """
    Access labels dropdown from either client cache or generate from DB data returned from server side.

    Parameters:
        reload (Boolean): Optional. True if clear cache is required. False by default.

    Returns:
        cache.get_cache (list): Labels dropdown formed by labels DB table data.
    """
    from ..Utils.ClientCache import ClientDropdownCache
    cache = ClientDropdownCache(CacheKey.DD_LABEL)
    if reload:
        cache.clear_cache()
    return cache.get_cache()

def get_label_dropdown_selected_item(lbl_id):
    """
    Return a complete key based on a partial label ID which is a part of the key in a dropdown list.

    Parameters:
        lbl_id (int): The label ID.

    Returns:
        selected_item (list): Complete key of the selected item in label dropdown.
    """
    from ..Utils.ClientCache import ClientDropdownCache
    cache = ClientDropdownCache(CacheKey.DD_LABEL)
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
    cache = ClientCache(CacheKey.OBJ_LABEL)
    if not reload and not cache.is_empty() and cache.get_cache().get(lbl_id, None):
        lbl = cache.get_cache().get(lbl_id, None)
    else:
        lbl = anvil.server.call('select_label', lbl_id)
        cache.set_cache({lbl_id: lbl})
        logger.trace(f'lbl_id={lbl.get_id()} / lbl={str(lbl)}')
    return lbl

def get_label_name(label_dropdown_selected, reload=False):
    """
    Return the label name of the selected label.

    Parameters:
        label_dropdown_selected (list): The selected value in list from the label dropdown.
        reload (Boolean): Optional. True if clear cache is required. False by default.

    Returns:
        lbl.get_name (string): Selected label's name.
    """
    lbl = __get_label__(label_dropdown_selected, reload)
    return lbl.get_name()

def get_label_status(label_dropdown_selected, reload=False):
    """
    Return the label status of the selected label.

    Parameters:
        label_dropdown_selected (list): The selected value in list from the label dropdown.
        reload (Boolean): Optional. True if clear cache is required. False by default.

    Returns:
        lbl.get_status (date): Selected label's status.
    """
    lbl = __get_label__(label_dropdown_selected, reload)
    if lbl.get_status() is None:
        lbl = lbl.set_status(True)
    return lbl.get_status()

def get_label_keywords(label_dropdown_selected, reload=False):
    """
    Return the label keywords of the selected label.

    Parameters:
        label_dropdown_selected (list): The selected value in list from the label dropdown.
        reload (Boolean): Optional. True if clear cache is required. False by default.

    Returns:
        lbl.get_keywords (list of string): Selected label's keywords.
    """
    lbl = __get_label__(label_dropdown_selected, reload)
    return lbl.get_keywords()

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

@logger.log_function
def create_label(lbl_name, keywords, status):
    """
    Convert the fields from the form for creating the label change in backend.

    Parameters:
        lbl_name (string): The name of the selected label.
        keywords (list of string): The selected keywords in list from the label dropdown.
        status (string): The status of the selected label.
        
    Returns:
        lbl (Label): An label object.
    """
    from .. import Global
    from ..Entities.Label import Label
    from ..Utils.ClientCache import ClientCache
    cache = ClientCache(CacheKey.OBJ_LABEL)

    lbl = Label().set_user_id(Global.userid).set_name(lbl_name).set_keywords(keywords).set_status(status)
    id_list = anvil.server.call('create_label', lbl)
    if not id_list or len(id_list) == 0:
        raise RuntimeError(f"Error occurs in create_label.")
    else:
        id = id_list[0]
        logger.trace('id=', id)
        lbl = lbl.set_id(id)
        cache.set_cache({id: lbl})
    return lbl

@logger.log_function
def update_label(label_dropdown_selected, lbl_name, keywords, status):
    """
    Convert the fields from the form for updating the label change in backend.

    Parameters:
        label_dropdown_selected (list): The selected value in list from the label dropdown.
        lbl_name (string): The name of the selected label.
        keywords (list of string): The selected keywords in list from the label dropdown.
        status (string): The status of the selected label.
        
    Returns:
        lbl (Label): An label object.
    """
    from .. import Global
    from ..Entities.Label import Label
    from ..Utils.ClientCache import ClientCache
    cache = ClientCache(CacheKey.OBJ_LABEL)

    lbl_id, _ = label_dropdown_selected if label_dropdown_selected is not None else [None, None]
    lbl = Label().set_user_id(Global.userid).set_id(lbl_id).set_name(lbl_name).set_keywords(keywords).set_status(status)
    result = anvil.server.call('update_label', lbl)
    if not result:
        raise RuntimeError(f"Error occurs in update_label.")
    else:
        logger.trace('result=', result)
        cache.set_cache({lbl.get_id(): lbl})
    return lbl

@logger.log_function
def delete_label(label_dropdown_selected):
    """
    Convert the fields from the form for deleting the label change in backend.

    Parameters:
        label_dropdown_selected (list): The selected value in list from the label dropdown.
        
    Returns:
        result (int): Successful delete row count, otherwise None.
    """
    from .. import Global
    from ..Entities.Label import Label
    from ..Utils.ClientCache import ClientCache
    cache = ClientCache(CacheKey.OBJ_LABEL)

    lbl_id, lbl_name = label_dropdown_selected if label_dropdown_selected is not None else [None, None]
    lbl = Label().set_user_id(Global.userid).set_id(lbl_id).set_name(lbl_name)
    result = anvil.server.call('delete_label', lbl)
    if not result:
        raise RuntimeError(f"Error occurs in delete_label.")
    else:
        logger.trace('result=', result)
        cache.clear_cache()
    return result
