from ._anvil_designer import AmountTemplate
from anvil import *
import anvil.server

class Amount(AmountTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        # Any code you write here will run before the form opens.
        self.editable_amt.text = self.amount
        self.display_amt.text = f"{self._format_ccy_display()}{self.amount}"
        print(f"{self.amount}")
        self.editable_amt.visible = False
        self.display_amt.visible = True
        self.editable_amt.enabled = not self.readonly
        self.display_amt.enabled = not self.readonly
        self.editable_amt.align, self.display_amt.align = [self.align]*2
        self.editable_amt.font_size, self.display_amt.font_size = [self.font_size]*2

    def display_amt_focus(self, **event_args):
        """This method is called when the TextBox gets focus"""
        print(f"{self.amount}")
        self.editable_amt.visible = True
        self.display_amt.visible = False
        self.editable_amt.focus()

    def editable_amt_lost_focus(self, **event_args):
        """This method is called when the TextBox loses focus"""
        print(f"{self.amount}")
        self.amount = self.editable_amt.text
        self.display_amt.text = f"{self._format_ccy_display()}{self.amount}"
        self.editable_amt.visible = False
        self.display_amt.visible = True

    def _format_ccy_display(self):
        return self.ccy_symbol if self.ccy_symbol else self.ccy_abbv if self.ccy_abbv else ""
