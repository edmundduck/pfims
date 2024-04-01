from ._anvil_designer import UnitTestMainFormTemplate
from anvil import *
import anvil.server
from ....Controllers import UnitTestController
from ....CustomComponents.TestItem import TestItem

class UnitTestMainForm(UnitTestMainFormTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        # Any code you write here will run before the form opens.
        for test_entity in UnitTestController.retrieve_test_cases():
            item = TestItem()
            item.title = test_entity
            item.modules = test_entity
            self.colpanel_testcases.add_component(item)
