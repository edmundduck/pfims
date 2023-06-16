from ._anvil_designer import LabelsMappingRPTemplateTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from ....App import Caching as cache

class LabelsMappingRPTemplate(LabelsMappingRPTemplateTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        # Any code you write here will run before the form opens.
        self.dropdown_lbl_action.items = cache.get_caching_labels_mapping_action_dropdown()
        self.dropdown_lbl_map_to.items = cache.get_caching_labels_dropdown()
        self.dropdown_lbl_action_change()

    def dropdown_lbl_action_change(self, **event_args):
        """This method is called when an item is selected"""
        if self.dropdown_lbl_action.selected_value in (None, 'S'):
            self.dropdown_lbl_map_to.visible = False
            self.input_label.visible = False
        elif self.dropdown_lbl_action.selected_value is 'M':
            self.dropdown_lbl_map_to.visible = True
            self.input_label.visible = False
        elif self.dropdown_lbl_action.selected_value is 'C':
            self.dropdown_lbl_map_to.visible = False
            self.input_label.visible = True