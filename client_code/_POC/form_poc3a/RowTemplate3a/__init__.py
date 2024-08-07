from ._anvil_designer import RowTemplate3aTemplate
from anvil import *
import anvil.server
from ....Utils.Validation import Validator

class RowTemplate3a(RowTemplate3aTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        # Any code you write here will run before the form opens.
