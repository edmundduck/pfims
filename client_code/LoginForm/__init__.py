from ._anvil_designer import LoginFormTemplate
from anvil import *
import anvil.server
import anvil.users
from ..Utils import Routing

class LoginForm(LoginFormTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

    def button_login_click(self, **event_args):
        """This method is called when the button is clicked"""
        from .. import StartupModule
        anvil.users.login_with_form()
        StartupModule.startup()

    def button_signup_click(self, **event_args):
        """This method is called when the button is clicked"""
        pass

