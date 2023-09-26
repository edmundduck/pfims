from ._anvil_designer import StockInputFormTemplate
from anvil import *
import anvil.users
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from datetime import date
from ...Utils import Constants as const
from ...Utils import Caching as cache
from ...Utils.ClientCache import ClientCache
from ...Utils.Validation import Validator
from ...Utils.Logger import ClientLogger

logger = ClientLogger()

class StockInputForm(StockInputFormTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)
    
        # Any code you write here will run when the form opens.
        self.input_repeating_panel.add_event_handler('x-save-change', self.save_row_change)
        self.input_repeating_panel.add_event_handler('x-disable-submit-button', self.disable_submit_button)

        # Initiate repeating panel items to an empty list otherwise will throw NoneType error
        cache_brokers = ClientCache('generate_brokers_dropdown')
        self.input_repeating_panel.items = []
        self.input_selldate.date = date.today()
        self.templ_name.text, broker_id = anvil.server.call('get_selected_template_attr', self.dropdown_templ.selected_value)
        self.dropdown_broker.items = cache_brokers.get_cache()
        self.dropdown_broker.selected_value = cache_brokers.get_complete_key(broker_id)
        # Reset on screen change status
        self.disable_submit_button()
        
    @logger.log_function
    def save_row_change(self, **event_args):
        """ 
        *** ESSENTIAL ***
        Update child items from repeating panel to parent form items
        Refer to the following reference links for detail
        https://anvil.works/forum/t/is-it-possible-to-access-a-repeating-panels-methods-from-the-parent-form/3028/2
        https://anvil.works/forum/t/refresh-data-bindings-when-any-key-in-self-items-changes/1141/3
        https://anvil.works/forum/t/repeating-panel-to-collect-new-information/356/3
        """
        # TODO - Improve the update change logic so that don't have to go through whole list everytime
        self.input_repeating_panel.items = [c.input_data_panel_readonly.item \
                                            for c in self.input_repeating_panel.get_components()]
    
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

        # IID generation logic is moved to database function
        # When a new row is created, IID is default to be None
        # if v.is_valid():
        #     last_iid = 0
        #     if len(self.input_repeating_panel.items) > 0:
        #         last_iid = self.input_repeating_panel.items[len(self.input_repeating_panel.items)-1]['iid']
      
        new_data = {"sell_date": self.input_selldate.date,
                    "buy_date": self.input_buydate.date,
                    "symbol": self.input_symbol.text,
                    "qty": self.input_qty.text,
                    "sales": self.input_sales.text,
                    "cost": self.input_cost.text,
                    "fee": self.input_fee.text,
                    "sell_price": anvil.server.call('cal_price', self.input_sales.text, self.input_qty.text),
                    "buy_price": anvil.server.call('cal_price', self.input_cost.text, self.input_qty.text),
                    "pnl": anvil.server.call('cal_profit', self.input_sales.text, self.input_cost.text, self.input_fee.text), 
                    #"iid": int(last_iid)+1}
                    "iid": None}
      
        self.input_repeating_panel.items = self.input_repeating_panel.items + [new_data]
        self.disable_submit_button()
      
    def dropdown_templ_change(self, **event_args):
        """This method is called when an item is selected"""
        cache_brokers = ClientCache('generate_brokers_dropdown')
        self.templ_name.text, broker_id = anvil.server.call('get_selected_template_attr', self.dropdown_templ.selected_value)
        self.dropdown_broker.selected_value = cache_brokers.get_complete_key(broker_id)
        self.input_repeating_panel.items = anvil.server.call('select_template_journals', self.dropdown_templ.selected_value)
        if self.dropdown_templ.selected_value is not None:
            self.button_submit.enabled = True

    def dropdown_templ_show(self, **event_args):
        """This method is called when the DropDown is shown on the screen"""
        self.dropdown_templ.items = anvil.server.call('generate_template_dropdown')
    
    @logger.log_function
    def button_save_templ_click(self, **event_args):
        """This method is called when the button is clicked"""
        templ_id = anvil.server.call('get_template_id', self.dropdown_templ.selected_value)
        templ_name = self.templ_name.text
        broker_id = self.dropdown_broker.selected_value[0] if self.dropdown_broker.selected_value is not None and isinstance(self.dropdown_broker.selected_value, list) else None
        templ_id = anvil.server.call('save_templates',
                                     template_id=templ_id,
                                     template_name=templ_name, 
                                     broker_id=broker_id,
                                     del_iid=cache.get_deleted_row()
                                    )

        if templ_id is None or templ_id <= 0:
            msg = f"ERROR: Fail to save template {templ_name}."
            logger.error(msg)
            Notification(msg).show()
            return
        
        """ Trigger save_row_change if del_iid is not empty """
        if len(cache.get_deleted_row()) > 0:
            self.save_row_change()
            cache.deleted_row_reset()
        
        """ Add/Update """
        result = anvil.server.call('upsert_journals', templ_id, self.input_repeating_panel.items)

        if result is not None:
            """ Reflect the change in template dropdown """
            self.dropdown_templ.items = anvil.server.call('generate_template_dropdown')
            self.dropdown_templ.selected_value = anvil.server.call('generate_template_dropdown_item', templ_id, templ_name)
            self.input_repeating_panel.items = anvil.server.call('select_template_journals', self.dropdown_templ.selected_value)
            self.button_submit.enabled = True
            msg = f"Template {templ_name} has been saved successfully."
            logger.info(msg)
        else:
            msg = f"ERROR: Fail to save template {templ_name}."
            logger.error(msg)
        Notification(msg).show()
            
    def button_erase_click(self, **event_args):
        """This method is called when the button is clicked"""
        self.input_selldate.date = ""
        self.input_buydate.date = ""
        self.input_symbol.text = ""
        self.input_qty.text = ""
        self.input_sales.text = ""
        self.input_cost.text = ""
        self.input_fee.text = 0
        self.input_sell_price.text = ""
        self.input_buy_price.text = ""
        self.input_pnl.text = ""
        """ Reset row delete flag """
        cache.deleted_row_reset()
    
    @logger.log_function
    def button_delete_templ_click(self, **event_args):
        """This method is called when the button is clicked"""
        cache_brokers = ClientCache('generate_brokers_dropdown')
        to_be_del_templ_name = self.dropdown_templ.selected_value
        confirm = Label(text="Proceed template <{templ_name}> deletion by clicking DELETE.".format(templ_name=to_be_del_templ_name))
        userconf = alert(content=confirm, 
                        title=f"Alert - Template Deletion",
                        buttons=[("DELETE", const.Alerts.CONFIRM), ("CANCEL", const.Alerts.CANCEL)])
    
        if userconf == const.Alerts.CONFIRM:
            templ_id = anvil.server.call('get_template_id', to_be_del_templ_name)
            result = anvil.server.call('delete_templates', template_id=templ_id)
            if result is not None and result > 0:
                """ Reset row delete flag """
                cache.deleted_row_reset()
            
                """ Reflect the change in template dropdown """
                self.dropdown_templ_show()
                self.dropdown_broker.items = cache_brokers.get_cache()
                self.input_repeating_panel.items = []
                
                msg = f"Template {to_be_del_templ_name} has been deleted."
                logger.info(msg)
            else:
                msg = f"ERROR: Fail to delete template {to_be_del_templ_name}."
                logger.error(msg)
            Notification(msg).show()                

    @logger.log_function
    def button_submit_click(self, **event_args):
        """This method is called when the button is clicked"""
        to_be_submitted_templ_name = self.dropdown_templ.selected_value
        templ_id = anvil.server.call('get_template_id', to_be_submitted_templ_name)
        templ_name = self.templ_name.text
        broker_id = self.dropdown_broker.selected_value[0] if self.dropdown_broker.selected_value is not None and isinstance(self.dropdown_broker.selected_value, list) else None
        result = anvil.server.call('submit_templates', templ_id, True)

        if result is not None and result > 0:
            """ Reflect the change in template dropdown """
            self.dropdown_templ.items = anvil.server.call('generate_template_dropdown')
            self.dropdown_templ.raise_event('change')
        
            msg = f"Template {to_be_submitted_templ_name} has been submitted.\n It can be viewed in the transaction list report only."
            logger.info(msg)
        else:
            msg = f"ERROR: Fail to submit template {to_be_submitted_templ_name}."
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