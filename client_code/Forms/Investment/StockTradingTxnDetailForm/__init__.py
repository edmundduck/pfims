from ._anvil_designer import StockTradingTxnDetailFormTemplate
from anvil import *
import anvil.server
from datetime import date
from ....Controllers import StockTradingTxnDetailController
from ....Utils.ButtonModerator import ButtonModerator
from ....Utils.Logger import ClientLogger

logger = ClientLogger()
btnmod = ButtonModerator()

class StockTradingTxnDetailForm(StockTradingTxnDetailFormTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)
    
        # Any code you write here will run when the form opens.
        StockTradingTxnDetailController.init_cache()
        self.input_repeating_panel.add_event_handler('x-disable-submit-button', self.disable_submit_button)
        # Initiate repeating panel items to an empty list otherwise will throw NoneType error
        self.input_repeating_panel.items = []
        self.input_selldate.date = date.today()
        self.dropdown_templ.items = StockTradingTxnDetailController.generate_stock_journal_groups_dropdown()
        self.dropdown_broker.items = StockTradingTxnDetailController.generate_brokers_dropdown()
        self.dropdown_broker.selected_value = StockTradingTxnDetailController.get_broker_dropdown_selected_item(self.dropdown_templ.selected_value)
        self.button_delete_templ.enabled = StockTradingTxnDetailController.enable_stock_journal_group_delete_button(self.dropdown_templ.selected_value)
        # Reset on screen change status
        self.disable_submit_button()
        
    @btnmod.one_click_only
    @logger.log_function
    def button_plus_click(self, **event_args):
        """This method is called when the button is clicked"""
        from ....Utils.Validation import Validator
        v = Validator()
        v.display_when_invalid(self.valerror_title)
        v.require_date_field(self.input_selldate, self.valerror_1, True)
        v.require_date_field(self.input_buydate, self.valerror_2, True)
        v.require_text_field(self.input_symbol, self.valerror_3, True)
        v.require_text_field(self.input_qty, self.valerror_4, True)
        v.require_text_field(self.input_sales, self.valerror_5, True)
        v.require_text_field(self.input_cost, self.valerror_6, True)
        v.require_text_field(self.input_fee, self.valerror_7, True)

        sell_price, buy_price, pnl = StockTradingTxnDetailController.calculate_amount(self.input_sales.text, self.input_cost.text, self.input_fee.text, self.input_qty.text)
        new_data = {
            "sell_date": self.input_selldate.date,
            "buy_date": self.input_buydate.date,
            "symbol": self.input_symbol.text,
            "qty": self.input_qty.text,
            "sales": self.input_sales.text,
            "cost": self.input_cost.text,
            "fee": self.input_fee.text,
            "sell_price": sell_price,
            "buy_price": buy_price,
            "pnl": pnl, 
            #"iid": int(last_iid)+1}
            "iid": None
        }
      
        self.input_repeating_panel.items = self.input_repeating_panel.items + [new_data]
        self.disable_submit_button()
      
    def dropdown_templ_change(self, **event_args):
        """This method is called when an item is selected"""
        self.templ_name.text = StockTradingTxnDetailController.get_group_name(self.dropdown_templ.selected_value)
        self.dropdown_broker.selected_value = StockTradingTxnDetailController.get_broker_dropdown_selected_item(self.dropdown_templ.selected_value)
        self.button_submit.enabled = StockTradingTxnDetailController.enable_stock_journal_group_submit_button(self.dropdown_templ.selected_value)
        self.button_delete_templ.enabled = StockTradingTxnDetailController.enable_stock_journal_group_delete_button(self.dropdown_templ.selected_value)
        self.input_repeating_panel.items = StockTradingTxnDetailController.get_journals(self.dropdown_templ.selected_value)
            
    @btnmod.one_click_only
    @logger.log_function
    def button_save_templ_click(self, **event_args):
        """This method is called when the button is clicked"""
        from ....Error.ValidationError import ValidationError

        # Reflect updates in the row first
        # *** ESSENTIAL ***
        # Update child items from repeating panel to parent form items
        # Refer to the following reference links for detail
        # https://anvil.works/forum/t/is-it-possible-to-access-a-repeating-panels-methods-from-the-parent-form/3028/2
        # https://anvil.works/forum/t/refresh-data-bindings-when-any-key-in-self-items-changes/1141/3
        # https://anvil.works/forum/t/repeating-panel-to-collect-new-information/356/3
        self.input_repeating_panel.items = [c.input_data_panel_readonly.item for c in self.input_repeating_panel.get_components()]
        try:
            result = StockTradingTxnDetailController.save_stock_journal_group(self.dropdown_templ.selected_value, self.templ_name.text, self.dropdown_broker.selected_value, self.input_repeating_panel.items)
        except ValidationError as err:
            logger.error(err)
            msg = f"ERROR occurs when updating stock journal group [{self.templ_name.text}].\n{err}"
            Notification(msg, timeout=10).show()
        except Exception as err:
            logger.error(err)
            msg = f'ERROR occurs when updating stock journal group [{self.templ_name.text}].'
            Notification(msg).show()
        else:
            self.dropdown_templ.items = StockTradingTxnDetailController.generate_stock_journal_groups_dropdown(reload=True)
            self.dropdown_templ.selected_value = StockTradingTxnDetailController.get_stock_journal_group_dropdown_selected_item(result.get_id())
            # Result not None means insert/update journals is done successfully
            self.input_repeating_panel.items = StockTradingTxnDetailController.get_journals(self.dropdown_templ.selected_value, reload=True)
            self.button_submit.enabled = StockTradingTxnDetailController.enable_stock_journal_group_submit_button(self.dropdown_templ.selected_value)
            msg = f'Stock journal group {self.templ_name.text} has been saved successfully.'
            logger.info(msg)
            Notification(msg).show()
            
    @btnmod.one_click_only
    def button_erase_click(self, **event_args):
        """This method is called when the button is clicked"""
        self.input_selldate.date = date.today()
        self.input_buydate.date = None
        self.input_symbol.text = None
        self.input_qty.text = None
        self.input_sales.text = None
        self.input_cost.text = None
        self.input_fee.text = 0
        self.input_sell_price.text = None
        self.input_buy_price.text = None
        self.input_pnl.text = None
    
    @btnmod.one_click_only
    @logger.log_function
    def button_delete_templ_click(self, **event_args):
        """This method is called when the button is clicked"""
        from ....Utils.Constants import Alerts
        _, jrn_grp_name = self.dropdown_templ.selected_value
        confirm = Label(text="Proceed stock journal group [{jrn_grp_name}] deletion by clicking PROCEED.".format(jrn_grp_name=jrn_grp_name))
        userconf = alert(content=confirm, title='Alert - Confirm to delete stock journal group', buttons=[('PROCEED', Alerts.CONFIRM), ('CANCEL', Alerts.CANCEL)])
    
        if userconf == Alerts.CONFIRM:
            try:
                result = StockTradingTxnDetailController.delete_stock_journal_group(self.dropdown_templ.selected_value)
                self.dropdown_templ.items = StockTradingTxnDetailController.generate_stock_journal_groups_dropdown(reload=True)
                self.dropdown_broker.selected_value = StockTradingTxnDetailController.get_broker_dropdown_selected_item()
                self.input_repeating_panel.items = []
                self.templ_name.text = None
                self.input_selldate.date = date.today()
                # Reset on screen change status
                self.disable_submit_button()
                msg = f"Stock journal group {jrn_grp_name} has been deleted."
                logger.info(msg)
                Notification(msg).show()
                return btnmod.override_end_state(False)
            except Exception as err:
                logger.error(err)
                msg = f"ERROR occurs when deleting stock journal group {jrn_grp_name}."
                Notification(msg).show()

    @btnmod.one_click_only
    @logger.log_function
    def button_submit_click(self, **event_args):
        """This method is called when the button is clicked"""
        jrn_grp_name = self.templ_name.text
        try:
            result = StockTradingTxnDetailController.submit_stock_journal_group(self.dropdown_templ.selected_value)
            """ Reflect the change in template dropdown """
            self.dropdown_templ.items = StockTradingTxnDetailController.generate_stock_journal_groups_dropdown(reload=True)
            self.dropdown_broker.selected_value = StockTradingTxnDetailController.get_broker_dropdown_selected_item()
            self.input_repeating_panel.items = []
            self.templ_name.text = None
            self.input_selldate.date = date.today()
            msg = f"Stock journal group {jrn_grp_name} has been submitted.\n It can be viewed in the transaction list report only."
            logger.info(msg)
            Notification(msg).show()
            return btnmod.override_end_state(False)
        except Exception as err:
            logger.error(err)
            msg = f"ERROR occurs when submitting stock journal group {jrn_grp_name}."
            Notification(msg).show()

    def templ_name_change(self, **event_args):
        """This method is called when the text in this text box is edited"""
        self.disable_submit_button()

    def dropdown_broker_change(self, **event_args):
        """This method is called when an item is selected"""
        self.disable_submit_button()

    def disable_submit_button(self, **event_args):
        self.button_submit.enabled = False    