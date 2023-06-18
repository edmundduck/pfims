from ._anvil_designer import ExpenseFileUploadFormP2Template
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from ...App import Routing
from ...App import Caching as cache

class ExpenseFileUploadFormP2(ExpenseFileUploadFormP2Template):
    def __init__(self, dataframe, labels, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        # Any code you write here will run when the form opens.
        self.button_next.visible = False
        self.labels_mapping_panel.items = labels
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

    def button_next_click(self, **event_args):
        """This method is called when the button is clicked"""
        print(self.labels_mapping_panel.items)

    def handle_action_count(self, action, prev, **event_args):
        if action is None:
            self.hidden_action_count.text = int(self.hidden_action_count.text) + 1
        elif prev is None:
            self.hidden_action_count.text = int(self.hidden_action_count.text) - 1
        else:
            pass
        self.enable_next_button()
