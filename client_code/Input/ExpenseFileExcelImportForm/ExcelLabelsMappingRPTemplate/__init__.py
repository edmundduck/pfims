from ._anvil_designer import ExcelLabelsMappingRPTemplateTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from ....Utils.ClientCache import ClientCache
from ....Utils import Constants as const
from ....Utils.Logger import ClientLogger

logger = ClientLogger()

class ExcelLabelsMappingRPTemplate(ExcelLabelsMappingRPTemplateTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        # Any code you write here will run before the form opens.
        cache_lbl_action = ClientCache('generate_labels_mapping_action_dropdown')
        cache_labels = ClientCache('generate_labels_dropdown')
        self.dropdown_lbl_action.items = cache_lbl_action.get_cache()
        self.dropdown_lbl_map_to.items = cache_labels.get_cache()
        self.dropdown_lbl_map_to.visible = False
        self.hidden_lbl_action.text = None
        self.input_label.visible = False

        # Prefill "labels map to" dropdown by finding high proximity choices
        self.dropdown_lbl_map_to.selected_value = self.item['tgtlbl'] if self.item['tgtlbl'] is not None else None
        self.add_event_handler('x-apply-action-to-all-labels', self.apply_action_to_all_labels)

    @logger.log_function
    def dropdown_lbl_action_change(self, **event_args):
        """This method is called when an item is selected"""
        action, action_desc = self.dropdown_lbl_action.selected_value if self.dropdown_lbl_action.selected_value is not None else [None, None]
        if action in (None, const.FileImportLabelExtraAction.SKIP):
            self.dropdown_lbl_map_to.visible = False
            self.input_label.visible = False
        elif action == const.FileImportLabelExtraAction.MAP:
            self.dropdown_lbl_map_to.visible = True
            self.input_label.visible = False
        elif action == const.FileImportLabelExtraAction.CREATE:
            self.dropdown_lbl_map_to.visible = False
            self.input_label.visible = True
        prev = self.hidden_lbl_action.text
        self.hidden_lbl_action.text = action
        self.parent.raise_event('x-handle-action-count', action=action, prev=prev)

    def apply_action_to_all_labels(self, action, **event_args):
        cache_lbl_action = ClientCache('generate_labels_mapping_action_dropdown')
        self.dropdown_lbl_action.selected_value = cache_lbl_action.get_complete_key(action)
        self.item['action'] = cache_lbl_action.get_complete_key(action)
        self.dropdown_lbl_action_change()
