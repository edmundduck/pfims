from ._anvil_designer import form_mainTemplate
from anvil import *
import anvil.users
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from .. import global_var
from ..Admin.form_lv1_settings import form_lv1_settings
from ..Input.form_input_stock import form_input_stock
from ..Input.form_input_exp import form_input_exp
from ..Report.form_lv1_dashb import form_lv1_dashb
from ..Report.form_lv2_pnl_report import form_lv2_pnl_report
from ..Report.form_lv2_search_panel import form_lv2_search_panel
from ..Report.form_lv2_pnl_report import form_lv2_pnl_report
from ..Report.form_lv2_exp_list import form_lv2_exp_list
from ..Obsolete.form_sub2_tranx_report import form_sub2_tranx_report
from ..Debug.form_poc_main import form_poc_main

class form_main(form_mainTemplate):
  def __init__(self, **properties):
    # TODO - Move the logon logic to a new logon page
    anvil.users.login_with_form()
    userid = anvil.users.get_user().get_id()
    username = anvil.server.call('get_username', userid)
    
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run when the form opens.
    self.colpanel_input1.visible = False
    self.colpanel_input2.visible = False
    self.colpanel_rpt1.visible = False
    self.colpanel_rpt2.visible = False
    self.colpanel_rpt3.visible = False
    self.app_welcome_msg.text = "Welcome {username}".format(username=username)
  
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
    self.content_panel.clear()
    self.content_panel.add_component(form_lv1_dashb())
    self.colpanel_link_dashb.role = 'selected'

  def colpanel_link_input_click(self, **event_args):
    """This method is called when the link is clicked"""
    if self.colpanel_link_input.icon == 'fa:caret-right':
      self.colpanel_input1.visible = True
      self.colpanel_input2.visible = True
      self.colpanel_link_input.icon = 'fa:caret-down'
    elif self.colpanel_link_input.icon == 'fa:caret-down':
      self.colpanel_input1.visible = False
      self.colpanel_input2.visible = False
      self.colpanel_link_input.icon = 'fa:caret-right'

  def colpanel_link_reports_click(self, **event_args):
    """This method is called when the link is clicked"""
    if self.colpanel_link_reports.icon == 'fa:caret-right':
      self.colpanel_rpt1.visible = True
      self.colpanel_rpt2.visible = True
      self.colpanel_rpt3.visible = True
      self.colpanel_link_reports.icon = 'fa:caret-down'
    elif self.colpanel_link_reports.icon == 'fa:caret-down':
      self.colpanel_rpt1.visible = False
      self.colpanel_rpt2.visible = False
      self.colpanel_rpt3.visible = False
      self.colpanel_link_reports.icon = 'fa:caret-right'

  def colpanel_link_settings_click(self, **event_args):
    """This method is called when the link is clicked"""
    self.reset_link_status()
    self.colpanel_link_settings.role = 'selected'
    self.content_panel.clear()
    self.content_panel.add_component(form_lv1_settings())

  def colpanel_lv2link_tranx_list_click(self, **event_args):
    """This method is called when the link is clicked"""
    self.reset_link_status()
    self.colpanel_link_reports.role = 'selected'
    self.colpanel_lv2link_tranx_list.role = 'selected'
    self.content_panel.clear()
    self.content_panel.add_component(form_lv2_search_panel(global_var.form_lv2_tranx_list()))

  def colpanel_lv2link_pnl_report_click(self, **event_args):
    """This method is called when the link is clicked"""
    self.reset_link_status()
    self.colpanel_link_reports.role = 'selected'
    self.colpanel_lv2link_pnl_report.role = 'selected'
    self.content_panel.clear()
    self.content_panel.add_component(form_lv2_search_panel(global_var.form_lv2_pnl_report()))

  def colpanel_lv2link_exp_list_click(self, **event_args):
    """This method is called when the link is clicked"""
    self.reset_link_status()
    self.colpanel_link_reports.role = 'selected'
    self.colpanel_lv2link_exp_list.role = 'selected'
    self.content_panel.clear()
    self.content_panel.add_component(form_lv2_exp_list())

  def colpanel_lv2link_input_stock_click(self, **event_args):
    """This method is called when the link is clicked"""
    self.reset_link_status()
    self.colpanel_link_input.role = 'selected'
    self.colpanel_lv2link_input_stock.role = 'selected'
    self.content_panel.clear()
    self.content_panel.add_component(form_input_stock())

  def colpanel_lv2link_input_exp_click(self, **event_args):
    """This method is called when the link is clicked"""
    self.reset_link_status()
    self.colpanel_link_input.role = 'selected'
    self.colpanel_lv2link_input_exp.role = 'selected'
    self.content_panel.clear()
    self.content_panel.add_component(form_input_exp())
    
  def column_panel_2_link_tranx_list_click(self, **event_args):
    """This method is called when the link is clicked"""
    self.reset_link_status()
    self.content_panel.clear()
    self.content_panel.add_component(form_sub2_tranx_report())

  def poc_link_click(self, **event_args):
    """This method is called when the link is clicked"""
    self.content_panel.clear()
    self.content_panel.add_component(form_poc_main())

  def app_logout_click(self, **event_args):
    """This method is called when the link is clicked"""
    # TODO - Improve the logic later
    anvil.users.logout()
    self.app_welcome_msg.text = ""
    self.content_panel.clear()
    self.column_panel.clear()
    open_form('form_main')

