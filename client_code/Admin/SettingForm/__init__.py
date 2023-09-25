from ._anvil_designer import SettingFormTemplate
from anvil import *
import anvil.users
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from ...Utils import Constants as const
from ...Utils import Caching as cache
from ...Utils.Logger import ClientLogger

logger = ClientLogger()

class SettingForm(SettingFormTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)
        
        # Any code you write here will run when the form opens.
        if anvil.app.environment.name in 'Dev': self.column_panel_logging.visible = True
        self.dropdown_logging_level.items = const.LoggingLevel.dropdown
        settings, search_interval, brokers_dropdown, ccy, submitted_templ_list = anvil.server.call('proc_init_settings')
        self.dropdown_default_broker.items = brokers_dropdown
        # Not use client cache to load search interval and CCY to reduce server calls turnaround
        self.dropdown_interval.items = search_interval
        self.dropdown_ccy.items = ccy
        self.dropdown_broker_list.items = brokers_dropdown
        self.dropdown_sub_templ_list.items = submitted_templ_list
        if settings is not None and len(settings) > 0:
            self.dropdown_default_broker.selected_value = cache.get_key_from_cache(settings.get('default_broker'), self.dropdown_default_broker.items)
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

    @logger.log_function
    def button_submit_click(self, **event_args):
        """This method is called when the button is clicked"""
        interval = self.dropdown_interval.selected_value[0] if isinstance(self.dropdown_interval.selected_value, list) else self.dropdown_interval.selected_value
        broker_id, broker_name, broker_ccy = self.dropdown_default_broker.selected_value
        count = anvil.server.call('upsert_settings', 
                                  def_broker=broker_id, 
                                  def_interval=interval, 
                                  def_datefrom=self.time_datefrom.date, 
                                  def_dateto=self.time_dateto.date,
                                  logging_level=self.dropdown_logging_level.selected_value
                                 )
        anvil.server.call('set_user_logging_level')
        logger.set_level()
        if (count > 0):
            n = Notification("{count} row updated successfully.".format(count=count))
        else:
            n = Notification("ERROR: Fail to insert or update.")
        n.show()

    @logger.log_function
    def button_broker_create_click(self, **event_args):
        """This method is called when the button is clicked"""
        default_broker = self.dropdown_default_broker.selected_value
        b_id, brokers_dropdown = anvil.server.call('proc_broker_create_update', None, self.text_broker_name.text, self.dropdown_ccy.selected_value)
        self.dropdown_broker_list.items = brokers_dropdown
        self.dropdown_default_broker.items = brokers_dropdown
        self.dropdown_broker_list.selected_value = b_id
        self.dropdown_default_broker.selected_value = default_broker

    def text_broker_name_lost_focus(self, **event_args):
        """This method is called when the TextBox loses focus"""
        self.button_broker_create.enabled = False if self.text_broker_name.text == '' else True

    @logger.log_function
    def button_broker_update_click(self, **event_args):
        """This method is called when the button is clicked"""
        default_broker = self.dropdown_default_broker.selected_value
        b_id, brokers_dropdown = anvil.server.call('proc_broker_create_update', None, self.text_broker_name.text, self.dropdown_ccy.selected_value)
        self.dropdown_broker_list.items = brokers_dropdown
        self.dropdown_default_broker.items = brokers_dropdown
        self.dropdown_broker_list.selected_value = b_id
        self.dropdown_default_broker.selected_value = default_broker

    @logger.log_function
    def button_broker_delete_click(self, **event_args):
        """This method is called when the button is clicked"""
        count, brokers_dropdown = anvil.server.call('proc_broker_delete', self.hidden_b_id.text)
        if (count > 0):
            self.dropdown_broker_list.items = brokers_dropdown
            self.dropdown_default_broker.items = brokers_dropdown
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
  
    @logger.log_function
    def button_templ_edit_click(self, **event_args):
        """This method is called when the button is clicked"""
        to_be_enabled_templ_name = self.dropdown_sub_templ_list.selected_value
        templ_id, result, submitted_templ_list = anvil.server.call('proc_submitted_template_update', to_be_enabled_templ_name)

        if result is not None and result > 0:
            """ Reflect the change in template dropdown """
            self.dropdown_sub_templ_list.items = submitted_templ_list
            n = Notification("Template {templ_name} has been enabled for modification in the input section.".format(templ_name=to_be_enabled_templ_name))
        else:
            n = Notification("ERROR: Fail to enable template {templ_name} for modification.".format(templ_name=to_be_enabled_templ_name))
        n.show()

    def button_logging_edit_click(self, **event_args):
        """This method is called when the button is clicked"""
        
