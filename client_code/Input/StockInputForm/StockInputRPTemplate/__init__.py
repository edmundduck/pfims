from ._anvil_designer import StockInputRPTemplateTemplate
from anvil import *
import anvil.users
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from ....Utils import Constants as const
from ....Utils.ClientCache import ClientCache
from ....Utils.Validation import Validator
from ....Utils.Logger import ClientLogger

logger = ClientLogger()

class StockInputRPTemplate(StockInputRPTemplateTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)
    
        # Any code you write here will run when the form opens.
        if self.item['pnl'] < 0:
            self.foreground = const.ColorSchemes.AMT_NEG
        else:
            self.foreground = const.ColorSchemes.AMT_POS

    @logger.log_function
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

    @logger.log_function
    def button_save_click(self, **event_args):
        """This method is called when the button is clicked"""
        print("cost=", self.item['cost'])
        v = Validator()
    
        # To access the parent form, needs to access 3 parent levels ...
        # self.parent = Repeating Panel
        # self.parent.parent = Data Grid
        # self.parent.parent.parent = Parent Form
        v.display_when_invalid(self.parent.parent.parent.valerror_title)
        v.require_date_field(self.row_selldate, self.parent.parent.parent.valerror_1, True)
        v.require_date_field(self.row_buydate, self.parent.parent.parent.valerror_2, True)
        v.require_text_field(self.row_symbol, self.parent.parent.parent.valerror_3, True)
        v.require_text_field(self.row_qty, self.parent.parent.parent.valerror_4, True)
        v.require_text_field(self.row_sales, self.parent.parent.parent.valerror_5, True)
        v.require_text_field(self.row_cost, self.parent.parent.parent.valerror_6, True)
        v.require_text_field(self.row_fee, self.parent.parent.parent.valerror_7, True)
    
        if v.is_valid():
            self.row_sell_price.text, self.row_buy_price.text, self.row_pnl.text = anvil.server.call('calculate_amount' ,self.row_sales.text, self.row_cost.text, self.row_fee.text, self.row_qty.text)
      
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
      
            print("cost=", self.item['cost'])
            self.input_data_panel_readonly.visible = True
            self.input_data_panel_editable.visible = False            
            self.parent.raise_event('x-disable-submit-button')
      
    @logger.log_function
    def button_delete_click(self, **event_args):
        """This method is called when the button is clicked"""
        if self.item.get('iid') is not None:
            cache_del_iid = ClientCache(const.CacheKey.STOCK_INPUT_DEL_IID)
            if cache_del_iid.is_empty():
                cache_del_iid.set_cache([self.item.get('iid')])
            else:
                cache_del_iid.get_cache().append(self.item.get('iid'))
        self.parent.raise_event('x-disable-submit-button')
        self.remove_from_parent()
