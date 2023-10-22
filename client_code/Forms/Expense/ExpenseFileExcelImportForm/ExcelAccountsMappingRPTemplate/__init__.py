from ._anvil_designer import ExcelAccountsMappingRPTemplateTemplate
from anvil import *
from .....Controllers import ExpenseFileExcelImportController
from .....Utils.Logger import ClientLogger

logger = ClientLogger()

class ExcelAccountsMappingRPTemplate(ExcelAccountsMappingRPTemplateTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        # Any code you write here will run before the form opens.
        self.dropdown_acct_action.items = ExpenseFileExcelImportController.generate_labels_mapping_action_dropdown()
        self.dropdown_acct_map_to.items = ExpenseFileExcelImportController.generate_accounts_dropdown()
        self.dropdown_acct_map_to.visible = False
        self.hidden_acct_action.text = None
        self.input_account.visible = False
        self.dropdown_acct_map_to.selected_value = self.item['tgtacct'] if self.item['tgtacct'] is not None else None
        self.add_event_handler('x-apply-action-to-all-accounts', self.apply_action_to_all_accounts)

    @logger.log_function
    def dropdown_acct_action_change(self, **event_args):
        """This method is called when an item is selected"""
        from .....Utils.Constants import FileImportLabelExtraAction
        
        action, _ = self.dropdown_acct_action.selected_value if self.dropdown_acct_action.selected_value is not None else [None, None]
        self.dropdown_acct_map_to.visible = ExpenseFileExcelImportController.visible_account_label_map_to_dropdown(self.dropdown_acct_action.selected_value)
        self.input_account.visible = ExpenseFileExcelImportController.visible_account_label_textfield(self.dropdown_acct_action.selected_value)
        prev = self.hidden_acct_action.text
        self.hidden_acct_action.text = action
        self.parent.raise_event('x-handle-action-count', action=action, prev=prev)

    def apply_action_to_all_accounts(self, action, **event_args):
        self.dropdown_acct_action.selected_value = ExpenseFileExcelImportController.get_labels_mapping_action_dropdown_selected_item(action)
        self.item['action'] = ExpenseFileExcelImportController.get_labels_mapping_action_dropdown_selected_item(action)
        self.dropdown_acct_action_change()
