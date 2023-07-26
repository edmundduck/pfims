from ._anvil_designer import MainFormTemplate
from anvil import *
import anvil.users
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from ..Utils import Constants as const
from ..Utils import Routing

class MainForm(MainFormTemplate):
    def __init__(self, **properties):
        # TODO - Move the logon logic to a new logon page
        anvil.users.login_with_form()
        username = anvil.server.call('get_current_username')
        anvil.server.call('set_user_logging_level')
        
        # Set Form properties and Data Bindings.
        self.init_components(**properties)
        
        # Any code you write here will run when the form opens.
        self.colpanel_input1.visible = False
        self.colpanel_input2.visible = False
        self.colpanel_rpt1.visible = False
        self.colpanel_rpt2.visible = False
        self.colpanel_rpt3.visible = False
        self.app_welcome_msg.text = "Welcome {username}".format(username=username)
        self.label_version.text = anvil.app.environment.name if anvil.app.environment.name in 'Dev' else None

    def reset_link_status(self, **event_args):
        self.colpanel_link_dashb.role = ''
        self.colpanel_link_input.role = ''
        self.colpanel_link_reports.role = ''
        self.colpanel_link_settings.role = ''
        self.colpanel_lv2link_input_stock.role = ''
        self.colpanel_lv2link_input_exp.role = ''
        self.colpanel_lv2link_tranx_list.role = ''
        self.colpanel_lv2link_pnl_report.role = ''
        self.colpanel_lv2link_exp_list.role = ''

    def colpanel_link_dashb_click(self, **event_args):
        """This method is called when the link is clicked"""
        self.reset_link_status()
        self.colpanel_link_dashb.role = 'selected'
        Routing.open_dashboard_form(self)

    def colpanel_link_input_click(self, **event_args):
        """This method is called when the link is clicked"""
        if self.colpanel_link_input.icon == const.Icons.MENU_SHRINK:
            self.colpanel_input1.visible = True
            self.colpanel_input2.visible = True
            self.colpanel_link_input.icon = const.Icons.MENU_EXPAND
        elif self.colpanel_link_input.icon == const.Icons.MENU_EXPAND:
            self.colpanel_input1.visible = False
            self.colpanel_input2.visible = False
            self.colpanel_link_input.icon = const.Icons.MENU_SHRINK

    def colpanel_link_reports_click(self, **event_args):
        """This method is called when the link is clicked"""
        if self.colpanel_link_reports.icon == const.Icons.MENU_SHRINK:
            self.colpanel_rpt1.visible = True
            self.colpanel_rpt2.visible = True
            self.colpanel_rpt3.visible = True
            self.colpanel_link_reports.icon = const.Icons.MENU_EXPAND
        elif self.colpanel_link_reports.icon == const.Icons.MENU_EXPAND:
            self.colpanel_rpt1.visible = False
            self.colpanel_rpt2.visible = False
            self.colpanel_rpt3.visible = False
            self.colpanel_link_reports.icon = const.Icons.MENU_SHRINK

    def colpanel_link_settings_click(self, **event_args):
        """This method is called when the link is clicked"""
        self.reset_link_status()
        self.colpanel_link_settings.role = 'selected'
        Routing.open_setting_form(self)

    def colpanel_lv2link_tranx_list_click(self, **event_args):
        """This method is called when the link is clicked"""
        self.reset_link_status()
        self.colpanel_link_reports.role = 'selected'
        self.colpanel_lv2link_tranx_list.role = 'selected'
        Routing.open_tranx_list_form(self)

    def colpanel_lv2link_pnl_report_click(self, **event_args):
        """This method is called when the link is clicked"""
        self.reset_link_status()
        self.colpanel_link_reports.role = 'selected'
        self.colpanel_lv2link_pnl_report.role = 'selected'
        Routing.open_pnl_report_form(self)

    def colpanel_lv2link_exp_list_click(self, **event_args):
        """This method is called when the link is clicked"""
        self.reset_link_status()
        self.colpanel_link_reports.role = 'selected'
        self.colpanel_lv2link_exp_list.role = 'selected'
        Routing.open_exp_list_form(self)

    def colpanel_lv2link_input_stock_click(self, **event_args):
        """This method is called when the link is clicked"""
        self.reset_link_status()
        self.colpanel_link_input.role = 'selected'
        self.colpanel_lv2link_input_stock.role = 'selected'
        Routing.open_stock_input_form(self)

    def colpanel_lv2link_input_exp_click(self, **event_args):
        """This method is called when the link is clicked"""
        self.reset_link_status()
        self.colpanel_link_input.role = 'selected'
        self.colpanel_lv2link_input_exp.role = 'selected'
        Routing.open_exp_input_form(self)
    
    def poc_link_click(self, **event_args):
        """This method is called when the link is clicked"""
        Routing.open_poc_main_form(self)

    def app_logout_click(self, **event_args):
        """This method is called when the link is clicked"""
        # TODO - Improve the logic later
        anvil.users.logout()
        self.app_welcome_msg.text = ""
        self.content_panel.clear()
        self.column_panel.clear()
        open_form('form_main')

