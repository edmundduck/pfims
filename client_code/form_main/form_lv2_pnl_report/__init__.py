from ._anvil_designer import form_lv2_pnl_reportTemplate
from anvil import *
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

class form_lv2_pnl_report(form_lv2_pnl_reportTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run when the form opens.
    self.data_grid.rows_per_page = self.dropdown_displayrow.selected_value
    self.rpt_panel.add_event_handler('x-update', self.update_pnl_list)

  def dropdown_displayrow_change(self, **event_args):
    """This method is called when an item is selected"""
    self.data_grid.rows_per_page = self.dropdown_displayrow.selected_value

  def update_pnl_list(self, date, mode, action, **event_args):
    self.rpt_panel.items = \
    anvil.server.call('update_pnl_list', 
                      self.rpt_panel.items, 
                      date, 
                      mode, 
                      action)