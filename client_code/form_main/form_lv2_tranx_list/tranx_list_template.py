from ._anvil_designer import tranx_list_templateTemplate
from anvil import *
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

class tranx_list_template(tranx_list_templateTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run when the form opens.
    if self.item['pnl'] < 0:
      self.foreground = 'Red'
    else:
      self.foreground = 'Green'