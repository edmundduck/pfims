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
        self.foreground = const.ColorSchemes.AMT_EXPENSE if self.item[const.ExpenseDBTableDefinion.Amount] < 0 else const.ColorSchemes.AMT_POS

        # Logic to generate label buttons
        cache_labels = ClientCache('generate_labels_dropdown')
        for j in self.item[const.ExpenseDBTableDefinion.Labels].split(","):
            if j not in (None, ''):
                print(cache_labels.get_complete_key(j)
                lbl_id, lbl_name = cache_labels.get_complete_key(j)
                b = Button(
                    text=lbl_name,
                    # icon=const.Icons.REMOVE,
                    foreground=const.ColorSchemes.BUTTON_FG,
                    background=const.ColorSchemes.BUTTON_BG,
                    font_size=10,
                    align="left",
                    spacing_above="small",
                    spacing_below="small",
                    tag=lbl_id,
                    enabled=False
                )
                self.row_panel_labels.add_component(b, False, name=lbl_id)

    def row_link_symbol_click(self, **event_args):
        """This method is called when the link is clicked"""
        # TODO - To be implemented with hash routing in the future
        #newform = SettingForm(symname=self.row_link_symbol.text, 
        #                    symid=self.row_hidden_iid.text, 
        #                    symtemplid=self.row_hidden_templ_id.text)
        #open_form(newform)
        pass
