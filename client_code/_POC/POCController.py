import anvil.server
from ..Utils.ClientCache import ClientCache
from ..Utils.Constants import CacheKey

# This is a module.
# You can define variables and functions here, and use them from any form. For example, in a top-level form:

DROPDOWN_MAPPPING = {
    CacheKey.DD_EXPENSE_TAB: ['generate_expense_groups_list', lambda d: list((r['tab_name'] + ' (' + str(r['tab_id']) + ')', [r['tab_id'], r['tab_name']]) for r in d)]
}
    
class DropdownCache(ClientCache):
    def get_cache(self):
        result = None
        mapping = DROPDOWN_MAPPPING.get(self.name, None)
        if mapping:
            func, transform = mapping
            if self.is_empty():
                result = transform(self.set_cache(anvil.server.call(func)))
            else:
                cache = super().get_cache()
                result = transform(cache)
        return result

def generate_dropdown():
    cache = DropdownCache(CacheKey.DD_EXPENSE_TAB)
    return cache.get_cache()
