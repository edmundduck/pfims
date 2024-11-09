from ._anvil_designer import form_poc5Template
from anvil import *
import anvil.server
import anvil.users

class form_poc5(form_poc5Template):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        # Any code you write here will run before the form opens.
        #self.amount_1.amount = 5
        self.amount_1.ccy_symbol = "$"
        self.amount_1.ccy_abbv = "USD"
        self.amount_2.ccy_symbol = ""
        self.amount_2.ccy_abbv = "JPY"
        self.amount_3.ccy_symbol = "@"
        self.amount_3.ccy_abbv = ""