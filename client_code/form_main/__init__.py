from ._anvil_designer import form_mainTemplate
from anvil import *
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from .form_sub1_dashb import form_sub1_dashb
from .form_sub1_input import form_sub1_input
from .form_sub1_settings import form_sub1_settings
from .form_sub2_tranx_report import form_sub2_tranx_report
from .form_sub2_pnl_mth_rpt import form_sub2_pnl_mth_rpt
from .form_testa import form_testa
from .form_testb import form_testb

class form_main(form_mainTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run when the form opens.
    self.report_column_panel_1.visible = False
    self.report_column_panel_2.visible = False

  def column_panel_link_dashb_click(self, **event_args):
    """This method is called when the link is clicked"""
    self.content_panel.clear()
    self.content_panel.add_component(form_sub1_dashb())

  def column_panel_link_input_click(self, **event_args):
    """This method is called when the link is clicked"""
    self.content_panel.clear()
    self.content_panel.add_component(form_sub1_input())

  def column_panel_link_reports_click(self, **event_args):
    """This method is called when the link is clicked"""
    if self.column_panel_link_reports.icon == 'fa:caret-right':
      self.report_column_panel_1.visible = True
      self.report_column_panel_2.visible = True
      self.column_panel_link_reports.icon = 'fa:caret-down'
    elif self.column_panel_link_reports.icon == 'fa:caret-down':
      self.report_column_panel_1.visible = False
      self.report_column_panel_2.visible = False
      self.column_panel_link_reports.icon = 'fa:caret-right'

  def column_panel_link_settings_click(self, **event_args):
    """This method is called when the link is clicked"""
    self.content_panel.clear()
    self.content_panel.add_component(form_sub1_settings())

  def column_panel_2_link_tranx_list_click(self, **event_args):
    """This method is called when the link is clicked"""
    self.content_panel.clear()
    self.content_panel.add_component(form_sub2_tranx_report())

  def column_panel_2_link_pnl_mth_rpt_click(self, **event_args):
    """This method is called when the link is clicked"""
    self.content_panel.clear()
    self.content_panel.add_component(form_sub2_pnl_mth_rpt())
    self.content_panel.add_component(form_sub2_tranx_report())

  def test_link_click(self, **event_args):
    """This method is called when the link is clicked"""
    self.content_panel.clear()
    self.content_panel.add_component(form_testa())
    self.content_panel.add_component(form_testb())
