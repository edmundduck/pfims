from ._anvil_designer import pnl_report_templateTemplate
from anvil import *
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from ... import global_var

class pnl_report_template(pnl_report_templateTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run when the form opens.
    if self.item['pnl'] < 0:
      self.foreground = 'Red'
    else:
      self.foreground = 'Green'
      
    if self.item['mode'] == global_var.pnl_list_yr_mode():
      self.button_exp.visible = True
    elif self.item['mode'] == global_var.pnl_list_mth_mode():
      self.button_exp.visible = False
    elif self.item['mode'] == global_var.pnl_list_day_mode():
      self.button_exp.visible = False

  def button_exp_click(self, **event_args):
    """This method is called when the button is clicked"""
    anvil.server.call('update_pnl_list', )

