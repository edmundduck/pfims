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
    
    # Initiate repeating panel items to an empty list otherwise will throw NoneType error
    self.input_repeating_panel.items = []

    # Debug - populate test data - START
    self.input_selldate.date = "2021-05-10"
    self.input_buydate.date = "2021-04-19"
    self.input_symbol.text = "AMD"
    self.input_qty.text = 1000
    self.input_sales.text = 10000
    self.input_cost.text = 8000
    self.input_pnl.text = 2000
    # Debug - populate test data - END
    
  def input_button_plus_click(self, **event_args):
    """This method is called when the button is clicked"""
    self.input_sell_price.text = self.input_sales.text / self.input_qty.text
    self.input_buy_price.text = self.input_cost.text / self.input_qty.text
    
    self.new_data = {"sell_date": ,
                    "buy_date": self.input_buydate.date,
                    "symbol": self.input_symbol.text,
                    "qty": self.input_qty.text,
                    "sales": self.input_sales.text,
                    "cost": self.input_cost.text,
                    "pnl": self.input_pnl.text,
                    "sell_price": self.input_sell_price.text,
                    "buy_price": self.input_buy_price.text}
    
    self.input_repeating_panel.items = self.input_repeating_panel.items + [self.new_data]
    
  def input_dropdown_templ_change(self, **event_args):
    """This method is called when an item is selected"""
    self.input_templ_name.text = anvil.server.call('get_input_templ_name', 
                                                   self.input_dropdown_templ.selected_value)
    self.input_repeating_panel.items = anvil.server.call('get_input_templ_items', 
                                                         self.input_dropdown_templ.selected_value)

  def input_dropdown_templ_show(self, **event_args):
    """This method is called when the DropDown is shown on the screen"""
    self.input_dropdown_templ.items = anvil.server.call('get_input_templ_list')
    self.input_templ_name.text = anvil.server.call('get_input_templ_name', 
                                                   self.input_dropdown_templ.selected_value)

  def button_save_templ_click(self, **event_args):
    """This method is called when the button is clicked"""
    
    templ_id = anvil.server.call('generate_new_templ_id', 
                                 self.input_dropdown_templ.selected_value)
    
    anvil.server.call('upsert_temp_template',
                      template_id=templ_id,
                      template_name=self.input_templ_name.text)
    
    for row in self.input_repeating_panel.items:
      anvil.server.call('upsert_temp_input', 
                        sell_date=row['sell_date'], 
                        buy_date=row['buy_date'], 
                        template_id=templ_id, 
                        symbol=row['symbol'], 
                        qty=row['qty'], 
                        sales=row['sales'], 
                        cost=row['cost'], 
                        pnl=row['pnl'], 
                        sell_price=row['sell_price'], 
                        buy_price=row['buy_price'])

    self.input_dropdown_templ.items = anvil.server.call('get_input_templ_list')
    self.input_dropdown_templ.selected_value = anvil.server.call('merge_templ_id_name', 
                                                                 templ_id, 
                                                                 self.input_templ_name.text)
