from ._anvil_designer import LoginFormTemplate
from anvil import *
import anvil.server
import anvil.users
from ..Utils import Routing

class LoginForm(LoginFormTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        # Cannot call Routing method here
        from ..Forms.Introduction.AppIntroForm import AppIntroForm
        self.content_panel.add_component(AppIntroForm())

    def button_login_click(self, **event_args):
        """This method is called when the button is clicked"""
        from .. import StartupModule
        anvil.users.login_with_form(allow_cancel=True)
        StartupModule.startup()

    def button_signup_click(self, **event_args):
        """This method is called when the button is clicked"""
        pass

    def button_feature_click(self, **event_args):
        """This method is called when the button is clicked"""
        Routing.open_intro_feature_form(self)

    def button_price_click(self, **event_args):
        """This method is called when the button is clicked"""
        Routing.open_intro_pricing_form(self)

    def button_resource_click(self, **event_args):
        """This method is called when the button is clicked"""
        Routing.open_intro_resource_form(self)

    def button_contact_click(self, **event_args):
        """This method is called when the button is clicked"""
        Routing.open_intro_contact_form(self)

    def image_logo_mouse_up(self, x, y, button, **event_args):
        """This method is called when a mouse button is released on this component"""
        Routing.open_intro_base_form(self)
