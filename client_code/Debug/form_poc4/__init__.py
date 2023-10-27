from ._anvil_designer import form_poc4Template
from anvil import *
import anvil.server
from ...Utils.Logger import ClientLogger
from ...Utils.ClientCache import ClientCache
from ...Utils.Constants import CacheKey

logger = ClientLogger()
cache = ClientCache(CacheKey.DD_EXPENSE_TAB)

class form_poc4(form_poc4Template):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        # Any code you write here will run before the form opens.

    def button_generate_click(self, **event_args):
        """This method is called when the button is clicked"""
        self.drop_down_expense_tab.items = list((r['tab_name'] + " (" + str(r['tab_id']) + ")", [r['tab_id'], r['tab_name']]) for r in cache.get_cache())

    def button_clear_click(self, **event_args):
        """This method is called when the button is clicked"""
        self.drop_down_expense_tab.items = []

