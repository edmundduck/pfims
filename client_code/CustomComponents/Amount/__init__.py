from ._anvil_designer import AmountTemplate
from anvil import *
import anvil.server

class Amount(AmountTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        # Any code you write here will run before the form opens.
        self.amount_field.text = f"{self._format_ccy_display()}{self.amount}"
        self.amount_field.enabled = not self.readonly
        self.amount_field.align = self.align
        self.amount_field.font_size = self.font_size

    def amount_field_focus(self, **event_args):
        """This method is called when the TextBox gets focus"""
        self.amount_field.text = self._amount

    def amount_field_lost_focus(self, **event_args):
        """This method is called when the TextBox loses focus"""
        print(f"_amount={self._amount}")
        print(f"amount={self.amount}")
        print(f"self.amount_field.text={self.amount_field.text}")
        self._amount = self.amount_field.text
        print(f"_amount={self._amount}")
        print(f"amount={self.amount}")
        print(f"self.amount_field.text={self.amount_field.text}")
        self.amount_field.text = f"{self._format_ccy_display()}{self.amount}"

    def _format_ccy_display(self):
        return self.ccy_symbol if self.ccy_symbol else self.ccy_abbv if self.ccy_abbv else ""

    @property
    def amount(self):
        return self._amount

    @amount.setter
    def amount(self, value):
        self._amount = value
