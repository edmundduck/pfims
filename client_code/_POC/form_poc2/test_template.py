from ._anvil_designer import test_templateTemplate
from anvil import *
import anvil.users
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from ...Utils import Constants as const

class test_template(test_templateTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run when the form opens.
    if self.item['pnl'] < 0:
      self.foreground = const.ColorSchemes.AMT_NEG
    else:
      self.foreground = const.ColorSchemes.AMT_POS

  def button_vis_click(self, **event_args):
    """This method is called when the button is clicked"""
    self.visible = False
    self.parent.raise_event_on_children('x-vis')

