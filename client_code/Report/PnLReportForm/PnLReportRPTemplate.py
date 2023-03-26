from ._anvil_designer import PnLReportRPTemplateTemplate
from anvil import *
import anvil.users
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from ... import Global as glo

# About amount formatting in design page's data binding field
# Refer to https://anvil.works/forum/t/formatting-float-fields-in-a-datagrid/6796

class PnLReportRPTemplate(PnLReportRPTemplateTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run when the form opens.
    if self.item['pnl'] < 0:
      self.foreground = 'Red'
    else:
      self.foreground = 'Green'
      
    if self.item['mode'] == glo.pnl_list_yr_mode():
      self.button_exp.visible = True
    elif self.item['mode'] == glo.pnl_list_mth_mode():
      self.button_exp.visible = True
    elif self.item['mode'] == glo.pnl_list_day_mode():
      self.button_exp.visible = False
      
    if self.item['action'] == glo.pnl_list_expand_icon():
      self.button_exp.icon = glo.pnl_list_expand_icon()
    elif self.item['action'] == glo.pnl_list_shrink_icon():
      self.button_exp.icon = glo.pnl_list_shrink_icon()

  def button_exp_click(self, **event_args):
    """This method is called when the button is clicked"""
    action = self.button_exp.icon
    self.parent.raise_event('x-update', date=self.item['sell_date'], mode=self.item['mode'], action=action)
    
