from ._anvil_designer import form_poc5Template
from anvil import *
import anvil.server
from ...Utils.Logger import ClientLogger

logger = ClientLogger()

class form_poc5(form_poc5Template):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        # Any code you write here will run before the form opens.

    def button_1_click(self, **event_args):
        """This method is called when the button is clicked"""
        a1, b1, c1, d1 = self.separate_call()
        self.consolidated_call()
        a2, b2, c2, d2 = [None, None, None, None]

    @logger.log_function
    def separate_call(self):
        from ...Controllers import AccountMaintController
        a = anvil.server.call('generate_expense_tbl_def_dropdown')
        b = anvil.server.call('generate_upload_action_dropdown')
        c = anvil.server.call('generate_labels_dropdown')
        d = AccountMaintController.generate_accounts_dropdown()
        return [a, b, c, d]

    @logger.log_function
    def consolidated_call(self):
        func_list = [
            'generate_expense_tbl_def_dropdown',
            'generate_upload_action_dropdown',
            'generate_labels_dropdown',
            'generate_accounts_list'
        ]
        a, b, c, d = anvil.server.call('proc_call_cache', func_list)
        return [a, b, c, d]
