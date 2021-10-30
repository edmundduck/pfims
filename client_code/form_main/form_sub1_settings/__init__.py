from ._anvil_designer import form_sub1_settingsTemplate
from anvil import *

class form_sub1_settings(form_sub1_settingsTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run when the form opens.