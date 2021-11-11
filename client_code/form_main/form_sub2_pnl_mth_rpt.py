from ._anvil_designer import form_sub2_pnl_mth_rptTemplate
from anvil import *
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from datetime import date

class form_sub2_pnl_mth_rpt(form_sub2_pnl_mth_rptTemplate):
  interval_list = [("[Interval]", ""), 
                  ("Last 1 Month", "L1M"), 
                  ("Last 3 Month", "L3M"),
                  ("Last 6 Month", "L6M"),
                  ("Last 1 Year", "L1Y"),
                  ("Year to Date", "YTD"),
                  ("Self Defined Range", "SDR")]
  
  symbol_list = [("[Symbol]", "")]
  
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run when the form opens.
    self.tranx_rpt_time_dropdown.items = self.interval_list
    self.tranx_rpt_symbol_dropdown.items = self.symbol_list
    self.data_grid.rows_per_page = self.tranx_rpt_displayrow_dropdown.selected_value
    # Prevent from adding default value "[Symbol]" by registering to the dictionary
    self.tag = {'added_symbols': {self.symbol_list[0][1]: 1}}

    if self.tranx_rpt_time_dropdown.selected_value != "SDR":
      self.tranx_rpt_time_from_date.enabled = False
      self.tranx_rpt_time_to_date.enabled = False
      self.tranx_rpt_time_to_label.enabled = False

  # NOTE - If use self.tag['added_symbols'] approach, need to consider the registered default value "[Symbol]"
  def get_selected_symbols(self):
    symbol_list = []
    for i in self.symbol_panel.get_components():
      if isinstance(i, Button):
        if i.icon == 'fa:minus':
          symbol_list += [i.text]
    return symbol_list

  def removeall_selected_symbols(self):
    for i in self.symbol_panel.get_components():
      if isinstance(i, Button):
        if i.icon == 'fa:minus':
          # Deregister the added symbol from the dictionary in self.tag
          self.tag['added_symbols'].pop(i.text)
          i.remove_from_parent()

  def tranx_rpt_time_dropdown_change(self, **event_args):
    """This method is called when an item is selected"""
    self.removeall_selected_symbols()
    
    if self.tranx_rpt_time_dropdown.selected_value != "SDR":
      self.tranx_rpt_time_from_date.enabled = False
      self.tranx_rpt_time_to_date.enabled = False
      self.tranx_rpt_time_to_label.enabled = False
      self.tranx_rpt_symbol_dropdown.items = self.symbol_list + anvil.server.call('get_symbol_dropdown_items', 
                                                               date.today(), 
                                                               anvil.server.call('get_start_date', 
                                                                                 date.today(), 
                                                                                 self.tranx_rpt_time_dropdown.selected_value))
    else:
      self.tranx_rpt_time_from_date.enabled = True
      self.tranx_rpt_time_to_date.enabled = True
      self.tranx_rpt_time_to_label.enabled = True
      self.tranx_rpt_symbol_dropdown.items = self.symbol_list + anvil.server.call('get_symbol_dropdown_items', 
                                                               self.tranx_rpt_time_to_date.date, 
                                                               self.tranx_rpt_time_from_date.date)

  def tranx_rpt_time_from_date_change(self, **event_args):
    """This method is called when the selected date changes"""
    self.tranx_rpt_symbol_dropdown.items = self.symbol_list + anvil.server.call('get_symbol_dropdown_items', 
                                                              self.tranx_rpt_time_to_date.date, 
                                                              self.tranx_rpt_time_from_date.date)

  def tranx_rpt_time_to_date_change(self, **event_args):
    """This method is called when the selected date changes"""
    self.tranx_rpt_symbol_dropdown.items = self.symbol_list + anvil.server.call('get_symbol_dropdown_items', 
                                                              self.tranx_rpt_time_to_date.date, 
                                                              self.tranx_rpt_time_from_date.date)

  def tranx_rpt_button_plus_click(self, **event_args):
    """This method is called when the button is clicked"""
    if self.tag['added_symbols'].get(self.tranx_rpt_symbol_dropdown.selected_value, None) is None:
      b = Button(text=self.tranx_rpt_symbol_dropdown.selected_value,
                icon='fa:minus',
                foreground="White",
                background="Blue")
      self.symbol_panel.add_component(b, name=self.tranx_rpt_symbol_dropdown.selected_value)
      b.set_event_handler('click', self.remove_symbol_button)

      # Register the added symbol to the dictionary in self.tag to avoid duplication
      self.tag['added_symbols'].update({self.tranx_rpt_symbol_dropdown.selected_value: 1})

  def remove_symbol_button(self, **event_args):
    b = event_args['sender']
    # Deregister the added symbol from the dictionary in self.tag
    self.tag['added_symbols'].pop(b.text)

    b.remove_from_parent()

  def tranx_rpt_button_search_click(self, **event_args):
    """This method is called when the button is clicked"""
    symbol_list = self.get_selected_symbols()
    if self.tranx_rpt_time_dropdown.selected_value != "SDR":
      self.tranx_rpt_repeating_panel.items = anvil.server.call('select_templ_journals', 
                                                               date.today(), 
                                                               anvil.server.call('get_start_date', 
                                                                                 date.today(), 
                                                                                 self.tranx_rpt_time_dropdown.selected_value), 
                                                               symbol_list)
    else:
      self.tranx_rpt_repeating_panel.items = anvil.server.call('select_templ_journals', 
                                                               self.tranx_rpt_time_to_date.date, 
                                                               self.tranx_rpt_time_from_date.date, 
                                                               symbol_list)

  def tranx_rpt_button_reset_click(self, **event_args):
    """This method is called when the button is clicked"""
    self.tranx_rpt_time_from_date.date = ""
    self.tranx_rpt_time_to_date.date = ""
    self.tranx_rpt_time_dropdown.items = []
    self.tranx_rpt_time_dropdown.items = self.interval_list
    self.tranx_rpt_symbol_dropdown.items = self.symbol_list
    self.removeall_selected_symbols()
    self.tranx_rpt_repeating_panel.items = []

  def tranx_rpt_displayrow_dropdown_change(self, **event_args):
    """This method is called when an item is selected"""
    self.data_grid.rows_per_page = self.tranx_rpt_displayrow_dropdown.selected_value
