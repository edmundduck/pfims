from ._anvil_designer import form_sub2_tranx_reportsTemplate
from anvil import *
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from datetime import date

class form_sub2_tranx_reports(form_sub2_tranx_reportsTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run when the form opens.
    self.tranx_rpt_time_dropdown.items = [("[Interval]", ""), 
                                          ("Last 1 Month", "L1M"), 
                                          ("Last 3 Month", "L3M"),
                                          ("Last 6 Month", "L6M"),
                                          ("Last 1 Year", "L1Y"),
                                          ("Year to Date", "YTD"),
                                          ("Self Defined Range", "SDR")]
    self.tranx_rpt_symbol_dropdown.items = [("[Symbol]", "")]

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
      self.tranx_rpt_symbol_dropdown.items = self.tranx_rpt_symbol_dropdown.items + anvil.server.call('get_symbol_dropdown_items', 
                                                               date.today(), 
                                                               anvil.server.call('get_start_date', 
                                                                                 date.today(), 
                                                                                 self.tranx_rpt_time_dropdown.selected_value))
    else:
      self.tranx_rpt_time_from_date.enabled = True
      self.tranx_rpt_time_to_date.enabled = True
      self.tranx_rpt_time_to_label.enabled = True
      self.tranx_rpt_symbol_dropdown.items = self.tranx_rpt_symbol_dropdown.items + anvil.server.call('get_symbol_dropdown_items', 
                                                               self.tranx_rpt_time_to_date.date, 
                                                               self.tranx_rpt_time_from_date.date)