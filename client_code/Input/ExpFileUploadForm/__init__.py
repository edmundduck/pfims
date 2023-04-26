from ._anvil_designer import ExpFileUploadFormTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from ...App import Routing

class ExpFileUploadForm(ExpFileUploadFormTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run when the form opens.

  def button_upload_filter_click(self, **event_args):
      """This method is called when the button is clicked"""
      Routing.open_upload_filter_form(self)
