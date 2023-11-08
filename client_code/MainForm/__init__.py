from ._anvil_designer import MainFormTemplate
from anvil import *
import anvil.users
from ..Controllers import MainFormController
from ..Utils import Routing

class MainForm(MainFormTemplate):
    investment_visgrp = []
    expense_visgrp = []
    
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)
        
        # Any code you write here will run when the form opens.
        from .. import Global
        self.investment_visgrp = [self.colpanel_link_input_stock.visible, self.colpanel_link_tranx_list.visible, self.colpanel_link_pnl_report.visible]
        self.expense_visgrp = [self.colpanel_link_input_exp.visible, self.colpanel_link_exp_list.visible, self.colpanel_link_exp_analysis.visible]
        self.app_welcome_msg.text = "Welcome {username}".format(username=Global.email)
        self.label_version.text = MainFormController.visible_test_env_label()
        self.poc_link.visible = MainFormController.visible_poc_link()
        self.investment_visgrp = [False] *3
        self.expense_visgrp = [False] *3

    def reset_link_status(self, **event_args):
        self.colpanel_link_input_stock.role, \
        self.colpanel_link_input_exp.role, \
        self.colpanel_link_tranx_list.role, \
        self.colpanel_link_pnl_report.role, \
        self.colpanel_link_exp_list.role, \
        self.poc_link.role \
        = [None]*6

    def colpanel_link_dashb_click(self, **event_args):
        """This method is called when the link is clicked"""
        self.reset_link_status()
        self.colpanel_link_dashb.role = MainFormController.switch_role(self.colpanel_link_dashb.role)
        Routing.open_dashboard_form(self)

    def colpanel_link_settings_click(self, **event_args):
        """This method is called when the link is clicked"""
        self.reset_link_status()
        self.colpanel_link_settings.role = MainFormController.switch_role(self.colpanel_link_settings.role)
        Routing.open_setting_form(self)

    def colpanel_link_tranx_list_click(self, **event_args):
        """This method is called when the link is clicked"""
        self.reset_link_status()
        self.colpanel_link_tranx_list.role = MainFormController.switch_role(self.colpanel_link_tranx_list.role)
        Routing.open_tranx_list_form(self)

    def colpanel_link_pnl_report_click(self, **event_args):
        """This method is called when the link is clicked"""
        self.reset_link_status()
        self.colpanel_link_pnl_report.role = MainFormController.switch_role(self.colpanel_link_pnl_report.role)
        Routing.open_pnl_report_form(self)

    def colpanel_link_exp_list_click(self, **event_args):
        """This method is called when the link is clicked"""
        self.reset_link_status()
        self.colpanel_link_exp_list.role = MainFormController.switch_role(self.colpanel_link_exp_list.role)
        Routing.open_exp_list_form(self)

    def colpanel_link_exp_analysis_click(self, **event_args):
        """This method is called when the link is clicked"""
        self.reset_link_status()
        self.colpanel_link_exp_analysis.role = MainFormController.switch_role(self.colpanel_link_exp_analysis.role)
        Routing.open_exp_analysis_form(self)

    def colpanel_link_input_stock_click(self, **event_args):
        """This method is called when the link is clicked"""
        self.reset_link_status()
        self.colpanel_link_input_stock.role = MainFormController.switch_role(self.colpanel_link_input_stock.role)
        Routing.open_stock_txn_input_form(self)

    def colpanel_link_input_exp_click(self, **event_args):
        """This method is called when the link is clicked"""
        self.reset_link_status()
        self.colpanel_link_input_exp.role = MainFormController.switch_role(self.colpanel_link_input_exp.role)
        Routing.open_exp_input_form(self)
    
    def poc_link_click(self, **event_args):
        """This method is called when the link is clicked"""
        self.reset_link_status()
        self.poc_link.role = MainFormController.switch_role(self.poc_link.role)
        Routing.open_poc_main_form(self)

    def colpanel_link_investment_click(self, **event_args):
        """This method is called when the link is clicked"""
        self.reset_link_status()
        self.colpanel_link_input_stock.visible, self.colpanel_link_tranx_list.visible, self.colpanel_link_pnl_report.visible = [True] *3
        self.colpanel_link_input_exp.visible, self.colpanel_link_exp_list.visible, self.colpanel_link_exp_analysis.visible = [False] *3

    def colpanel_link_expense_click(self, **event_args):
        """This method is called when the link is clicked"""
        self.reset_link_status()
        self.colpanel_link_input_stock.visible, self.colpanel_link_tranx_list.visible, self.colpanel_link_pnl_report.visible = [False] *3
        self.colpanel_link_input_exp.visible, self.colpanel_link_exp_list.visible, self.colpanel_link_exp_analysis.visible = [True] *3

    def app_logout_click(self, **event_args):
        """This method is called when the link is clicked"""
        from .. import StartupModule
        anvil.users.logout()
        StartupModule.startup()
