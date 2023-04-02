from ._anvil_designer import LabelMaintFormTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from ... import Routing

class LabelMaintForm(LabelMaintFormTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        # Any code you write here will run before the form opens.

    def button_exp_input_click(self, **event_args):
        """This method is called when the button is clicked"""
        Routing.open_exp_input_form(self)

    def dropdown_acct_list_show(self, **event_args):
        """This method is called when the DropDown is shown on the screen"""
        self.dropdown_acct_list.items = anvil.server.call('generate_accounts_dropdown')
        self.dropdown_acct_list.selected_value = None

    def dropdown_acct_list_change(self, **event_args):
        """This method is called when an item is selected"""
        self.hidden_acct_id.text, \
        self.text_acct_name.text, \
        self.dropdown_ccy.selected_value, \
        self.date_valid_from.date, \
        self.date_valid_to.date, \
        self.dropdown_status.selected_value = anvil.server.call('get_selected_account_attr', self.dropdown_acct_list.selected_value[0])

    def dropdown_ccy_show(self, **event_args):
        """This method is called when the DropDown is shown on the screen"""
        self.dropdown_ccy.items = anvil.server.call('generate_ccy_dropdown')
        self.dropdown_ccy.selected_value = None

    def dropdown_status_show(self, **event_args):
        """This method is called when the DropDown is shown on the screen"""
        self.dropdown_status.items = [('Active', True), ('Inactive', False)]
        self.dropdown_status.selected_value = True

    def button_labels_create_click(self, **event_args):
        """This method is called when the button is clicked"""
        acct_id = anvil.server.call('create_account',
                                    name=self.text_acct_name.text,
                                    ccy=self.dropdown_ccy.selected_value,
                                    valid_from=self.date_valid_from.date,
                                    valid_to=self.date_valid_to.date,
                                    status=True
                                )

        if acct_id is None or acct_id <= 0:
            n = Notification("ERROR: Fail to create account {acct_name}.".format(acct_name=self.text_acct_name.text))
        else:
            print(acct_id)
            """ Reflect the change in accounts dropdown """
            self.dropdown_acct_list.items = anvil.server.call('generate_accounts_dropdown')
            self.dropdown_acct_list.selected_value = [acct_id, self.text_acct_name.text]
            n = Notification("Account {acct_name} has been created successfully.".format(acct_name=self.text_acct_name.text))
        n.show()
        return

    def button_labels_update_click(self, **event_args):
        """This method is called when the button is clicked"""
        result = anvil.server.call('update_account',
                                   id=self.hidden_acct_id.text,
                                   name=self.text_acct_name.text,
                                   ccy=self.dropdown_ccy.selected_value,
                                   valid_from=self.date_valid_from.date,
                                   valid_to=self.date_valid_to.date,
                                   status=self.dropdown_status.selected_value
                                )

        if result is None or result <= 0:
            n = Notification("ERROR: Fail to update account {acct_name}.".format(acct_name=self.text_acct_name.text))
        else:
            """ Reflect the change in accounts dropdown """
            self.dropdown_acct_list.items = anvil.server.call('generate_accounts_dropdown')
            n = Notification("Account {acct_name} has been updated successfully.".format(acct_name=self.text_acct_name.text))
        n.show()
        return

    def button_labels_move_click(self, **event_args):
        """This method is called when the button is clicked"""
        pass

    def button_labels_delete_click(self, **event_args):
        """This method is called when the button is clicked"""
        selected_acct_id, selected_acct_name = self.dropdown_acct_list.selected_value
        msg = Label(text="Proceed account <{acct_name}> ({acct_id}) deletion by clicking DELETE.".format(acct_name=selected_acct_name, acct_id=selected_acct_id))
        userconf = alert(content=msg,
                        title=f"Alert - Account Deletion",
                        buttons=[
                        ("DELETE", "Y"),
                        ("CANCEL", "N")
                        ])

        if userconf == "Y":
            result = anvil.server.call('delete_account', selected_acct_id)
            if result is not None and result > 0:
                """ Reflect the change in template dropdown """
                self.clear()

                n = Notification("Account {acct_name} has been deleted.".format(acct_name=selected_acct_name))
            else:
                n = Notification("ERROR: Fail to delete account {acct_name}.".format(acct_name=selected_acct_name))
            n.show()

    def clear(self, **event_args):
        self.dropdown_acct_list_show()
        self.dropdown_ccy.selected_value = None
        self.dropdown_status.selected_value = True
        self.text_acct_name.text = None
        self.date_valid_from.date = None
        self.date_valid_to.date = None
