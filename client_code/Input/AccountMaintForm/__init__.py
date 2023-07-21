from ._anvil_designer import AccountMaintFormTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from ...Utils import Routing
from ...Utils import Constants as const
from ...Utils import Caching as cache
from ...Utils.Logging import dump, debug, info, warning, error, critical

class AccountMaintForm(AccountMaintFormTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        # Any code you write here will run before the form opens.
    
    def button_exp_input_click(self, **event_args):
        """This method is called when the button is clicked"""
        Routing.open_exp_input_form(self)

    def dropdown_acct_list_show(self, **event_args):
        """This method is called when the DropDown is shown on the screen"""
        self.dropdown_acct_list.items = cache.accounts_dropdown()
        self.dropdown_acct_list.selected_value = None
        self.button_accounts_update.enabled = False if self.dropdown_acct_list.selected_value in ('', None) else True
        self.button_accounts_delete.enabled = False if self.dropdown_acct_list.selected_value in ('', None) else True

    def dropdown_acct_list_change(self, **event_args):
        """This method is called when an item is selected"""
        selected_acct_id, selected_acct_name = self.dropdown_acct_list.selected_value if self.dropdown_acct_list.selected_value is not None else [None, None]
        self.hidden_acct_id.text, \
        self.text_acct_name.text, \
        self.dropdown_ccy.selected_value, \
        self.date_valid_from.date, \
        self.date_valid_to.date, \
        self.dropdown_status.selected_value = anvil.server.call('get_selected_account_attr', selected_acct_id)
        self.button_accounts_update.enabled = False if self.dropdown_acct_list.selected_value in ('', None) else True
        self.button_accounts_delete.enabled = False if self.dropdown_acct_list.selected_value in ('', None) else True

    def dropdown_ccy_show(self, **event_args):
        """This method is called when the DropDown is shown on the screen"""
        self.dropdown_ccy.items = cache.ccy_dropdown()
        self.dropdown_ccy.selected_value = None

    def dropdown_status_show(self, **event_args):
        """This method is called when the DropDown is shown on the screen"""
        self.dropdown_status.items = [('Active', True), ('Inactive', False)]
        self.dropdown_status.selected_value = True

    @debug.log_function
    def button_accounts_create_click(self, **event_args):
        """This method is called when the button is clicked"""
        acct_name = self.text_acct_name.text
        acct_id = anvil.server.call('create_account',
                                    name=acct_name,
                                    ccy=self.dropdown_ccy.selected_value, 
                                    valid_from=self.date_valid_from.date,
                                    valid_to=self.date_valid_to.date,
                                    status=self.dropdown_status.selected_value
                                )

        if acct_id is None or acct_id <= 0:
            msg = f"ERROR: Fail to create account {acct_name} ({acct_id})."
            error.log(msg)
        else:
            """ Reflect the change in accounts dropdown """
            cache.accounts_reset()
            self.dropdown_acct_list.items = cache.accounts_dropdown()
            self.dropdown_acct_list.selected_value = [acct_id, acct_name]
            msg = f"Account {acct_name} ({acct_id}) has been created successfully."
            info.log(msg)
        Notification(msg).show()
        return

    @debug.log_function
    def button_accounts_update_click(self, **event_args):
        """This method is called when the button is clicked"""
        acct_name = self.text_acct_name.text
        acct_id = self.hidden_acct_id.text
        result = anvil.server.call('update_account',
                                   id=acct_id,
                                   name=acct_name,
                                   ccy=self.dropdown_ccy.selected_value, 
                                   valid_from=self.date_valid_from.date,
                                   valid_to=self.date_valid_to.date,
                                   status=self.dropdown_status.selected_value
                                )

        if result is None or result <= 0:
            msg = f"ERROR: Fail to update account {acct_name} ({acct_id})."
            error.log(msg)
        else:
            """ Reflect the change in accounts dropdown """
            cache.accounts_reset()
            self.dropdown_acct_list.items = cache.accounts_dropdown()
            self.dropdown_acct_list.selected_value = [acct_id, acct_name]
            msg = f"Account {acct_name} ({acct_id}) has been updated successfully."
            info.log(msg)
        Notification(msg).show()
        return

    @debug.log_function
    def button_accounts_delete_click(self, **event_args):
        """This method is called when the button is clicked"""
        acct_id, acct_name = self.dropdown_acct_list.selected_value if self.dropdown_acct_list.selected_value is not None else [None, None]
        confirm = Label(text=f"Proceed account <{acct_name}> ({acct_id}) deletion by clicking DELETE.")
        userconf = alert(content=confirm, 
                        title=f"Alert - Account Deletion",
                        buttons=[("DELETE", const.Alerts.CONFIRM), ("CANCEL", const.Alerts.CANCEL)])
    
        if userconf == const.Alerts.CONFIRM:
            cache.accounts_reset()
            result = anvil.server.call('delete_account', acct_id)
            if result is not None and result > 0:
                """ Reflect the change in account dropdown """
                self.clear()
                msg = f"Account {acct_name} ({acct_id}) has been deleted."
                info.log(msg)
            else:
                msg = f"ERROR: Fail to delete account {acct_name} ({acct_id})."
                error.log(msg)
            Notification(msg).show()

    def clear(self, **event_args):
        self.dropdown_acct_list_show()
        self.dropdown_ccy.selected_value = None
        self.dropdown_status.selected_value = True
        self.text_acct_name.text = None
        self.date_valid_from.date = None
        self.date_valid_to.date = None
