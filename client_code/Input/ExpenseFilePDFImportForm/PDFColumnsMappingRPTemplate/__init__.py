from ._anvil_designer import PDFColumnsMappingRPTemplateTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from ....Utils import Caching as cache
from ....Utils import Constants as const
from ....Utils.Logger import ClientLogger

logger = ClientLogger()

class PDFColumnsMappingRPTemplate(PDFColumnsMappingRPTemplateTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        # Any code you write here will run before the form opens.
        self.dropdown_col_map_to.items = cache.expense_tbl_def_dropdown()
        self.dropdown_sign.visible = False

    def dropdown_col_map_to_change(self, **event_args):
        """This method is called when an item is selected"""
        if self.dropdown_col_map_to.selected_value == const.ExpenseDBTableDefinion.Amount:
            self.dropdown_sign.visible = True
        else:
            self.dropdown_sign.visible = False

