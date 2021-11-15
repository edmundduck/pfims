from ._anvil_designer import form_lv2_search_panelTemplate
from anvil import *
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from datetime import date
from ... import global_var
from ..form_lv2_tranx_list import form_lv2_tranx_list
from ..form_lv2_pnl_report import form_lv2_pnl_report

class form_lv2_search_panel(form_lv2_search_panelTemplate):
  subform = None

  def __init__(self, subform, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run when the form opens.
    self.dropdown_interval.items = global_var.search_interval_dropdown()
    self.dropdown_symbol.items = global_var.search_symbol_dropdown()

    settings = anvil.server.call('select_settings')
    self.dropdown_interval.selected_value = settings.get('default_interval')
    self.time_datefrom.date = settings.get('default_datefrom')
    self.time_dateto.date = settings.get('default_dateto')
    
    if subform == global_var.form_lv2_tranx_list():
      self.subform = form_lv2_tranx_list()
      self.colpanel_list.add_component(self.subform)
      self.panel_tranx_list.visible = True
      self.panel_pnl_report.visible = False
    elif subform == global_var.form_lv2_pnl_report():
      self.subform = form_lv2_pnl_report()
      self.colpanel_list.add_component(self.subform)
      self.panel_tranx_list.visible = False
      self.panel_pnl_report.visible = True
    else:
      # If error, show no buttons
      self.panel_tranx_list.visible = False
      self.panel_pnl_report.visible = False
   
    # Prevent from adding default value "[Symbol]" by registering to the dictionary
    self.tag = {'added_symbols': {global_var.search_symbol_dropdown()[0][1]: 1}}

    if self.dropdown_interval.selected_value != "SDR":
      if self.dropdown_interval.selected_value == '' or self.dropdown_interval.selected_value is None:
        self.button_tranx_search.enabled = False
        self.button_pnl_search.enabled = False
      self.time_datefrom.enabled = False
      self.time_dateto.enabled = False
      self.label_timetotime.enabled = False

      self.dropdown_symbol.items = global_var.search_symbol_dropdown() + \
        anvil.server.call('get_symbol_dropdown_items', 
                          date.today(), 
                          anvil.server.call('get_start_date', 
                                            date.today(), 
                                            self.dropdown_interval.selected_value))
    else:
      self.time_datefrom.enabled = True
      self.time_dateto.enabled = True
      self.label_timetotime.enabled = True
      self.dropdown_symbol.items = global_var.search_symbol_dropdown() + \
        anvil.server.call('get_symbol_dropdown_items', 
                          self.time_dateto.date, 
                          self.time_datefrom.date)

      
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
      if self.dropdown_interval.selected_value == "":
        self.button_tranx_search.enabled = False
        self.button_pnl_search.enabled = False
      else:
        self.button_tranx_search.enabled = True
        self.button_pnl_search.enabled = True
        
      self.time_datefrom.enabled = False
      self.time_dateto.enabled = False
      self.label_timetotime.enabled = False
      self.dropdown_symbol.items = global_var.search_symbol_dropdown() + \
        anvil.server.call('get_symbol_dropdown_items', 
                          date.today(), 
                          anvil.server.call('get_start_date', 
                                            date.today(), 
                                            self.dropdown_interval.selected_value))
    else:
      self.button_tranx_search.enabled = True
      self.button_pnl_search.enabled = True
      self.time_datefrom.enabled = True
      self.time_dateto.enabled = True
      self.label_timetotime.enabled = True
      self.dropdown_symbol.items = global_var.search_symbol_dropdown() + \
        anvil.server.call('get_symbol_dropdown_items', 
                          self.time_dateto.date, 
                          self.time_datefrom.date)

  def time_datefrom_change(self, **event_args):
    """This method is called when the selected date changes"""
    self.dropdown_symbol.items = global_var.search_symbol_dropdown() + \
      anvil.server.call('get_symbol_dropdown_items', 
                        self.time_dateto.date, 
                        self.time_datefrom.date)

  def time_dateto_change(self, **event_args):
    """This method is called when the selected date changes"""
    self.dropdown_symbol.items = global_var.search_symbol_dropdown() + \
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

  def button_tranx_search_click(self, **event_args):
    """This method is called when the button is clicked"""
    symbol_list = self.get_selected_symbols()
    enddate = None
    startdate = None
    
    if self.dropdown_interval.selected_value != "SDR":
      enddate = date.today()
      startdate = anvil.server.call('get_start_date', 
                                    date.today(), 
                                    self.dropdown_interval.selected_value)      
    else:
      enddate = self.time_dateto.date
      startdate = self.time_datefrom.date 
                                    
    self.subform.rpt_panel.items = anvil.server.call('select_templ_journals', 
                                              enddate, 
                                              startdate, 
                                              symbol_list)

  def button_tranx_reset_click(self, **event_args):
    """This method is called when the button is clicked"""
    self.time_datefrom.date = ""
    self.time_dateto.date = ""
    self.dropdown_interval.items = []
    self.dropdown_interval.items = global_var.search_interval_dropdown()
    self.dropdown_symbol.items = global_var.search_symbol_dropdown()
    self.removeall_selected_symbols()
    self.subform.rpt_panel.items = []
    self.button_tranx_search.enabled = False

  def button_pnl_search_click(self, **event_args):
    """This method is called when the button is clicked"""
    symbol_list = self.get_selected_symbols()
    enddate = None
    startdate = None

    if self.dropdown_interval.selected_value != "SDR":
      enddate = date.today()
      startdate = anvil.server.call('get_start_date', 
                                    date.today(), 
                                    self.dropdown_interval.selected_value)      
    else:
      enddate = self.time_dateto.date
      startdate = self.time_datefrom.date 

    self.subform.hidden_time_dateto.date = enddate
    self.subform.hidden_time_datefrom.date = startdate
    self.subform.hidden_symbol.text = symbol_list
    self.subform.rpt_panel.items = anvil.server.call('generate_init_pnl_list', 
                                                     enddate, 
                                                     startdate, 
                                                     symbol_list)

  def button_pnl_reset_click(self, **event_args):
    """This method is called when the button is clicked"""
    self.time_datefrom.date = ""
    self.time_dateto.date = ""
    self.dropdown_interval.items = []
    self.dropdown_interval.items = global_var.search_interval_dropdown()
    self.dropdown_symbol.items = global_var.search_symbol_dropdown()
    self.removeall_selected_symbols()
    self.subform.rpt_panel.items = []
    self.button_pnl_search.enabled = False

