from ._anvil_designer import TestItemTemplate
from anvil import *
import anvil.server

class TestItem(TestItemTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        # Any code you write here will run before the form opens.
        self.label.text = self.title
        self.error_msg.visible = False
        self._validate()

    def button_run_click(self, **event_args):
        """This method is called when the button is clicked"""
        for f in self.test_function:
            if anvil.server.call(f):
                self.result_success += 1
            else:
                self.result_failure += 1
        self.result.text = f"Success ({self.result_success}) / Failure ({self.result_failure})"

    def _validate(self):
        print(self.test_function)
        if isinstance(self.test_function, (list, tuple)):
            self.button_run.enabled = True
        else:
            self.button_run.enabled = False
            self.error_msg.visible = True
            self.error_msg.text = "Error: test_function properties must be either List or Tuple."
