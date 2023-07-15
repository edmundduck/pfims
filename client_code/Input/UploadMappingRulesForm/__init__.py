from ._anvil_designer import UploadMappingRulesFormTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from ...Utils import Routing

class UploadMappingRulesForm(UploadMappingRulesFormTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        # Any code you write here will run before the form opens.
        mappings = anvil.server.call('select_mapping_rules')
        self.repeating_panel_1.items = mappings if mappings not in (None, '', []) else [{} for i in range(1)]

    def button_create_mapping_click(self, **event_args):
        """This method is called when the button is clicked"""
        self.repeating_panel_1.items = [{} for i in range(1)] + self.repeating_panel_1.items 

    def button_file_import_click(self, **event_args):
        """This method is called when the button is clicked"""
        Routing.open_exp_file_upload_form(self)
