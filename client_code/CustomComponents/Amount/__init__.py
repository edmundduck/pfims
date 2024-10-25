from ._anvil_designer import AmountTemplate
from anvil import *
import anvil.server

class Amount(AmountTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        # Any code you write here will run before the form opens.
        self.editable_amt.text = self.amount
        self.display_amt.text = self.amount
        if self.readonly:
            self.editable_amt.visible = False
            self.display_amt.visible = True