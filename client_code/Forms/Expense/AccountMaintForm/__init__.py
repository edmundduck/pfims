from ._anvil_designer import AccountMaintFormTemplate
from anvil import *
from ....Controllers import AccountMaintController
from ....Utils.ButtonModerator import ButtonModerator
from ....Utils.Logger import ClientLogger

logger = ClientLogger()
btnmod = ButtonModerator()

class AccountMaintForm(AccountMaintFormTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        # Any code you write here will run before the form opens.
        self.dropdown_ccy.items = AccountMaintController.generate_currency_dropdown()
        self.dropdown_ccy.selected_value = None
        self.dropdown_acct_list.items = AccountMaintController.generate_accounts_dropdown()
        self.dropdown_acct_list.selected_value = None
        self.button_accounts_update.enabled = AccountMaintController.enable_account_update_button(self.dropdown_acct_list.selected_value)
        self.button_accounts_delete.enabled = AccountMaintController.enable_account_delete_button(self.dropdown_acct_list.selected_value)

    def button_exp_input_click(self, **event_args):
        """This method is called when the button is clicked"""
        from ....Utils import Routing
        Routing.open_exp_input_form(self)

    def dropdown_acct_list_change(self, **event_args):
        """This method is called when an item is selected"""
        self.text_acct_name.text = AccountMaintController.get_account_name(self.dropdown_acct_list.selected_value)
        self.dropdown_ccy.selected_value = AccountMaintController.get_currency_dropdown_selected_item(AccountMaintController.get_account_base_currency(self.dropdown_acct_list.selected_value))
        self.date_valid_from.date = AccountMaintController.get_account_valid_from_date(self.dropdown_acct_list.selected_value)
        self.date_valid_to.date = AccountMaintController.get_account_valid_to_date(self.dropdown_acct_list.selected_value)
        self.dropdown_status.selected_value = AccountMaintController.get_account_status(self.dropdown_acct_list.selected_value)
        self.button_accounts_update.enabled = AccountMaintController.enable_account_update_button(self.dropdown_acct_list.selected_value)
        self.button_accounts_delete.enabled = AccountMaintController.enable_account_delete_button(self.dropdown_acct_list.selected_value)

    def dropdown_status_show(self, **event_args):
        """This method is called when the DropDown is shown on the screen"""
        self.dropdown_status.items = [('Active', True), ('Inactive', False)]
        self.dropdown_status.selected_value = True

    @btnmod.one_click_only
    @logger.log_function
    def button_accounts_create_click(self, **event_args):
        """This method is called when the button is clicked"""
        try:
            account = AccountMaintController.create_account(
                self.text_acct_name.text,
                self.dropdown_ccy.selected_value,
                self.date_valid_from.date,
                self.date_valid_to.date,
                self.dropdown_status.selected_value
            )
            """ Reflect the change in accounts dropdown """
            self.dropdown_acct_list.items = AccountMaintController.generate_accounts_dropdown(reload=True)
            self.dropdown_acct_list.selected_value = [account.get_id(), account.get_name()]
            msg = f"Account {account.get_name()} ({account.get_id()}) has been created successfully."
            logger.info(msg)
        except Exception as err:
            logger.error(err)
            msg = f"ERROR occurs when creating account {self.text_acct_name.text}."
        Notification(msg).show()

    @btnmod.one_click_only
    @logger.log_function
    def button_accounts_update_click(self, **event_args):
        """This method is called when the button is clicked"""
        try:
            account = AccountMaintController.update_account(
                self.dropdown_acct_list.selected_value,
                self.text_acct_name.text,
                self.dropdown_ccy.selected_value, 
                self.date_valid_from.date,
                self.date_valid_to.date,
                self.dropdown_status.selected_value
            )
            """ Reflect the change in accounts dropdown """
            self.dropdown_acct_list.items = AccountMaintController.generate_accounts_dropdown(reload=True)
            self.dropdown_acct_list.selected_value = [account.get_id(), account.get_name()]
            msg = f"Account {account.get_name()} ({account.get_id()}) has been updated successfully."
            logger.info(msg)
        except Exception as err:
            logger.error(err)
            msg = f"ERROR occurs when updating account {self.text_acct_name.text}."
        Notification(msg).show()

    @btnmod.one_click_only
    @logger.log_function
    def button_accounts_delete_click(self, **event_args):
        """This method is called when the button is clicked"""
        from ....Utils.Constants import Alerts
        acct_id, acct_name = self.dropdown_acct_list.selected_value if self.dropdown_acct_list.selected_value is not None else [None, None]
        confirm = Label(text='Proceed account [{acct_name}] deletion by clicking PROCEED.'.format(acct_name=acct_name))
        userconf = alert(content=confirm, title='Alert - Confirm to delete account', buttons=[('PROCEED', Alerts.CONFIRM), ('CANCEL', Alerts.CANCEL)])
    
        if userconf == Alerts.CONFIRM:
            try:
                result = AccountMaintController.delete_account(self.dropdown_acct_list.selected_value)
                """ Reflect the change in account dropdown """
                self.dropdown_acct_list.items = AccountMaintController.generate_accounts_dropdown(reload=True)
                self.clear()
                msg = f"Account {acct_name} ({acct_id}) has been deleted."
                logger.info(msg)
                Notification(msg).show()
                return btnmod.override_end_state(False)
            except Exception as err:
                logger.error(err)
                msg = f"ERROR occurs when deleting account {acct_name}."
                Notification(msg).show()

    def clear(self, **event_args):
        self.dropdown_acct_list.selected_value = None
        self.dropdown_ccy.selected_value = None
        self.dropdown_status.selected_value = True
        self.text_acct_name.text = None
        self.date_valid_from.date = None
        self.date_valid_to.date = None
