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

    def button_nav_upload_mapping_click(self, **event_args):
        """This method is called when the button is clicked"""
        Routing.open_upload_mapping_form(self)

    def button_nav_input_exp_click(self, **event_args):
        """This method is called when the button is clicked"""
        Routing.open_exp_input_form(self)

    def enable_next_button(self, **event_args):
        cb = event_args['sender']
        if cb.checked:
            self.button_next.visible = True
        else:
            vis = False
            for i in cb.parent.get_components():
                if isinstance(i, CheckBox) and i.checked:
                    vis = True
            self.button_next.visible = vis

    def button_next_click(self, **event_args):
        """This method is called when the button is clicked"""
        tablist = []
        for i in self.sheet_tabs_panel.get_components():
            if isinstance(i, CheckBox) and i.checked:
                tablist.append(i.text)
        matrix = anvil.server.call('select_mapping_matrix', self.dropdown_filter.selected_value)
        df, lbls = anvil.server.call('import_file', file=self.file_loader_1.file, tablist=tablist, rules=matrix)
        self.labels_mapping_panel.items = lbls
