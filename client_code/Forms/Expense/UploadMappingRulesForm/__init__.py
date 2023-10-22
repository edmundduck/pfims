from ._anvil_designer import UploadMappingRulesFormTemplate
from anvil import *
from ....Controllers import UploadMappingRulesController
from ....Utils.Logger import ClientLogger

logger = ClientLogger()

class UploadMappingRulesForm(UploadMappingRulesFormTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        # Any code you write here will run before the form opens.
        self.repeating_panel_1.add_event_handler('x-reload-rp', self.reload_rp_data)
        self.repeating_panel_1.items = UploadMappingRulesController.populate_repeating_panel_items()

    def button_create_mapping_click(self, **event_args):
        """This method is called when the button is clicked"""
        self.repeating_panel_1.items = UploadMappingRulesController.populate_repeating_panel_items(self.repeating_panel_1.items)

    @logger.log_function
    def button_file_import_click(self, **event_args):
        """This method is called when the button is clicked"""
        from ....Utils import Routing
        Routing.open_exp_file_upload_form(self)

    @logger.log_function
    def reload_rp_data(self, del_id=None, **event_args):
        self.repeating_panel_1.items = UploadMappingRulesController.populate_repeating_panel_items(self.repeating_panel_1.items, reload=True, del_iid=del_id)