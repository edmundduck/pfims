from ._anvil_designer import form_poc2Template
from anvil import *
import anvil.server
from datetime import date, datetime

class form_poc2(form_poc2Template):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run when the form opens.
    symbol_list = []
    self.rpt_panel.items = anvil.server.call('select_journals', date(2000,1,1), date.today(), symbol_list)

    self.rpt_panel.add_event_handler('x-vis', self.setvisibility)
    self.rpt_panel.get_event_handlers('x-vis')
    
  def setvisibility(self, **properties):
    self.data_grid.visible = False