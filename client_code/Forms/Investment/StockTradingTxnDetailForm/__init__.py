from ._anvil_designer import StockTradingTxnDetailFormTemplate
from anvil import *
import anvil.users
import anvil.server
from datetime import date
from ....Controllers import StockTradingTxnDetailController, UserSettingController
from ....Utils import Constants as const
from ....Utils.ButtonModerator import ButtonModerator
from ....Utils.ClientCache import ClientCache
from ....Utils.Validation import Validator
from ....Utils.Logger import ClientLogger

logger = ClientLogger()
btnmod = ButtonModerator()

class StockTradingTxnDetailForm(StockTradingTxnDetailFormTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)
    
        # Any code you write here will run when the form opens.
        self.input_repeating_panel.add_event_handler('x-disable-submit-button', self.disable_submit_button)
        jrn_grp = StockTradingTxnDetailController.get_stock_journal_group(self.dropdown_templ.selected_value)
        # Initiate repeating panel items to an empty list otherwise will throw NoneType error
        self.input_repeating_panel.items = []
        self.input_selldate.date = date.today()
        self.dropdown_templ.items = StockTradingTxnDetailController.generate_stock_journal_groups_dropdown()
        self.dropdown_broker.items = UserSettingController.generate_brokers_dropdown()
        self.dropdown_broker.selected_value = UserSettingController.get_broker_dropdown_selected_item(jrn_grp.get_broker())
        # Reset on screen change status
        self.disable_submit_button()
        
    @btnmod.one_click_only
    @logger.log_function
    def button_plus_click(self, **event_args):
        """This method is called when the button is clicked"""
        v = Validator()
        v.display_when_invalid(self.valerror_title)
        v.require_date_field(self.input_selldate, self.valerror_1, True)
        v.require_date_field(self.input_buydate, self.valerror_2, True)
        v.require_text_field(self.input_symbol, self.valerror_3, True)
        v.require_text_field(self.input_qty, self.valerror_4, True)
        v.require_text_field(self.input_sales, self.valerror_5, True)
        v.require_text_field(self.input_cost, self.valerror_6, True)
        v.require_text_field(self.input_fee, self.valerror_7, True)

        sell_price, buy_price, pnl = anvil.server.call('calculate_amount', self.input_sales.text, self.input_cost.text, self.input_fee.text, self.input_qty.text)
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
        jrn_grp = StockTradingTxnDetailController.get_stock_journal_group(self.dropdown_templ.selected_value)
        print("3b=", jrn_grp)
        self.templ_name.text = jrn_grp.get_name()
        self.dropdown_broker.selected_value = UserSettingController.get_broker_dropdown_selected_item(jrn_grp.get_broker())
        self.button_submit.enabled = StockTradingTxnDetailController.enable_stock_journal_group_submit_button(self.dropdown_templ.selected_value)
        self.input_repeating_panel.items = jrn_grp.get_serialized_journals()
            
    @btnmod.one_click_only
    @logger.log_function
    def button_save_templ_click(self, **event_args):
        """This method is called when the button is clicked"""
        try:
            result = StockTradingTxnDetailController.save_stock_journal_group(self.dropdown_templ.selected_value, self.templ_name.text, self.dropdown_broker.selected_valu, self.input_repeating_panel.items)
            self.dropdown_templ.items = StockTradingTxnDetailController.generate_stock_journal_groups_dropdown(reload=True)
            self.dropdown_templ.selected_value = StockTradingTxnDetailController.get_stock_journals_group_dropdown_selected_item(templ_id)
            if result:
                # Result not None means insert/update journals is done successfully
                self.input_repeating_panel.items = result[1]
                self.button_submit.enabled = StockTradingTxnDetailController.enable_stock_journal_group_submit_button(self.dropdown_templ.selected_value)
                msg = f'Stock journal group {self.templ_name.text} has been saved successfully.'
                logger.info(msg)
        except RuntimeError as err:
            logger.error(msg)
            msg = Notification(f'ERROR occurs when updating broker {self.text_broker_name.text}.')
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
        templ_id, templ_name = self.dropdown_templ.selected_value
        confirm = Label(text="Proceed template <{templ_name}> deletion by clicking DELETE.".format(templ_name=templ_name))
        userconf = alert(content=confirm, 
                        title=f"Alert - Template Deletion",
                        buttons=[("DELETE", const.Alerts.CONFIRM), ("CANCEL", const.Alerts.CANCEL)])
    
        if userconf == const.Alerts.CONFIRM:
            result = anvil.server.call('delete_templates', template_id=templ_id)
            if result is not None and result > 0:
                cache_del_iid = ClientCache(const.CacheKey.STOCK_INPUT_DEL_IID)
                
                """ Reset row delete flag """
                cache_del_iid.clear_cache()
            
                """ Reflect the change in template dropdown """
                self.dropdown_templ.items = StockTradingTxnDetailController.generate_stock_journal_groups_dropdown(reload=True)
                self.dropdown_broker.selected_value = UserSettingController.get_broker_dropdown_selected_item(UserSettingController.get_user_settings().get_broker())
                self.input_repeating_panel.items = []
                self.templ_name.text = None
                self.input_selldate.date = date.today()
                # Reset on screen change status
                self.disable_submit_button()
                msg = f"Template {templ_name} has been deleted."
                logger.info(msg)
                Notification(msg).show()
                return btnmod.override_end_state(False)
            else:
                msg = f"ERROR: Fail to delete template {templ_name}."
                logger.error(msg)
                Notification(msg).show()

    @btnmod.one_click_only
    @logger.log_function
    def button_submit_click(self, **event_args):
        """This method is called when the button is clicked"""
        templ_id, templ_name = self.dropdown_templ.selected_value
        broker_id = self.dropdown_broker.selected_value[0] if self.dropdown_broker.selected_value is not None and isinstance(self.dropdown_broker.selected_value, list) else None
        result = anvil.server.call('submit_templates', templ_id, True)

        if result is not None and result > 0:
            """ Reflect the change in template dropdown """
            self.dropdown_templ.items = StockTradingTxnDetailController.generate_stock_journal_groups_dropdown(reload=True)
            self.dropdown_broker.selected_value = UserSettingController.get_broker_dropdown_selected_item(UserSettingController.get_user_settings().get_broker())
            self.dropdown_templ.selected_value = None
            self.input_repeating_panel.items = []
            self.templ_name.text = None
            self.input_selldate.date = date.today()
            msg = f"Template {templ_name} has been submitted.\n It can be viewed in the transaction list report only."
            logger.info(msg)
            Notification(msg).show()
            return btnmod.override_end_state(False)
        else:
            msg = f"ERROR: Fail to submit template {templ_name}."
            logger.error(msg)
            Notification(msg).show()

    def templ_name_change(self, **event_args):
        """This method is called when the text in this text box is edited"""
        self.disable_submit_button()

    def dropdown_broker_change(self, **event_args):
        """This method is called when an item is selected"""
        self.disable_submit_button()

    def disable_submit_button(self, **event_args):
        self.button_submit.enabled = False    