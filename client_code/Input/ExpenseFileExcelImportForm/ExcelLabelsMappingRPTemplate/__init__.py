from ._anvil_designer import ExcelLabelsMappingRPTemplateTemplate
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

class ExcelLabelsMappingRPTemplate(ExcelLabelsMappingRPTemplateTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        # Any code you write here will run before the form opens.
        self.dropdown_lbl_action.items = cache.labels_mapping_action_dropdown()
        self.dropdown_lbl_map_to.items = cache.labels_dropdown()
        self.hidden_lbl_action.text = None
        self.input_label.visible = False

        # Prefill "labels map to" dropdown by finding high proximity choices
        self.dropdown_lbl_map_to.selected_value = repr(self.item['tgtlbl']) if self.item['tgtlbl'] is not None else None

    def dropdown_lbl_action_show(self, **event_args):
        """This method is called when the DropDown is shown on the screen"""
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
            self.parent.raise_event('x-refresh-label-cache')

    @logger.log_function
    def dropdown_lbl_action_change(self, **event_args):
        """This method is called when an item is selected"""
        self.dropdown_lbl_action_show()
        action, action_desc = self.dropdown_lbl_action.selected_value if self.dropdown_lbl_action.selected_value is not None else [None, None]
        prev = self.hidden_lbl_action.text
        self.hidden_lbl_action.text = action
        self.parent.raise_event('x-handle-action-count', action=action, prev=prev)
