from ._anvil_designer import form_poc_mainTemplate
from anvil import *
import anvil.users
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from ..form_poc1 import form_poc1
from ..form_poc2 import form_poc2
from ..form_poc3 import form_poc3
from ..form_poc3a import form_poc3a
from ..form_poc4 import form_poc4
from ...App import Global as glo

class form_poc_main(form_poc_mainTemplate):
    subform = None
  
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)
    
        # Any code you write here will run when the form opens.
        self.drop_down_1.items = [
            ('form_poc1 - Tags', 'form_poc1'),
            ('form_poc2 - Repeating items', 'form_poc2'),
            ('form_poc3 - Parent calls child validation', 'form_poc3'),
            ('form_poc3a - Child validation done in parent', 'form_poc3a'),
            ('form_poc4 - File import', 'form_poc4')
        ]

    def button_select_click(self, **event_args):
        """This method is called when the button is clicked"""
        self.test_panel.clear()
        if self.drop_down_1.selected_value == "form_poc1":
            self.test_panel.add_component(form_poc1())
        elif self.drop_down_1.selected_value == "form_poc2":
            self.test_panel.add_component(form_poc2())
        elif self.drop_down_1.selected_value == "form_poc3":
            self.test_panel.add_component(form_poc3())
        elif self.drop_down_1.selected_value == "form_poc3a":
            self.test_panel.add_component(form_poc3a())
        elif self.drop_down_1.selected_value == "form_poc4":
            self.test_panel.add_component(form_poc4())