from ._anvil_designer import StockTradingTxnDetailRPTemplateTemplate
from anvil import *
import anvil.server
from .....Controllers import StockTradingTxnDetailController
from .....Utils.ButtonModerator import ButtonModerator
from .....Utils.Logger import ClientLogger

logger = ClientLogger()
btnmod = ButtonModerator()

class StockTradingTxnDetailRPTemplate(StockTradingTxnDetailRPTemplateTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)
    
        # Any code you write here will run when the form opens.
        from .....Utils.Constants import Roles
        self.row_pnl.role = Roles.AMT_NEGATIVE if self.item['pnl'] < 0 else Roles.AMT_POSITIVE
        self.row_label_pnl.role = self.row_pnl.role
        self.input_data_panel_readonly.visible = True
        self.input_data_panel_editable.visible = False            

    @btnmod.one_click_only
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

    @btnmod.one_click_only
    @logger.log_function
    def button_save_click(self, **event_args):
        """This method is called when the button is clicked"""
        from .....Utils.Validation import Validator
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
        v.highlight_when_invalid(self.row_selldate)
        v.highlight_when_invalid(self.row_buydate)
        v.highlight_when_invalid(self.row_symbol)
        v.highlight_when_invalid(self.row_qty)
        v.highlight_when_invalid(self.row_sales)
        v.highlight_when_invalid(self.row_cost)
        v.highlight_when_invalid(self.row_fee)
    
        if v.is_valid():
            self.row_sell_price.text, self.row_buy_price.text, self.row_pnl.text = StockTradingTxnDetailController.calculate_amount(self.row_sales.text, self.row_cost.text, self.row_fee.text, self.row_qty.text)
      
            # Lesson learnt ... THIS LINE DOESN'T WORK!!
            # new_data = {'sell_date': self.row_selldate.date,
            #                'buy_date': self.row_buydate.date,
            #                'symbol': self.row_symbol.text,
            #                'qty': self.row_qty.text,
            #                'sales': self.row_sales.text,
            #                'cost': self.row_cost.text,
            #                'sell_price': self.row_sell_price.text,
            #                'buy_price': self.row_buy_price.text,
            #                'iid': self.row_iid.text}
            # self.item = self.row_symbol.text
            # self.item = new_data
            self.item = {
                'sell_date': self.row_selldate.date,
                'buy_date': self.row_buydate.date,
                'symbol': self.row_symbol.text,
                'qty': self.row_qty.text,
                'sales': float(self.row_sales.text),
                'cost': float(self.row_cost.text),
                'fee': float(self.row_fee.text),
                'sell_price': self.row_sell_price.text,
                'buy_price': self.row_buy_price.text,
                'pnl': self.row_pnl.text,
                'iid': self.row_iid.text
            }
      
            self.input_data_panel_readonly.visible = True
            self.input_data_panel_editable.visible = False            
            self.parent.raise_event('x-disable-submit-button')
      
    @btnmod.one_click_only
    @logger.log_function
    def button_delete_click(self, **event_args):
        """This method is called when the button is clicked"""
        StockTradingTxnDetailController.delete_item(self.item.get('iid', None))
        if self.item.get('iid', None) is not None:
            self.parent.raise_event('x-disable-submit-button')
        self.remove_from_parent()

    @btnmod.one_click_only
    def button_cancel_click(self, **event_args):
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
        
        self.input_data_panel_readonly.visible = True
        self.input_data_panel_editable.visible = False
