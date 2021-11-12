from ._anvil_designer import form_lv2_search_panelTemplate
from anvil import *
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from datetime import date
from ... import global_var
from ..form_lv2_tranx_list import form_lv2_tranx_list

class form_lv2_search_panel(form_lv2_search_panelTemplate):
  interval_list = [("[Interval]", ""), 
                  ("Last 1 Month", "L1M"), 
                  ("Last 3 Month", "L3M"),
                  ("Last 6 Month", "L6M"),
                  ("Last 1 Year", "L1Y"),
                  ("Year to Date", "YTD"),
                  ("Self Defined Range", "SDR")]
  
  symbol_list = [("[Symbol]", "")]
  
  subform = None

  def __init__(self, subform, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run when the form opens.
    self.dropdown_interval.items = self.interval_list
    self.dropdown_symbol.items = self.symbol_list
    
    if subform == global_var.form_lv2_tranx_list():
      self.subform = form_lv2_tranx_list()
      self.colpanel_list.add_component(self.subform)
    elif subform == global_var.form_lv2_pnl_report():
      #self.subform = open_form()
      pass
   
    # Prevent from adding default value "[Symbol]" by registering to the dictionary
    self.tag = {'added_symbols': {self.symbol_list[0][1]: 1}}

    if self.dropdown_interval.selected_value != "SDR":
      self.time_datefrom.enabled = False
      self.time_dateto.enabled = False
      self.label_timetotime.enabled = False

  # NOTE - If use self.tag['added_symbols'] approach, need to consider the registered default value "[Symbol]"
  # Return selected symbols which appear in blue buttons 
  def get_selected_symbols(self):
    symbol_list = []
    for i in self.panel_symbol.get_components():
      if isinstance(i, Button):
        if i.icon == 'fa:minus':
          symbol_list += [i.text]
    return symbol_list

  # Remove all symbols selected as blue buttons from dictionary
  def removeall_selected_symbols(self):
    for i in self.panel_symbol.get_components():
      if isinstance(i, Button):
        if i.icon == 'fa:minus':
          # Deregister the added symbol from the dictionary in self.tag
          self.tag['added_symbols'].pop(i.text)
          i.remove_from_parent()

  def dropdown_interval_change(self, **event_args):
    """This method is called when an item is selected"""
    self.removeall_selected_symbols()
    
    if self.dropdown_interval.selected_value != "SDR":
      self.time_datefrom.enabled = False
      self.time_dateto.enabled = False
      self.label_timetotime.enabled = False
      self.dropdown_symbol.items = self.symbol_list + \
        anvil.server.call('get_symbol_dropdown_items', 
                          date.today(), 
                          anvil.server.call('get_start_date', 
                                            date.today(), 
                                            self.dropdown_interval.selected_value))
    else:
      self.time_datefrom.enabled = True
      self.time_dateto.enabled = True
      self.label_timetotime.enabled = True
      self.dropdown_symbol.items = self.symbol_list + \
        anvil.server.call('get_symbol_dropdown_items', 
                          self.time_dateto.date, 
                          self.time_datefrom.date)

  def time_datefrom_change(self, **event_args):
    """This method is called when the selected date changes"""
    self.dropdown_symbol.items = self.symbol_list + \
      anvil.server.call('get_symbol_dropdown_items', 
                        self.time_dateto.date, 
                        self.time_datefrom.date)

  def time_dateto_change(self, **event_args):
    """This method is called when the selected date changes"""
    self.dropdown_symbol.items = self.symbol_list + \
      anvil.server.call('get_symbol_dropdown_items', 
                        self.time_dateto.date, 
                        self.time_datefrom.date)

  def tranx_rpt_button_plus_click(self, **event_args):
    """This method is called when the button is clicked"""
    if self.tag['added_symbols'].get(self.dropdown_symbol.selected_value, None) is None:
      b = Button(text=self.dropdown_symbol.selected_value,
                icon='fa:minus',
                foreground="White",
                background="Blue")
      self.panel_symbol.add_component(b, name=self.dropdown_symbol.selected_value)
      b.set_event_handler('click', self.remove_symbol_button)

      # Register the added symbol to the dictionary in self.tag to avoid duplication
      self.tag['added_symbols'].update({self.dropdown_symbol.selected_value: 1})

  def remove_symbol_button(self, **event_args):
    b = event_args['sender']
    # Deregister the added symbol from the dictionary in self.tag
    self.tag['added_symbols'].pop(b.text)

    b.remove_from_parent()

  def tranx_rpt_button_search_click(self, **event_args):
    """This method is called when the button is clicked"""
    symbol_list = self.get_selected_symbols()
    if self.dropdown_interval.selected_value != "SDR":
      self.rpt_panel.items = anvil.server.call('select_templ_journals', 
                                               date.today(), 
                                               anvil.server.call('get_start_date', 
                                                                 date.today(), 
                                                                 self.dropdown_interval.selected_value), 
                                               symbol_list)
    else:
      self.rpt_panel.items = anvil.server.call('select_templ_journals', 
                                               self.time_dateto.date, 
                                               self.time_datefrom.date, 
                                               symbol_list)

  def tranx_rpt_button_reset_click(self, **event_args):
    """This method is called when the button is clicked"""
    self.time_datefrom.date = ""
    self.time_dateto.date = ""
    self.dropdown_interval.items = []
    self.dropdown_interval.items = self.interval_list
    self.dropdown_symbol.items = self.symbol_list
    self.removeall_selected_symbols()
    self.tranx_rpt_repeating_panel.items = []


