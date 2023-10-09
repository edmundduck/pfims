from ._anvil_designer import UserSettingFormTemplate
from anvil import *
import anvil.users
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from ...Utils import Constants as const
from ...Utils.ButtonModerator import ButtonModerator
from ...Utils.ClientCache import ClientCache
from ...Utils.Logger import ClientLogger
from ....Controllers.UserSettingController import UserSettingController

logger = ClientLogger()
btnmod = ButtonModerator()

class UserSettingForm(UserSettingFormTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)
        
        # Any code you write here will run when the form opens.
        if anvil.app.environment.name in 'Dev': self.column_panel_logging.visible = True
        cache_brokers = ClientCache('generate_brokers_dropdown')
        
        self.dropdown_logging_level.items = const.LoggingLevel.dropdown
        settings, search_interval, ccy, submitted_templ_list = anvil.server.call('proc_init_settings')
        self.dropdown_default_broker.items = cache_brokers.get_cache()
        # Not use client cache to load search interval and CCY to reduce server calls turnaround
        self.dropdown_interval.items = search_interval
        self.dropdown_ccy.items = ccy
        self.dropdown_broker_list.items = cache_brokers.get_cache()
        self.dropdown_sub_templ_list.items = submitted_templ_list
        if settings is not None and len(settings) > 0:
            self.dropdown_default_broker.selected_value = cache_brokers.get_complete_key(settings.get('default_broker'))
            self.dropdown_interval.selected_value = settings.get('default_interval')
            self.time_datefrom.date = settings.get('default_datefrom')
            self.time_dateto.date = settings.get('default_dateto')
            self.dropdown_logging_level.selected_value = settings.get('logging_level')

        interval = self.dropdown_interval.selected_value[0] if isinstance(self.dropdown_interval.selected_value, list) else self.dropdown_interval.selected_value
        if interval != "SDR":
            self.time_datefrom.enabled = False
            self.time_dateto.enabled = False
    
        self.button_broker_create.enabled = False
        self.button_broker_update.enabled = False
        self.button_broker_delete.enabled = False
    
    def dropdown_interval_change(self, **event_args):
        """This method is called when an item is selected"""
        interval = self.dropdown_interval.selected_value[0] if isinstance(self.dropdown_interval.selected_value, list) else self.dropdown_interval.selected_value
        if interval != "SDR":
            if interval in (None, ''):
                self.time_datefrom.date = ''
                self.time_dateto.date = ''
        
            self.time_datefrom.enabled = False
            self.time_dateto.enabled = False
        else:
            self.time_datefrom.enabled = True
            self.time_dateto.enabled = True

    @btnmod.one_click_only
    @logger.log_function
    def button_submit_click(self, **event_args):
        """This method is called when the button is clicked"""
        cache_settings = ClientCache('select_settings')
        interval = self.dropdown_interval.selected_value[0] if isinstance(self.dropdown_interval.selected_value, list) else self.dropdown_interval.selected_value
        broker_id, broker_name, broker_ccy = self.dropdown_default_broker.selected_value
        count = anvil.server.call('proc_upsert_settings', broker_id, interval, self.time_datefrom.date, self.time_dateto.date, self.dropdown_logging_level.selected_value)
        logger.set_level()
        if count is not None and count > 0:
            n = Notification("{count} row updated successfully.".format(count=count))
            cache_settings.clear_cache()
        else:
            n = Notification("ERROR: Fail to insert or update.")
        n.show()

    @btnmod.one_click_only
    @logger.log_function
    def button_broker_create_click(self, **event_args):
        """This method is called when the button is clicked"""
        default_broker = self.dropdown_default_broker.selected_value
        cache_brokers = ClientCache('generate_brokers_dropdown')
        broker_id, dummy = anvil.server.call('proc_broker_create_update', None, self.text_broker_name.text, self.dropdown_ccy.selected_value)
        cache_brokers.clear_cache()
        self.dropdown_broker_list.items = cache_brokers.get_cache()
        self.dropdown_default_broker.items = cache_brokers.get_cache()
        self.dropdown_broker_list.selected_value = cache_brokers.get_complete_key(broker_id)
        self.dropdown_default_broker.selected_value = default_broker
        self.hidden_b_id.text = broker_id

    def text_broker_name_lost_focus(self, **event_args):
        """This method is called when the TextBox loses focus"""
        self.button_broker_create.enabled = False if self.text_broker_name.text == '' else True

    @btnmod.one_click_only
    @logger.log_function
    def button_broker_update_click(self, **event_args):
        """This method is called when the button is clicked"""
        default_broker = self.dropdown_default_broker.selected_value
        broker_id, broker_name, broker_ccy = self.dropdown_broker_list.selected_value
        cache_brokers = ClientCache('generate_brokers_dropdown')
        broker_id, dummy = anvil.server.call('proc_broker_create_update', broker_id, self.text_broker_name.text, self.dropdown_ccy.selected_value)
        cache_brokers.clear_cache()
        self.dropdown_broker_list.items = cache_brokers.get_cache()
        self.dropdown_default_broker.items = cache_brokers.get_cache()
        self.dropdown_broker_list.selected_value = cache_brokers.get_complete_key(broker_id)
        self.dropdown_default_broker.selected_value = default_broker
        self.hidden_b_id.text = broker_id

    @btnmod.one_click_only
    @logger.log_function
    def button_broker_delete_click(self, **event_args):
        """This method is called when the button is clicked"""
        cache_brokers = ClientCache('generate_brokers_dropdown')
        count, dummy = anvil.server.call('proc_broker_delete', self.hidden_b_id.text)
        cache_brokers.clear_cache()
        if count is not None and count > 0:
            self.dropdown_broker_list.items = cache_brokers.get_cache()
            self.dropdown_default_broker.items = cache_brokers.get_cache()
            n = Notification("Broker ID ({b_id}) deleted successfully.".format(b_id=self.hidden_b_id.text))
        else:
            n = Notification("ERROR: Fail to delete broker ID ({b_id}).".format(b_id=self.hidden_b_id.text))
        n.show()

    def dropdown_broker_list_change(self, **event_args):
        """This method is called when an item is selected"""
        broker_id, broker_name, broker_ccy = self.dropdown_broker_list.selected_value
        self.hidden_b_id.text = broker_id
        if broker_id in (None, ''):
            self.button_broker_update.enabled = False
            self.button_broker_delete.enabled = False
            self.button_broker_create.enabled = False
            self.text_broker_name.text = ''
        else:
            self.button_broker_update.enabled = True
            self.button_broker_delete.enabled = True
            self.button_broker_create.enabled = True
            self.text_broker_name.text = broker_name
            self.dropdown_ccy.selected_value = broker_ccy
  
    @btnmod.one_click_only
    @logger.log_function
    def button_templ_edit_click(self, **event_args):
        """This method is called when the button is clicked"""
        templ_id, templ_name = self.dropdown_sub_templ_list.selected_value if self.dropdown_sub_templ_list.selected_value is not None else [None, None]
        templ_id, result, submitted_templ_list = anvil.server.call('proc_submitted_template_update', templ_id)

        if result is not None and result > 0:
            """ Reflect the change in template dropdown """
            self.dropdown_sub_templ_list.items = submitted_templ_list
            n = Notification("Template {templ_name} has been enabled for modification in the input section.".format(templ_name=templ_name))
        else:
            n = Notification("ERROR: Fail to enable template {templ_name} for modification.".format(templ_name=templ_name))
        n.show()

    def button_logging_edit_click(self, **event_args):
        """This method is called when the button is clicked"""
        