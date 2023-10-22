from ._anvil_designer import ExpenseFileExcelImportFormTemplate
from anvil import *
from ....Controllers import ExpenseFileExcelImportController
from ....Utils.ButtonModerator import ButtonModerator
from ....Utils.Logger import ClientLogger

logger = ClientLogger()
btnmod = ButtonModerator()

class ExpenseFileExcelImportForm(ExpenseFileExcelImportFormTemplate):
    def __init__(self, data, labels, accounts, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        # Any code you write here will run when the form opens.
        self.dropdown_tabs.items = ExpenseFileExcelImportController.generate_expense_tabs_dropdown()
        self.dropdown_actions_for_all_labels.items = ExpenseFileExcelImportController.generate_labels_mapping_action_dropdown()
        self.dropdown_actions_for_all_accounts.items = ExpenseFileExcelImportController.generate_labels_mapping_action_dropdown()
        self.tag = {'data': data}
        logger.debug("self.tag=", self.tag)
        self.button_next.visible = False
        self.labels_mapping_panel.items = ExpenseFileExcelImportController.populate_labels_repeating_panel_items(labels)
        logger.trace("self.labels_mapping_panel.items=", self.labels_mapping_panel.items)
        if accounts is None:
            self.flow_panel_step7.visible = False
        else:
            self.accounts_mapping_panel.items = ExpenseFileExcelImportController.populate_accounts_repeating_panel_items(accounts)
            logger.trace("self.accounts_mapping_panel.items=", self.accounts_mapping_panel.items)
            self.flow_panel_step7.visible = True
        self.hidden_action_count.text = len(labels)
        self.labels_mapping_panel.add_event_handler('x-handle-action-count', self.handle_action_count)

    def button_nav_upload_mapping_click(self, **event_args):
        """This method is called when the button is clicked"""
        from ....Utils import Routing
        Routing.open_upload_mapping_form(self)

    def button_nav_input_exp_click(self, **event_args):
        """This method is called when the button is clicked"""
        from ....Utils import Routing
        Routing.open_exp_input_form(self)

    def enable_next_button(self, **event_args):
        self.button_next.visible = True if self.hidden_action_count.text == 0 else False

    @btnmod.one_click_only
    @logger.log_function
    def button_next_click(self, **event_args):
        """This method is called when the button is clicked"""
        from ....Utils import Routing

        df = ExpenseFileExcelImportController.update_excel_import_mapping(self.tag.get('data'), self.labels_mapping_panel.items, self.accounts_mapping_panel.items)
        ExpenseFileExcelImportController.generate_labels_dropdown(reload=True)
        ExpenseFileExcelImportController.generate_accounts_dropdown(reload=True)
        Routing.open_exp_input_form(self, tab_id=self.dropdown_tabs.selected_value, data=df)

    def handle_action_count(self, action, prev, **event_args):
        if action is None:
            self.hidden_action_count.text = int(self.hidden_action_count.text) + 1
        elif prev is None:
            self.hidden_action_count.text = int(self.hidden_action_count.text) - 1
        else:
            pass
        self.enable_next_button()

    def dropdown_actions_for_all_labels_change(self, **event_args):
        """This method is called when an item is selected"""
        action, _ = self.dropdown_actions_for_all_labels.selected_value if self.dropdown_actions_for_all_labels.selected_value is not None else [None, None]
        self.labels_mapping_panel.raise_event_on_children('x-apply-action-to-all-labels', action=action)

    def dropdown_actions_for_all_accounts_change(self, **event_args):
        """This method is called when an item is selected"""
        action, _ = self.dropdown_actions_for_all_accounts.selected_value if self.dropdown_actions_for_all_accounts.selected_value is not None else [None, None]
        self.accounts_mapping_panel.raise_event_on_children('x-apply-action-to-all-accounts', action=action)
