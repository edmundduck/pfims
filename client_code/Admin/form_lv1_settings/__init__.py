from ._anvil_designer import form_lv1_settingsTemplate
from anvil import *
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from ... import global_var

class form_lv1_settings(form_lv1_settingsTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run when the form opens.
    settings = anvil.server.call('select_settings')
    if len(settings) > 0:
      self.dropdown_default_broker.selected_value = settings.get('default_broker')
      self.dropdown_interval.selected_value = settings.get('default_interval')
      self.time_datefrom.date = settings.get('default_datefrom')
      self.time_dateto.date = settings.get('default_dateto')
      
    if self.dropdown_interval.selected_value != "SDR":
      self.time_datefrom.enabled = False
      self.time_dateto.enabled = False
    
    self.button_broker_create.enabled = False
    self.button_broker_update.enabled = False
    self.button_broker_delete.enabled = False
    
  def dropdown_default_broker_show(self, **event_args):
    """This method is called when the DropDown is shown on the screen"""
    self.dropdown_default_broker.items = [''] + anvil.server.call('select_brokers')

  def dropdown_interval_show(self, **event_args):
    """This method is called when the DropDown is shown on the screen"""
    self.dropdown_interval.items = global_var.search_interval_dropdown()

  def dropdown_ccy_show(self, **event_args):
    """This method is called when the DropDown is shown on the screen"""
    self.dropdown_ccy.items = global_var.setting_ccy_dropdown()

  def dropdown_interval_change(self, **event_args):
    """This method is called when an item is selected"""
    if self.dropdown_interval.selected_value != "SDR":
      if self.dropdown_interval.selected_value == '' or self.dropdown_interval.selected_value is None:
        self.time_datefrom.date = ''
        self.time_dateto.date = ''
        
      self.time_datefrom.enabled = False
      self.time_dateto.enabled = False
    else:
      self.time_datefrom.enabled = True
      self.time_dateto.enabled = True

  def button_submit_click(self, **event_args):
    """This method is called when the button is clicked"""
    anvil.server.call('upsert_settings', 
                      self.dropdown_default_broker.selected_value, 
                      self.dropdown_interval.selected_value, 
                      self.time_datefrom.date, 
                      self.time_dateto.date)

  def button_broker_create_click(self, **event_args):
    """This method is called when the button is clicked"""
    b_id = \
    anvil.server.call('upsert_brokers', 
                      '', 
                      self.text_broker_name.text, 
                      self.dropdown_ccy.selected_value)
    self.dropdown_broker_list.items = global_var.setting_broker_dropdown() + \
                                      anvil.server.call('select_brokers')
    self.dropdown_broker_list.selected_value = b_id
    self.dropdown_broker_list.raise_event('change')

  def text_broker_name_lost_focus(self, **event_args):
    """This method is called when the TextBox loses focus"""
    if self.text_broker_name.text == '':
      self.button_broker_create.enabled = False
    else:
      self.button_broker_create.enabled = True

  def button_broker_update_click(self, **event_args):
    """This method is called when the button is clicked"""
    b_id = \
    anvil.server.call('upsert_brokers', 
                      self.hidden_b_id.text, 
                      self.text_broker_name.text, 
                      self.dropdown_ccy.selected_value)
    self.dropdown_broker_list.items = global_var.setting_broker_dropdown() + \
                                      anvil.server.call('select_brokers')

  def button_broker_delete_click(self, **event_args):
    """This method is called when the button is clicked"""
    anvil.server.call('delete_brokers', self.hidden_b_id.text)
    self.dropdown_broker_list.items = global_var.setting_broker_dropdown() + \
                                      anvil.server.call('select_brokers')
    self.dropdown_broker_list.raise_event('change')

  def dropdown_broker_list_change(self, **event_args):
    """This method is called when an item is selected"""
    self.hidden_b_id.text = self.dropdown_broker_list.selected_value
    if self.dropdown_broker_list.selected_value == '':
      self.button_broker_update.enabled = False
      self.button_broker_delete.enabled = False
      self.button_broker_create.enabled = False
      self.text_broker_name.text = ''
    else:
      self.button_broker_update.enabled = True
      self.button_broker_delete.enabled = True
      self.button_broker_create.enabled = True
      self.text_broker_name.text = \
      anvil.server.call('get_broker_name', 
                        self.dropdown_broker_list.selected_value)
      self.dropdown_ccy.selected_value = \
      anvil.server.call('get_broker_ccy', 
                        self.dropdown_broker_list.selected_value)
  
  def dropdown_broker_list_show(self, **event_args):
    """This method is called when the DropDown is shown on the screen"""
    self.dropdown_broker_list.items = global_var.setting_broker_dropdown() + \
                                      anvil.server.call('select_brokers')
    self.dropdown_broker_list.raise_event('change')

  def dropdown_sub_templ_list_change(self, **event_args):
    """This method is called when an item is selected"""
    self.dropdown_sub_templ_list.items = anvil.server.call('get_submitted_templ_list')

  def dropdown_sub_templ_list_show(self, **event_args):
    """This method is called when the DropDown is shown on the screen"""
    self.dropdown_sub_templ_list.raise_event('change')

  def button_templ_edit_click(self, **event_args):
    """This method is called when the button is clicked"""
    to_be_enabled_templ_name = self.dropdown_sub_templ_list.selected_value
    templ_id = anvil.server.call('get_templ_id', 
                                 to_be_enabled_templ_name)
    anvil.server.call('update_templates_submit_flag', 
                      templ_id, 
                      False)
    """ Reflect the change in template dropdown """
    self.dropdown_sub_templ_list.items = anvil.server.call('get_submitted_templ_list')

    n = Notification("Template {templ_name} has been enabled for modification in the input section.".format(templ_name=to_be_enabled_templ_name))
    n.show()

