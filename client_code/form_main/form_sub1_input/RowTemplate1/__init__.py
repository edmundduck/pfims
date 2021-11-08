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
    self.input_row_selldate.date = self.item['sell_date']
    self.input_row_buydate.date = self.item['buy_date']
    self.input_row_symbol.text = self.item['symbol']
    self.input_row_qty.text = self.item['qty']
    self.input_row_sales.text = self.item['sales']
    self.input_row_cost.text = self.item['cost']
    self.input_row_fee.text = self.item['fee']
    self.input_row_sell_price.text = self.item['sell_price']
    self.input_row_buy_price.text = self.item['buy_price']
    self.input_row_pnl.text = self.item['pnl']
    self.input_row_iid.text = self.item['iid']
    
    self.input_data_panel_readonly.visible = False
    self.input_data_panel_editable.visible = True

  def input_button_save_click(self, **event_args):
    """This method is called when the button is clicked"""
    self.input_row_sell_price.text = anvil.server.call('cal_price' ,self.input_row_sales.text, self.input_row_qty.text)
    self.input_row_buy_price.text = anvil.server.call('cal_price', self.input_row_cost.text, self.input_row_qty.text)
    self.input_row_pnl.text = anvil.server.call('cal_profit', self.input_row_sales.text, self.input_row_cost.text)
    
    # Lesson learnt ... THIS LINE DOESN'T WORK!!
    # new_data = {"sell_date": self.input_row_selldate.date,
    #                "buy_date": self.input_row_buydate.date,
    #                "symbol": self.input_row_symbol.text,
    #                "qty": self.input_row_qty.text,
    #                "sales": self.input_row_sales.text,
    #                "cost": self.input_row_cost.text,
    #                "sell_price": self.input_row_sell_price.text,
    #                "buy_price": self.input_row_buy_price.text,
    #                "iid": self.input_row_iid.text}
    # self.item = self.input_row_symbol.text
    # self.item = new_data
    self.item = {"sell_date": self.input_row_selldate.date,
                 "buy_date": self.input_row_buydate.date,
                 "symbol": self.input_row_symbol.text,
                 "qty": self.input_row_qty.text,
                 "sales": self.input_row_sales.text,
                 "cost": self.input_row_cost.text,
                 "fee": self.input_row_fee.text,
                 "sell_price": self.input_row_sell_price.text,
                 "buy_price": self.input_row_buy_price.text,
                 "pnl": self.input_row_pnl.text,
                 "iid": self.input_row_iid.text}
    
    self.input_data_panel_readonly.visible = True
    self.input_data_panel_editable.visible = False
    
  def input_button_delete_click(self, **event_args):
    """This method is called when the button is clicked"""
    self.remove_from_parent()

