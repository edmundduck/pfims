from ._anvil_designer import TestItemTemplate
from anvil import *
import anvil.server
from ...Controllers import UnitTestController

class TestItem(TestItemTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        # Any code you write here will run before the form opens.
        self.result_success = 0
        self.result_failure = 0
        self.error_msg.text = None

    def flow_panel_1_show(self, **event_args):
        """This method is called when the FlowPanel is shown on the screen"""
        self.label.text = self.title
        self.error_msg.visible = False
        self._validate()

    def button_run_click(self, **event_args):
        """This method is called when the button is clicked"""
        result = UnitTestController.submit_server_test_cases(self.test_function)
        if result.get(self.title):
            self.result_success = result.get(self.title).get('success_count')
            self.result_failure = result.get(self.title).get('failure_count')
            print(f"failure? {result.get(self.title).get('failure_messages')}")
            if result.get(self.title).get('failure_messages'):
                self.error_msg.text = "\n".join(result.get(self.title).get('failure_messages'))
                self.error_msg.visible = True
            else:
                self.error_msg.text = None
                self.error_msg.visible = False
                
        self.result.text = f"Success ({self.result_success}) / Failure ({self.result_failure})"

    def _validate(self):
        pass