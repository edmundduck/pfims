from ._anvil_designer import form_sub1_inputTemplate
from anvil import *
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

class form_sub1_input(form_sub1_inputTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run when the form opens.

  def input_button_plus_click(self, **event_args):
    """This method is called when the button is clicked"""
    if self.input_chk_dtl.checked is True:
      anvil.server.call('add_temp_input', 
                        date_sales=self.input_date.date, 
                        date_buy=self.input_date.date, 
                        symbol=self.input_symbol.text, 
                        qty=self.input_qty.text, 
                        sales=self.input_sales.text, 
                        cost=self.input_cost.text, 
                        pnl=self.input_pnl.text, 
                        sell_price=0, 
                        buy_price=0)
    else:
      anvil.server.call('add_temp_input', 
                        date_sales=self.input_date.date, 
                        date_buy=self.input_date.date, 
                        symbol=self.input_symbol.text, 
                        qty=self.input_qty.text, 
                        sales=self.input_sales.text, 
                        cost=self.input_cost.text, 
                        pnl=self.input_pnl.text, 
                        sell_price=0, 
                        buy_price=0)

