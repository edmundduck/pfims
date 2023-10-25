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

    def button_1_click(self, **event_args):
        """This method is called when the button is clicked"""
        self.drop_down_1.items = cache.get_cache()
