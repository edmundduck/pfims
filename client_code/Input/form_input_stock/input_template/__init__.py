from ._anvil_designer import input_templateTemplate
from anvil import *
import anvil.users
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from .... import global_var
from .... import validation

class input_template(input_templateTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)
    
        # Any code you write here will run when the form opens.
        if self.item['pnl'] < 0:
            self.foreground = 'Red'
        else:
            self.foreground = 'Green'

    def button_edit_click(self, **event_args):
        """This method is called when the button is clicked"""
        self.row_selldate.date = self.item['sell_date']
        self.row_buydate.date = self.item['buy_date']
        self.row_symbol.text = self.item['symbol']
        self.row_qty.text = self.item['qty']
        self.row_sales.text = self.item['sales']
        self.row_cost.text = self.item['cost']
        self.row_fee.text = self.item['fee']
        self.row_sell_price.text = self.item['sell_price']
        self.row_buy_price.text = self.item['buy_price']
        self.row_pnl.text = self.item['pnl']
        self.row_iid.text = self.item['iid']
        
        self.input_data_panel_readonly.visible = False
        self.input_data_panel_editable.visible = True

    def button_save_click(self, **event_args):
        """This method is called when the button is clicked"""
        v = validation.Validator()
    
        # To access the parent form, needs to access 3 parent levels ...
        # self.parent = Repeating Panel
        # self.parent.parent = Data Grid
        # self.parent.parent.parent = Parent Form
        #print(self.parent.parent.parent.valerror_1.text)
        v.display_when_invalid(self.parent.parent.parent.valerror_title)
        v.require_date_field(self.row_selldate, self.parent.parent.parent.valerror_1, True)
        v.require_date_field(self.row_buydate, self.parent.parent.parent.valerror_2, True)
        v.require_text_field(self.row_symbol, self.parent.parent.parent.valerror_3, True)
        v.require_text_field(self.row_qty, self.parent.parent.parent.valerror_4, True)
        v.require_text_field(self.row_sales, self.parent.parent.parent.valerror_5, True)
        v.require_text_field(self.row_cost, self.parent.parent.parent.valerror_6, True)
        v.require_text_field(self.row_fee, self.parent.parent.parent.valerror_7, True)
    
        if v.is_valid():
            self.row_sell_price.text = anvil.server.call('cal_price' ,self.row_sales.text, self.row_qty.text)
            self.row_buy_price.text = anvil.server.call('cal_price', self.row_cost.text, self.row_qty.text)
            self.row_pnl.text = anvil.server.call('cal_profit', self.row_sales.text, self.row_cost.text, self.row_fee.text)
      
            # Lesson learnt ... THIS LINE DOESN'T WORK!!
            # new_data = {"sell_date": self.row_selldate.date,
            #                "buy_date": self.row_buydate.date,
            #                "symbol": self.row_symbol.text,
            #                "qty": self.row_qty.text,
            #                "sales": self.row_sales.text,
            #                "cost": self.row_cost.text,
            #                "sell_price": self.row_sell_price.text,
            #                "buy_price": self.row_buy_price.text,
            #                "iid": self.row_iid.text}
            # self.item = self.row_symbol.text
            # self.item = new_data
            self.item = {"sell_date": self.row_selldate.date,
                        "buy_date": self.row_buydate.date,
                        "symbol": self.row_symbol.text,
                        "qty": self.row_qty.text,
                        "sales": float(self.row_sales.text),
                        "cost": float(self.row_cost.text),
                        "fee": float(self.row_fee.text),
                        "sell_price": self.row_sell_price.text,
                        "buy_price": self.row_buy_price.text,
                        "pnl": self.row_pnl.text,
                        "iid": self.row_iid.text}
      
            self.input_data_panel_readonly.visible = True
            self.input_data_panel_editable.visible = False
            
            #self.parent.raise_event('x-save-change', iid=self.row_iid.text)
            self.parent.raise_event('x-save-change')
      
    def button_delete_click(self, **event_args):
        """This method is called when the button is clicked"""
        anvil.server.call('delete_row', self.row_iid.text)    
        self.remove_from_parent()
        #global_var.input_row_del_trigger()
