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
    self.input_templ_name.text = anvil.server.call('update_generate_input_templ_name', 
                                                   self.input_dropdown_templ.selected_value)
    
    
  def input_button_plus_click(self, **event_args):
    """This method is called when the button is clicked"""
#    anvil.server.call('add_temp_input', 
#                      sell_date=self.input_selldate.date, 
#                      buy_date=self.input_buydate.date, 
#                      symbol=self.input_symbol.text, 
#                      qty=self.input_qty.text, 
#                      sales=self.input_sales.text, 
#                      cost=self.input_cost.text, 
#                      pnl=self.input_pnl.text, 
#                      sell_price=self.input_sales.text/qty, 
#                      buy_price=self.input_cost.text/qty)
    self.input_sell_price.text = self.input_sales.text / self.input_qty.text
    self.input_buy_price.text = self.input_cost.text / self.input_qty.text
    
    self.new_data = {"sell_date": self.input_selldate.date,
                    "buy_date": self.input_buydate.date,
#                    "symbol": self.input_symbol.text,
                    "symbol": "XXX",
                    "qty": self.input_qty.text,
                    "sales": self.input_sales.text,
                    "cost": self.input_cost.text,
                    "pnl": self.input_pnl.text,
                    "sell_date": self.input_sell_price.text,
                    "buy_date": self.input_buy_price.text}

    #self.data = self.input_repeating_panel.items
    self.input_repeating_panel.items = [self.new_data]
    
  def input_dropdown_templ_change(self, **event_args):
    """This method is called when an item is selected"""
    self.input_templ_name.text = anvil.server.call('update_generate_input_templ_name', 
                                                   self.input_dropdown_templ.selected_value)

  def input_dropdown_templ_show(self, **event_args):
    """This method is called when the DropDown is shown on the screen"""
    self.input_dropdown_templ.items = anvil.server.call('get_input_templ_list')


