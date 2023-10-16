from ._anvil_designer import LoginFormTemplate
from anvil import *
import anvil.users
import anvil.server
from ..Utils import Constants as const
from ..Utils import Routing

class LoginForm(LoginFormTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

    def app_logout_click(self, **event_args):
        """This method is called when the link is clicked"""
        # TODO - Improve the logic later
        anvil.users.logout()
        self.app_welcome_msg.text = ""
        self.content_panel.clear()
        self.column_panel.clear()
        open_form('form_main')
