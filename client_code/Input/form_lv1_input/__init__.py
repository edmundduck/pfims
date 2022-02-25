from ._anvil_designer import form_lv1_inputTemplate
from anvil import *
import anvil.users
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from datetime import date
from ... import validation

class form_lv1_input(form_lv1_inputTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run when the form opens.
    self.input_repeating_panel.add_event_handler('x-save-change', self.save_row_change)
    
    # Initiate repeating panel items to an empty list otherwise will throw NoneType error
    self.input_repeating_panel.items = []
    self.input_selldate.date = date.today()
  
  def save_row_change(self, iid, **event_args):
    """ 
    *** ESSENTIAL ***
    Update child items from repeating panel to parent form items
    Refer to the following reference links for detail
    https://anvil.works/forum/t/is-it-possible-to-access-a-repeating-panels-methods-from-the-parent-form/3028/2
    https://anvil.works/forum/t/refresh-data-bindings-when-any-key-in-self-items-changes/1141/3
    https://anvil.works/forum/t/repeating-panel-to-collect-new-information/356/3
    """
    # TODO - Improve the update change logic so that don't have to go through whole list everytime
    self.input_repeating_panel.items = [c.input_data_panel_readonly.item \
                                        for c in self.input_repeating_panel.get_components()]
    
  def button_plus_click(self, **event_args):
    """This method is called when the button is clicked"""
    v = validation.Validator()
    v.display_when_invalid(self.valerror_title)
    v.require_date_field(self.input_selldate, self.valerror_1, True)
    v.require_date_field(self.input_buydate, self.valerror_2, True)
    v.require_text_field(self.input_symbol, self.valerror_3, True)
    v.require_text_field(self.input_qty, self.valerror_4, True)
    v.require_text_field(self.input_sales, self.valerror_5, True)
    v.require_text_field(self.input_cost, self.valerror_6, True)
    v.require_text_field(self.input_fee, self.valerror_7, True)

    if v.is_valid():
      last_iid = 0
      if len(self.input_repeating_panel.items) > 0:
        last_iid = self.input_repeating_panel.items[len(self.input_repeating_panel.items)-1]['iid']
      
      new_data = {"sell_date": self.input_selldate.date,
                      "buy_date": self.input_buydate.date,
                      "symbol": self.input_symbol.text,
                      "qty": self.input_qty.text,
                      "sales": self.input_sales.text,
                      "cost": self.input_cost.text,
                      "fee": self.input_fee.text,
                      "sell_price": anvil.server.call('cal_price', self.input_sales.text, self.input_qty.text),
                      "buy_price": anvil.server.call('cal_price', self.input_cost.text, self.input_qty.text),
                      "pnl": anvil.server.call('cal_profit', self.input_sales.text, self.input_cost.text, self.input_fee.text),
                      "iid": int(last_iid)+1}
      
      self.input_repeating_panel.items = self.input_repeating_panel.items + [new_data]
      
  def dropdown_templ_change(self, **event_args):
    """This method is called when an item is selected"""
    self.templ_name.text = anvil.server.call('get_input_templ_name', 
                                             self.dropdown_templ.selected_value)
    self.input_repeating_panel.items = anvil.server.call('get_input_templ_items', 
                                                         self.dropdown_templ.selected_value)
    self.dropdown_broker.selected_value = anvil.server.call('get_input_templ_broker', 
                                                            self.dropdown_templ.selected_value)

  def dropdown_templ_show(self, **event_args):
    """This method is called when the DropDown is shown on the screen"""
    self.dropdown_templ.items = anvil.server.call('get_input_templ_list')
    self.templ_name.text = anvil.server.call('get_input_templ_name', 
                                             self.dropdown_templ.selected_value)
    
  def dropdown_broker_show(self, **event_args):
    """This method is called when the DropDown is shown on the screen"""
    self.dropdown_broker.items = [''] + anvil.server.call('select_brokers')
    self.dropdown_broker.selected_value = anvil.server.call('get_input_templ_broker', 
                                                            self.dropdown_templ.selected_value)

  def button_save_templ_click(self, **event_args):
    """This method is called when the button is clicked"""
    templ_id = anvil.server.call('get_templ_id', 
                                 self.dropdown_templ.selected_value)
    
    anvil.server.call('upsert_templates',
                      template_id=templ_id,
                      template_name=self.templ_name.text, 
                      broker_id=self.dropdown_broker.selected_value)
    
    """ Delete all existing inputs before adding/updating """
    anvil.server.call('delete_templ_journals', 
                      template_id=templ_id)
    
    """ Add/Update """
    for row in self.input_repeating_panel.items:
      anvil.server.call('upsert_templ_journals', 
                        iid=row['iid'], 
                        template_id=templ_id, 
                        sell_date=row['sell_date'], 
                        buy_date=row['buy_date'], 
                        symbol=row['symbol'], 
                        qty=row['qty'], 
                        sales=row['sales'], 
                        cost=row['cost'], 
                        fee=row['fee'], 
                        sell_price=row['sell_price'], 
                        buy_price=row['buy_price'],
                        pnl=row['pnl'])

    """ Reflect the change in template dropdown """
    self.dropdown_templ.items = anvil.server.call('get_input_templ_list')
    self.dropdown_templ.selected_value = anvil.server.call('merge_templ_id_name', 
                                                                 templ_id, 
                                                                 self.templ_name.text)

  def button_erase_click(self, **event_args):
    """This method is called when the button is clicked"""
    self.input_selldate.date = ""
    self.input_buydate.date = ""
    self.input_symbol.text = ""
    self.input_qty.text = ""
    self.input_sales.text = ""
    self.input_cost.text = ""
    self.input_fee.text = 0
    self.input_sell_price.text = ""
    self.input_buy_price.text = ""
    self.input_pnl.text = ""

  def button_delete_templ_click(self, **event_args):
    """This method is called when the button is clicked"""
    to_be_del_templ_name = self.dropdown_templ.selected_value
    msg = Label(text="Proceed template <{templ_name}> deletion by clicking DELETE.".format(templ_name=to_be_del_templ_name))
    userconf = alert(content=msg, 
                     title=f"Alert - Template Deletion",
                     buttons=[
                       ("DELETE", "Y"),
                       ("CANCEL", "N")
                     ])
    
    if userconf == "Y":
      templ_id = anvil.server.call('get_templ_id', 
                                  to_be_del_templ_name)
      
      anvil.server.call('delete_templ_journals', 
                        template_id=templ_id)
      anvil.server.call('delete_templates', 
                        template_id=templ_id)
  
      """ Reflect the change in template dropdown """
      self.dropdown_templ_show()
      #self.dropdown_templ.items = anvil.server.call('get_input_templ_list')
      #self.templ_name.text = ""
      self.dropdown_broker_show()
      self.input_repeating_panel.items = []
      
      n = Notification("Template {templ_name} has been deleted.".format(templ_name=to_be_del_templ_name))
      n.show()
      

  def button_submit_click(self, **event_args):
    """This method is called when the button is clicked"""
    to_be_submitted_templ_name = self.dropdown_templ.selected_value
    templ_id = anvil.server.call('get_templ_id', 
                                 to_be_submitted_templ_name)
    anvil.server.call('update_templates_submit_flag', 
                      templ_id, 
                      True)
    """ Reflect the change in template dropdown """
    self.dropdown_templ.items = anvil.server.call('get_input_templ_list')
    self.dropdown_templ.raise_event('change')

    n = Notification("Template {templ_name} has been submitted.\n It can be viewed in the transaction list report only.".format(templ_name=to_be_submitted_templ_name))
    n.show()

