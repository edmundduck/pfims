from ._anvil_designer import form_sub2_tranx_reportsTemplate
from anvil import *
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from datetime import date

class form_sub2_tranx_reports(form_sub2_tranx_reportsTemplate):
  interval_list = [("[Interval]", ""), 
                  ("Last 1 Month", "L1M"), 
                  ("Last 3 Month", "L3M"),
                  ("Last 6 Month", "L6M"),
                  ("Last 1 Year", "L1Y"),
                  ("Year to Date", "YTD"),
                  ("Self Defined Range", "SDR")]
  
  symbol_list = [("[Symbol]", "")]
  
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run when the form opens.
    self.tranx_rpt_time_dropdown.items = self.interval_list
    self.tranx_rpt_symbol_dropdown.items = self.symbol_list

    if self.tranx_rpt_time_dropdown.selected_value != "SDR":
      self.tranx_rpt_time_from_date.enabled = False
      self.tranx_rpt_time_to_date.enabled = False
      self.tranx_rpt_time_to_label.enabled = False
      
  def tranx_rpt_time_dropdown_change(self, **event_args):
    """This method is called when an item is selected"""
    if self.tranx_rpt_time_dropdown.selected_value != "SDR":
      self.tranx_rpt_time_from_date.enabled = False
      self.tranx_rpt_time_to_date.enabled = False
      self.tranx_rpt_time_to_label.enabled = False
      self.tranx_rpt_symbol_dropdown.items = self.symbol_list + anvil.server.call('get_symbol_dropdown_items', 
                                                               date.today(), 
                                                               anvil.server.call('get_start_date', 
                                                                                 date.today(), 
                                                                                 self.tranx_rpt_time_dropdown.selected_value))
    else:
      self.tranx_rpt_time_from_date.enabled = True
      self.tranx_rpt_time_to_date.enabled = True
      self.tranx_rpt_time_to_label.enabled = True
      self.tranx_rpt_symbol_dropdown.items = self.symbol_list + anvil.server.call('get_symbol_dropdown_items', 
                                                               self.tranx_rpt_time_to_date.date, 
                                                               self.tranx_rpt_time_from_date.date)

  def tranx_rpt_time_from_date_change(self, **event_args):
    """This method is called when the selected date changes"""
    self.tranx_rpt_symbol_dropdown.items = self.symbol_list + anvil.server.call('get_symbol_dropdown_items', 
                                                              self.tranx_rpt_time_to_date.date, 
                                                              self.tranx_rpt_time_from_date.date)

  def tranx_rpt_time_to_date_change(self, **event_args):
    """This method is called when the selected date changes"""
    self.tranx_rpt_symbol_dropdown.items = self.symbol_list + anvil.server.call('get_symbol_dropdown_items', 
                                                              self.tranx_rpt_time_to_date.date, 
                                                              self.tranx_rpt_time_from_date.date)

  def tranx_rpt_button_plus_click(self, **event_args):
    """This method is called when the button is clicked"""
    b = Button(text=self.tranx_rpt_symbol_dropdown.selected_value,
               icon='fa:minus',
               foreground="White",
               background="Blue")
    b.add_event_handler('click', self.remove_symbol_button)
    self.flow_panel_3.add_component(b)

  def remove_symbol_button(self, **event_args):
    self.remove_from_parent()


