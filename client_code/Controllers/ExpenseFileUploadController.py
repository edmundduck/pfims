import anvil.server
from ..Utils.Constants import CacheKey

# This is a module.
# You can define variables and functions here, and use them from any form. For example, in a top-level form:

@logger.log_function
def generate_file_mapping_type_dropdown(data=None, reload=False):
    """
    Access reference data - file mapping type dropdown from either client cache or generate from DB data returned from server side.

    Parameters:
        data (list of RealRowDict): Optional. The data list returned from the DB table to replace the client cache, should the client cache not already contain the data.
        reload (Boolean): Optional. True if clear cache is required. False by default.

    Returns:
        cache.get_cache (list): File mapping type dropdown formed by import file type DB table data.
    """
    from ..Utils.ClientCache import ClientCache
    cache_data = list((r['name'], [r['id'], r['name']]) for r in data) if data else None
    cache = ClientCache(CacheKey.DD_IMPORT_FILE_TYPE, cache_data)
    if reload:
        cache.clear_cache()
    if cache.is_empty():
        rows = anvil.server.call('generate_mapping_type_dropdown')
        new_dropdown = list((r['name'], [r['id'], r['name']]) for r in rows)
        cache.set_cache(new_dropdown)
    return cache.get_cache()
