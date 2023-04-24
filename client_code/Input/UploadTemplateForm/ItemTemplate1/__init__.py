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
        self.row_dropdown_datacol.items = glo.input_expense_col_def()
        self.row_dropdown_extraact.items = glo.input_expense_upload_additional_action()
        self.row_dropdown_lbl.items = cache.get_caching_labels_dropdown()