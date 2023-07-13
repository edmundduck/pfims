from ._anvil_designer import form_poc2Template
from anvil import *
import anvil.users
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from datetime import date, datetime

class form_poc2(form_poc2Template):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run when the form opens.
    self.userid = anvil.server.call('get_current_userid')
    symbol_list = []
    self.rpt_panel.items = anvil.server.call('select_journals', self.userid, date(2000,1,1), date.today(), symbol_list)

    self.rpt_panel.add_event_handler('x-vis', self.setvisibility)
    self.rpt_panel.get_event_handlers('x-vis')
    
  def setvisibility(self, **properties):
    print("setvisibility")
    self.data_grid.visible = False