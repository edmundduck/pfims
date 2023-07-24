from ._anvil_designer import UploadMappingRulesFormTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from ...Utils import Routing
from ...Utils.Logging import trace, debug, info, warning, error, critical

class UploadMappingRulesForm(UploadMappingRulesFormTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        # Any code you write here will run before the form opens.
        self.repeating_panel_1.add_event_handler('x-reload-rp', self.reload_rp_data)
        mappings = anvil.server.call('select_mapping_rules')
        self.repeating_panel_1.items = mappings if mappings not in (None, '', []) else [{} for i in range(1)]

    def button_create_mapping_click(self, **event_args):
        """This method is called when the button is clicked"""
        self.repeating_panel_1.items = [{} for i in range(1)] + self.repeating_panel_1.items 

    @debug.log_function
    def button_file_import_click(self, **event_args):
        """This method is called when the button is clicked"""
        Routing.open_exp_file_upload_form(self)

    @debug.log_function
    def reload_rp_data(self, del_id=None, **event_args):
        for d in self.repeating_panel_1.get_components(): trace.log("reload_rp_data d.item=", d.item)
        # This doesn't work
        #self.repeating_panel_1.items = [c for c in self.repeating_panel_1.items if c['id'] != del_id]
        self.repeating_panel_1.items = [c.item for c in self.repeating_panel_1.get_components() if c.item['id'] != del_id]