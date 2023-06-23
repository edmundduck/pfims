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
        self.hidden_lbl_action.text = None

        # Prototype - lbl mapping dropdown pre-selection
        print(self.item['tgtlbl'])
        self.dropdown_lbl_map_to.selected_value = repr(self.item['tgtlbl'])

    def dropdown_lbl_action_show(self, **event_args):
        """This method is called when the DropDown is shown on the screen"""
        action = self.dropdown_lbl_action.selected_value.get('id') if isinstance(self.dropdown_lbl_action.selected_value, dict) else self.dropdown_lbl_action.selected_value
        if action in (None, 'S'):
            self.dropdown_lbl_map_to.visible = False
            self.input_label.visible = False
        elif action == 'M':
            self.dropdown_lbl_map_to.visible = True
            self.input_label.visible = False
        elif action == 'C':
            self.dropdown_lbl_map_to.visible = False
            self.input_label.visible = True

    def dropdown_lbl_action_change(self, **event_args):
        """This method is called when an item is selected"""
        self.dropdown_lbl_action_show()
        action = self.dropdown_lbl_action.selected_value.get('id') if isinstance(self.dropdown_lbl_action.selected_value, dict) else self.dropdown_lbl_action.selected_value
        prev = self.hidden_lbl_action.text
        self.hidden_lbl_action.text = action
        self.parent.raise_event('x-handle-action-count', action=action, prev=prev)
