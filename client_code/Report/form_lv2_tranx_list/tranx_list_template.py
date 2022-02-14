from ._anvil_designer import tranx_list_templateTemplate
from anvil import *
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

# About amount formatting in design page's data binding field
# Refer to https://anvil.works/forum/t/formatting-float-fields-in-a-datagrid/6796

class tranx_list_template(tranx_list_templateTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run when the form opens.
    if self.item['pnl'] < 0:
      self.foreground = 'Red'
    else:
      self.foreground = 'Green'

  def row_link_symbol_click(self, **event_args):
    """This method is called when the link is clicked"""
    # TODO - To be implemented with hash routing in the future
    #newform = form_lv1_settings(symname=self.row_link_symbol.text, 
    #                    symid=self.row_hidden_iid.text, 
    #                    symtemplid=self.row_hidden_templ_id.text)
    #open_form(newform)
    pass
