from ._anvil_designer import TransactionReportRPTemplateTemplate
from anvil import *
from ....Utils.Constants import Roles

# About amount formatting in design page's data binding field
# Refer to https://anvil.works/forum/t/formatting-float-fields-in-a-datagrid/6796

class TransactionReportRPTemplate(TransactionReportRPTemplateTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)
    
        # Any code you write here will run when the form opens.
        self.row_label_pnl.role = Roles.AMT_NEGATIVE if self.item['pnl'] < 0 else Roles.AMT_POSITIVE

    def row_link_symbol_click(self, **event_args):
        """This method is called when the link is clicked"""
        # TODO - To be implemented with hash routing in the future
        #newform = SettingForm(symname=self.row_link_symbol.text, 
        #                    symid=self.row_hidden_iid.text, 
        #                    symtemplid=self.row_hidden_templ_id.text)
        #open_form(newform)
        pass
