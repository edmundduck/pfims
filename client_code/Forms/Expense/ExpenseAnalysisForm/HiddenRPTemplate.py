from ._anvil_designer import HiddenRPTemplateTemplate
from anvil import *
import anvil.server

class HiddenRPTemplate(HiddenRPTemplateTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)
