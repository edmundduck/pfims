from ._anvil_designer import form_sub2_tranx_reportsTemplate
from anvil import *
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

class form_sub2_tranx_reports(form_sub2_tranx_reportsTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run when the form opens.
    self.tranx_rpt_time_dropdown.items = [("Please choose one", ""), 
                                          ("Last 1 Month", "L1M"), 
                                          ("Last 3 Month", "L3M"),
                                          ("Last 6 Month", "L6M"),
                                          ("Last 1 Year", "L1Y"),
                                          ("Year to Date", "YTD"),
                                          ("Self Defined Range", "SDR")]

    if self.tranx_rpt_time_dropdown.selected_value != "SDR":
      self.tranx_rpt_time_from_date.visible = False
      self.tranx_rpt_time_to_date.visible = False
      self.tranx_rpt_time_to_label.visible = False
      
  def tranx_rpt_time_dropdown_change(self, **event_args):
    """This method is called when an item is selected"""
    if self.tranx_rpt_time_dropdown.selected_value != "SDR":
      self.tranx_rpt_time_from_date.visible = False
      self.tranx_rpt_time_to_date.visible = False
      self.tranx_rpt_time_to_label.visible = False
    else:
      self.tranx_rpt_time_from_date.visible = True
      self.tranx_rpt_time_to_date.visible = True
      self.tranx_rpt_time_to_label.visible = True
