from ._anvil_designer import AccountMaintFormTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from ... import Routing

class AccountMaintForm(AccountMaintFormTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        # Any code you write here will run before the form opens.
    
    def link_acct_maint_click(self, **event_args):
        """This method is called when the link is clicked"""
        Routing.open_exp_input_form(self)

    def dropdown_acct_list_show(self, **event_args):
        """This method is called when the DropDown is shown on the screen"""
        self.dropdown_acct_list.items = anvil.server.call('generate_accounts_dropdown')

    def dropdown_acct_list_change(self, **event_args):
        """This method is called when an item is selected"""
        self.text_acct_name.text, \
        self.dropdown_ccy.selected_value, \
        self.date_valid_from.date, \
        self.date_valid_to.date, \
        self.dropdown_status.selected_value = anvil.server.call('get_selected_account_attr', self.dropdown_acct_list.selected_value)

    def dropdown_ccy_show(self, **event_args):
        """This method is called when the DropDown is shown on the screen"""
        self.dropdown_ccy.items = anvil.server.call('generate_ccy_dropdown')

    def dropdown_status_show(self, **event_args):
        """This method is called when the DropDown is shown on the screen"""
        self.dropdown_status.items = [('Active', True), ('Inactive', False)]

    def button_accounts_create_click(self, **event_args):
        """This method is called when the button is clicked"""
        acct_id = anvil.server.call('create_accounts',
                                    name=self.text_acct_name.text,
                                    ccy=self.dropdown_ccy.selected_value, 
                                    valid_from=self.date_valid_from.date,
                                    valid_to=self.date_valid_to.date,
                                    status=True
                                )

        if acct_id is None or acct_id <= 0:
            n = Notification("ERROR: Fail to create account {acct_name}.".format(acct_name=self.text_acct_name.text))
        else:
            """ Reflect the change in accounts dropdown """
            self.dropdown_acct_list.items = anvil.server.call('generate_accounts_dropdown')
            n = Notification("Account {acct_name} has been created successfully.".format(acct_name=self.text_acct_name.text))
        n.show()
        return

    def button_accounts_update_click(self, **event_args):
        """This method is called when the button is clicked"""
        pass

    def button_accounts_delete_click(self, **event_args):
        """This method is called when the button is clicked"""
        pass
