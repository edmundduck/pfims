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
        logger.debug("self.dropdown_col_map_to.selected_value=", self.dropdown_col_map_to.selected_value)
        if self.dropdown_col_map_to.selected_value is not None and self.dropdown_col_map_to.selected_value[0] == const.ExpenseDBTableDefinion.Amount:
            self.dropdown_sign.visible = True
        else:
            self.dropdown_sign.visible = False

    def cb_required_change(self, **event_args):
        """This method is called when this checkbox is checked or unchecked"""
        if self.cb_required.checked == True:
            self.dropdown_col_map_to.visible = True
        else:    
            self.dropdown_col_map_to.selected_value = None
            self.dropdown_col_map_to.visible = False
            self.dropdown_sign.visible = False


