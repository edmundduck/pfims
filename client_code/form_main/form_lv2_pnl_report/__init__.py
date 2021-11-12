from ._anvil_designer import form_lv2_pnl_reportTemplate
from anvil import *
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from datetime import date

class form_lv2_pnl_report(form_lv2_pnl_reportTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run when the form opens.
    self.data_grid.rows_per_page = self.tranx_rpt_displayrow_dropdown.selected_value

  def tranx_rpt_displayrow_dropdown_change(self, **event_args):
    """This method is called when an item is selected"""
    self.data_grid.rows_per_page = self.tranx_rpt_displayrow_dropdown.selected_value
