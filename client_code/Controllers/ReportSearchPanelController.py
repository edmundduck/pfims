import anvil.server
from ..Utils.Constants import CacheKey
from ..Utils.Logger import ClientLogger

# This is a module.
# You can define variables and functions here, and use them from any form. For example, in a top-level form:

logger = ClientLogger()

@logger.log_function
def generate_search_interval_dropdown():
    """
    Access search interval dropdown from either client cache or generate from DB data returned from server side.

    Returns:
        cache.get_cache (list): Search interval dropdown formed by search interval DB table data.
    """
    from . import UserSettingController
    return UserSettingController.generate_search_interval_dropdown()

@logger.log_function
def generate_labels_dropdown(reload=False):
    """
    Access labels dropdown from either client cache or generate from DB data returned from server side.

    Parameters:
        reload (Boolean): Optional. True if clear cache is required. False by default.

    Returns:
        cache.get_cache (list): Labels dropdown formed by labels DB table data.
    """
    from . import LabelMaintController
    return LabelMaintController.generate_labels_dropdown(reload)
