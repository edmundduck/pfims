from ._anvil_designer import form_mainTemplate
from anvil import *
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from .form_sub1_dashb import form_sub1_dashb
from .form_sub1_input import form_sub1_input
from .form_sub1_reports import form_sub1_reports
from .form_sub1_settings import form_sub1_settings

class form_main(form_mainTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run when the form opens.

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
    self.content_panel.clear()
    self.content_panel.add_component(form_sub1_reports())

  def column_panel_link_settings_click(self, **event_args):
    """This method is called when the link is clicked"""
    self.content_panel.clear()
    self.content_panel.add_component(form_sub1_settings())






