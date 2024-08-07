from ._anvil_designer import MainFormTemplate
from anvil import *
import anvil.server
import anvil.users
from ..Controllers import MainFormController
from ..Utils import Routing

class MainForm(MainFormTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)
        
        # Any code you write here will run when the form opens.
        from .. import Global
        self.app_welcome_msg.text = "{username}".format(username=Global.email)
        self.label_version.visible = MainFormController.visible_test_env_label()
        self.button_poc.visible = MainFormController.visible_poc_link()
        self.button_unittest.visible = MainFormController.visible_unittest_link()

    def reset_link_status(self, **event_args):
        self.button_inv_input.role, \
        self.button_inv_list.role, \
        self.button_inv_pnl.role, \
        self.button_exp_input.role, \
        self.button_exp_list.role, \
        self.button_unittest.role, \
        self.button_poc.role \
        = [None]*7

    def colpanel_link_dashb_click(self, **event_args):
        """This method is called when the link is clicked"""
        self.reset_link_status()
        # self.colpanel_link_dashb.role = MainFormController.switch_role(self.colpanel_link_dashb.role)
        Routing.open_dashboard_form(self)

    def colpanel_link_settings_click(self, **event_args):
        """This method is called when the link is clicked"""
        self.reset_link_status()
        # self.colpanel_link_settings.role = MainFormController.switch_role(self.colpanel_link_settings.role)
        Routing.open_setting_form(self)

    def button_inv_input_click(self, **event_args):
        """This method is called when the button is clicked"""
        self.reset_link_status()
        # self.button_inv_input.role = MainFormController.switch_role(self.button_inv_input.role)
        Routing.open_stock_txn_input_form(self)

    def button_inv_list_click(self, **event_args):
        """This method is called when the button is clicked"""
        self.reset_link_status()
        # self.button_inv_list.role = MainFormController.switch_role(self.button_inv_list.role)
        Routing.open_tranx_list_form(self)

    def button_inv_pnl_click(self, **event_args):
        """This method is called when the button is clicked"""
        self.reset_link_status()
        # self.button_inv_pnl.role = MainFormController.switch_role(self.button_inv_pnl.role)
        Routing.open_pnl_report_form(self)

    def button_exp_input_click(self, **event_args):
        """This method is called when the button is clicked"""
        self.reset_link_status()
        # self.button_exp_input.role = MainFormController.switch_role(self.button_exp_input.role)
        Routing.open_exp_input_form(self)

    def button_exp_list_click(self, **event_args):
        """This method is called when the button is clicked"""
        self.reset_link_status()
        # self.button_exp_list.role = MainFormController.switch_role(self.button_exp_list.role)
        Routing.open_exp_list_form(self)

    def button_exp_analysis_click(self, **event_args):
        """This method is called when the button is clicked"""
        self.reset_link_status()
        # self.button_exp_analysis.role = MainFormController.switch_role(self.button_exp_analysis.role)
        Routing.open_exp_analysis_form(self)

    def button_unittest_click(self, **event_args):
        """This method is called when the button is clicked"""
        self.reset_link_status()
        # self.button_unittest.role = MainFormController.switch_role(self.button_unittest.role)
        Routing.open_unittest_main_form(self)

    def button_poc_click(self, **event_args):
        """This method is called when the button is clicked"""
        self.reset_link_status()
        # self.button_poc.role = MainFormController.switch_role(self.button_poc.role)
        Routing.open_poc_main_form(self)

    def app_logout_click(self, **event_args):
        """This method is called when the link is clicked"""
        from .. import StartupModule
        anvil.users.logout()
        StartupModule.startup()
