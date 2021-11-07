from ._anvil_designer import RowTemplate1Template
from anvil import *
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

class RowTemplate1(RowTemplate1Template):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run when the form opens.

  def input_button_edit_click(self, **event_args):
    """This method is called when the button is clicked"""
    self.input_row_selldate.date = self.input_data_panel_readonly.item['sell_date']
    self.input_row_buydate.date = self.input_data_panel_readonly.item['buy_date']
    self.input_row_symbol.text = self.input_data_panel_readonly.item['symbol']
    self.input_row_qty.text = self.input_data_panel_readonly.item['qty']
    self.input_row_sales.text = self.input_data_panel_readonly.item['sales']
    self.input_row_cost.text = self.input_data_panel_readonly.item['cost']
    self.input_row_pnl.text = self.input_data_panel_readonly.item['pnl']
    self.input_row_sell_price.text = self.input_data_panel_readonly.item['sell_price']
    self.input_row_buy_price.text = self.input_data_panel_readonly.item['buy_price']
    
    self.input_data_panel_readonly.visible = False
    self.input_data_panel_editable.visible = True

  def input_button_save_click(self, **event_args):
    """This method is called when the button is clicked"""
    self.input_row_sell_price.text = float(self.input_row_sales.text) / float(self.input_row_qty.text)
    self.input_row_buy_price.text = float(self.input_row_cost.text) / float(self.input_row_qty.text)
    
    self.new_data = {"sell_date": self.input_row_selldate.date,
                    "buy_date": self.input_row_buydate.date,
                    "symbol": self.input_row_symbol.text,
                    "qty": self.input_row_qty.text,
                    "sales": self.input_row_sales.text,
                    "cost": self.input_row_cost.text,
                    "pnl": self.input_row_pnl.text,
                    "sell_price": self.input_row_sell_price.text,
                    "buy_price": self.input_row_buy_price.text}
    
    #self.input_data_panel_readonly.item = self.new_data
    self.item = self.new_data
    self.refresh_data_bindings()
    #self.item['symbol'] = self.input_row_symbol.text

    self.input_data_panel_readonly.visible = True
    self.input_data_panel_editable.visible = False
    
  def input_button_delete_click(self, **event_args):
    """This method is called when the button is clicked"""
    self.input_data_panel_readonly.remove_from_parent()

