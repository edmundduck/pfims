from ._anvil_designer import UnitTestMainFormTemplate
from anvil import *
from ....Controllers import UnitTestController
import anvil.server

class UnitTestMainForm(UnitTestMainFormTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        # Any code you write here will run before the form opens.
        print(UnitTestController.retrieve_test_cases())
        self.test_item_1.title = "Test LabelDAModule"
        self.test_item_1.test_function = ["test_generate_labels_list_normal_case"]