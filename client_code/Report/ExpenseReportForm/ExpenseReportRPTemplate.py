from ._anvil_designer import ExpenseReportRPTemplateTemplate
from anvil import *
import anvil.users
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from ...Utils import Constants as const
from ...Utils.ClientCache import ClientCache

# About amount formatting in design page's data binding field
# Refer to https://anvil.works/forum/t/formatting-float-fields-in-a-datagrid/6796

class ExpenseReportRPTemplate(ExpenseReportRPTemplateTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)
    
        # Any code you write here will run when the form opens.
        cache_acct = ClientCache('generate_accounts_dropdown')
        self.foreground = const.ColorSchemes.AMT_EXPENSE if self.item['amount'] < 0 else const.ColorSchemes.AMT_POS
        self.row_dropdown_acct.items = cache_acct.get_cache()
        
    def row_link_symbol_click(self, **event_args):
        """This method is called when the link is clicked"""
        # TODO - To be implemented with hash routing in the future
        #newform = SettingForm(symname=self.row_link_symbol.text, 
        #                    symid=self.row_hidden_iid.text, 
        #                    symtemplid=self.row_hidden_templ_id.text)
        #open_form(newform)
        pass
