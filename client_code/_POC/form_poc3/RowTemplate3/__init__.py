from ._anvil_designer import RowTemplate3Template
from anvil import *
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
        v.highlight_when_invalid(self.text_box_1)
        