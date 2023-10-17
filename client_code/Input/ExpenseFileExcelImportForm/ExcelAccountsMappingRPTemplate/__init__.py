from ._anvil_designer import ExcelAccountsMappingRPTemplateTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from ....Controllers import ExpenseFileExcelImportController
from ....Utils.ClientCache import ClientCache
from ....Utils import Constants as const
from ....Utils.Logger import ClientLogger

logger = ClientLogger()

class ExcelAccountsMappingRPTemplate(ExcelAccountsMappingRPTemplateTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        # Any code you write here will run before the form opens.
        cache_acct_action = ClientCache('generate_labels_mapping_action_dropdown')
        self.dropdown_acct_action.items = cache_acct_action.get_cache()
        self.dropdown_acct_map_to.items = ExpenseFileExcelImportController.generate_accounts_dropdown()
        self.dropdown_acct_map_to.visible = False
        self.hidden_acct_action.text = None
        self.input_account.visible = False

        ### TO DO ###
        # Prefill "labels map to" dropdown by finding high proximity choices
        self.dropdown_acct_map_to.selected_value = self.item['tgtacct'] if self.item['tgtacct'] is not None else None
        self.add_event_handler('x-apply-action-to-all-accounts', self.apply_action_to_all_accounts)

    @logger.log_function
    def dropdown_acct_action_change(self, **event_args):
        """This method is called when an item is selected"""
        action, action_desc = self.dropdown_acct_action.selected_value if self.dropdown_acct_action.selected_value is not None else [None, None]
        if action in (None, const.FileImportLabelExtraAction.SKIP):
            self.dropdown_acct_map_to.visible = False
            self.input_account.visible = False
        elif action == const.FileImportLabelExtraAction.MAP:
            self.dropdown_acct_map_to.visible = True
            self.input_account.visible = False
        elif action == const.FileImportLabelExtraAction.CREATE:
            self.dropdown_acct_map_to.visible = False
            self.input_account.visible = True
        prev = self.hidden_acct_action.text
        self.hidden_acct_action.text = action
        self.parent.raise_event('x-handle-action-count', action=action, prev=prev)

    def apply_action_to_all_accounts(self, action, **event_args):
        cache_acct_action = ClientCache('generate_labels_mapping_action_dropdown')
        self.dropdown_acct_action.selected_value = cache_acct_action.get_complete_key(action)
        self.item['action'] = cache_acct_action.get_complete_key(action)
        self.dropdown_acct_action_change()
