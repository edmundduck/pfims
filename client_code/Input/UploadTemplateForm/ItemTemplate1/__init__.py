from ._anvil_designer import ItemTemplate1Template
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from ....App import Caching as cache
from ....App import Global as glo

class ItemTemplate1(ItemTemplate1Template):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        # Any code you write here will run before the form opens.
        self.row_dropdown_datacol.items = cache.get_caching_exp_tbl_def()
        self.row_dropdown_extraact.items = glo.input_expense_upload_additional_action()
        self.row_dropdown_lbl.items = cache.get_caching_labels_dropdown()

    def row_button_add_click(self, **event_args):
        """This method is called when the button is clicked"""
        rule = self.row_lbl_1.text + " " + self.row_dropdown_excelcol.selected_value + " " + self.row_lbl_2.text + " " \
                + self.row_dropdown_datacol.selected_value["text"] + "."
        if self.row_dropdown_extraact.selected_value is not None:
            rule = rule + " In addition " + self.row_dropdown_extraact.selected_value + " " + self.row_dropdown_lbl.selected_value[1]
        self.row_flowpanel_rules.add_component(Label(text=rule, font_size=10, foreground='White'))
