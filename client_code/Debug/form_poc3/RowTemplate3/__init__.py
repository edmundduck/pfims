from ._anvil_designer import RowTemplate3Template
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from ....Utils.Validation import Validator

class RowTemplate3(RowTemplate3Template):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        # Any code you write here will run before the form opens.
        self.add_event_handler('x-validate', self.validate)

    def validate(self, **properties):
        v = Validator()
        v.display_when_invalid(self.parent.parent.parent.valerror)
        v.require_text_field(self.text_box_1, self.parent.parent.parent.valerror1, False)
        v.highlight_when_invalid(self.text_box_1, 'rgb(245,135,200)', self.text_box_1.background)
        