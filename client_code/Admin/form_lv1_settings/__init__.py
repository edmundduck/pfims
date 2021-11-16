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
    self.dropdown_ccy.items = global_var.setting_ccy_dropdown()
    self.dropdown_interval.items = global_var.search_interval_dropdown()

    settings = anvil.server.call('select_settings')
    self.dropdown_ccy.selected_value = settings.get('default_ccy')
    self.dropdown_interval.selected_value = settings.get('default_interval')
    self.time_datefrom.date = settings.get('default_datefrom')
    self.time_dateto.date = settings.get('default_dateto')
    
    if self.dropdown_interval.selected_value != "SDR":
      self.time_datefrom.enabled = False
      self.time_dateto.enabled = False
    
    if self.text_pfm_name.text == '':
      self.button_pfm_create.enabled = False
      
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
                      self.dropdown_ccy.selected_value, 
                      self.dropdown_interval.selected_value, 
                      self.time_datefrom.date, 
                      self.time_dateto.date)

  def button_pfm_create_click(self, **event_args):
    """This method is called when the button is clicked"""
    pass

  def text_pfm_name_lost_focus(self, **event_args):
    """This method is called when the TextBox loses focus"""
    if self.text_pfm_name.text == '':
      self.button_pfm_create.enabled = False
    else:
      self.button_pfm_create.enabled = True


