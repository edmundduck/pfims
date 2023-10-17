from ._anvil_designer import ExpenseFileExcelImportFormTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from ...Controllers import ExpenseFileExcelImportController
from ...Utils import Routing
from ...Utils.ButtonModerator import ButtonModerator
from ...Utils.ClientCache import ClientCache
from ...Utils.Logger import ClientLogger

logger = ClientLogger()
btnmod = ButtonModerator()

class ExpenseFileExcelImportForm(ExpenseFileExcelImportFormTemplate):
    def __init__(self, data, labels, accounts, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        # Any code you write here will run when the form opens.
        cache_labels = ClientCache('generate_labels_dropdown')
        cache_exptabs = ClientCache('generate_expensetabs_dropdown')
        cache_lbl_action = ClientCache('generate_labels_mapping_action_dropdown')
        self.dropdown_tabs.items = cache_exptabs.get_cache()
        self.dropdown_actions_for_all_labels.items = cache_lbl_action.get_cache()
        self.dropdown_actions_for_all_accounts.items = cache_lbl_action.get_cache()
        self.tag = {'data': data}
        logger.debug("self.tag=", self.tag)
        self.button_next.visible = False
        # Prefill "labels map to" dropdown by finding high proximity choices
        relevant_lbls = anvil.server.call('predict_relevant_labels', srclbl=labels, curlbl=cache_labels.get_cache())
        logger.debug("relevant_lbls=", relevant_lbls)
        # Transpose Dict of Lists (DL) to List of Dicts (LD)
        # Ref - https://stackoverflow.com/questions/37489245/transposing-pivoting-a-dict-of-lists-in-python
        DL = {
            'srclbl': labels,
            'action': [ None for i in range(len(labels))],
            'tgtlbl': relevant_lbls,
            'new': labels
        }
        logger.trace("DL=", DL)
        DL_acct = {
            'srcacct': accounts,
            'action': [ None for i in range(len(accounts))],
            'tgtacct': [ None for i in range(len(accounts))],
            'newacct': accounts
        }
        self.labels_mapping_panel.items = [dict(zip(DL, col)) for col in zip(*DL.values())]
        logger.trace("self.labels_mapping_panel.items=", self.labels_mapping_panel.items)
        if accounts is None:
            self.flow_panel_step7.visible = False
        else:
            self.accounts_mapping_panel.items = [dict(zip(DL_acct, col)) for col in zip(*DL_acct.values())]
            self.flow_panel_step7.visible = True
        self.hidden_action_count.text = len(labels)
        self.labels_mapping_panel.add_event_handler('x-handle-action-count', self.handle_action_count)

    def button_nav_upload_mapping_click(self, **event_args):
        """This method is called when the button is clicked"""
        Routing.open_upload_mapping_form(self)

    def button_nav_input_exp_click(self, **event_args):
        """This method is called when the button is clicked"""
        Routing.open_exp_input_form(self)

    def enable_next_button(self, **event_args):
        if self.hidden_action_count.text == 0:
            self.button_next.visible = True
        else:
            self.button_next.visible = False

    @btnmod.one_click_only
    @logger.log_function
    def button_next_click(self, **event_args):
        """This method is called when the button is clicked"""
        cache_labels = ClientCache('generate_labels_dropdown')
        logger.trace(f"labels_mapping={self.labels_mapping_panel.items}")
        df = anvil.server.call('proc_excel_update_mappings', data=self.tag.get('data'), mapping_lbls=self.labels_mapping_panel.items, mapping_accts=self.accounts_mapping_panel.items)
        cache_labels.clear_cache()
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
        action, action_desc = self.dropdown_actions_for_all_labels.selected_value if self.dropdown_actions_for_all_labels.selected_value is not None else [None, None]
        self.labels_mapping_panel.raise_event_on_children('x-apply-action-to-all-labels', action=action)

    def dropdown_actions_for_all_accounts_change(self, **event_args):
        """This method is called when an item is selected"""
        action, action_desc = self.dropdown_actions_for_all_accounts.selected_value if self.dropdown_actions_for_all_accounts.selected_value is not None else [None, None]
        self.accounts_mapping_panel.raise_event_on_children('x-apply-action-to-all-accounts', action=action)
