from ._anvil_designer import form_poc1Template
from anvil import *
import anvil.users
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from ...Utils import Constants as const

class form_poc1(form_poc1Template):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)
    
        # Any code you write here will run when the form opens.
        """
        #dict_test = {'a': 1, 'b': 2}
        dict_test = {}
        a, b = dict_test.get('a', [0, 0])
        print("a={}, b={}".format(a, b))
        """
      
    def create_tag(self, txt):
        self.panel_tags.add_component(Button(text=txt, background=const.ColorSchemes.THEME_PRIM, foreground=const.ColorSchemes.THEME_WHITE, font_size=9, icon=const.Icons.REMOVE, icon_align='left', spacing_above='None', spacing_below='None'))

    def text_taglabel_pressed_enter(self, **event_args):
        """This method is called when the user presses Enter in this text box"""
        self.create_tag(self.text_taglabel.text)
