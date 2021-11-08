from ._anvil_designer import form_sub1_inputTemplate
from anvil import *
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from datetime import date

class form_sub1_input(form_sub1_inputTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run when the form opens.
    
    # Initiate repeating panel items to an empty list otherwise will throw NoneType error
    self.input_repeating_panel.items = []
    self.input_selldate.date = date.today()
    
  def input_button_plus_click(self, **event_args):
    """This method is called when the button is clicked"""

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
                    "sell_price": anvil.server.call('get_amt_with_stockprecision', float(self.input_sales.text) / float(self.input_qty.text)),
                    "buy_price": anvil.server.call('get_amt_with_stockprecision', float(self.input_cost.text) / float(self.input_qty.text)),
                    "pnl": anvil.server.call('get_amt_with_stockprecision', float(self.input_cost.text) - float(self.input_fee.text)),
                    "iid": int(last_iid)+1}
    
    self.input_repeating_panel.items = self.input_repeating_panel.items + [new_data]
    
  def input_dropdown_templ_change(self, **event_args):
    """This method is called when an item is selected"""
    self.input_templ_name.text = anvil.server.call('get_input_templ_name', 
                                                   self.input_dropdown_templ.selected_value)
    self.input_repeating_panel.items = anvil.server.call('get_input_templ_items', 
                                                         self.input_dropdown_templ.selected_value)

  def input_dropdown_templ_show(self, **event_args):
    """This method is called when the DropDown is shown on the screen"""
    self.input_dropdown_templ.items = anvil.server.call('get_input_templ_list')
    self.input_templ_name.text = anvil.server.call('get_input_templ_name', 
                                                   self.input_dropdown_templ.selected_value)
    
  def button_save_templ_click(self, **event_args):
    """This method is called when the button is clicked"""
    
    """ 
    *** ESSENTIAL ***
    Update child items from repeating panel to parent form items
    Refer to the following reference links for detail
    https://anvil.works/forum/t/is-it-possible-to-access-a-repeating-panels-methods-from-the-parent-form/3028/2
    https://anvil.works/forum/t/refresh-data-bindings-when-any-key-in-self-items-changes/1141/3
    https://anvil.works/forum/t/repeating-panel-to-collect-new-information/356/3
    """
    child_items = []
    for c in self.input_repeating_panel.get_components():
      child_items += [c.input_data_panel_readonly.item]
    self.input_repeating_panel.items = child_items
    
    templ_id = anvil.server.call('generate_new_templ_id', 
                                 self.input_dropdown_templ.selected_value)
    
    anvil.server.call('upsert_templates',
                      template_id=templ_id,
                      template_name=self.input_templ_name.text)
    
    """ Delete all existing inputs before adding/updating """
    anvil.server.call('delete_temp_input', 
                      template_id=templ_id)
    
    """ Add/Update """
    for row in self.input_repeating_panel.items:
      anvil.server.call('upsert_temp_input', 
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
                        buy_price=row['buy_price'])

    """ Reflect the change in template dropdown """
    self.input_dropdown_templ.items = anvil.server.call('get_input_templ_list')
    self.input_dropdown_templ.selected_value = anvil.server.call('merge_templ_id_name', 
                                                                 templ_id, 
                                                                 self.input_templ_name.text)

  def input_button_erase_click(self, **event_args):
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
    to_be_del_templ_name = self.input_dropdown_templ.selected_value
    msg = Label(text="Proceed template <{templ_name}> deletion by clicking DELETE.".format(templ_name=to_be_del_templ_name))
    userconf = alert(content=msg, 
                     title=f"Alert - Template Deletion",
                     buttons=[
                       ("DELETE", "Y"),
                       ("CANCEL", "N")
                     ])
    
    if userconf == "Y":
      templ_id = anvil.server.call('generate_new_templ_id', 
                                  to_be_del_templ_name)
      
      anvil.server.call('delete_temp_input', 
                        template_id=templ_id)
      anvil.server.call('delete_templates', 
                        template_id=templ_id)
  
      """ Reflect the change in template dropdown """
      self.input_dropdown_templ_show()
      #self.input_dropdown_templ.items = anvil.server.call('get_input_templ_list')
      #self.input_templ_name.text = ""
      self.input_repeating_panel.items = []
      
      n = Notification("Template {templ_name} has been deleted.".format(templ_name=to_be_del_templ_name))
      n.show()