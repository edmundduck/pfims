from ._anvil_designer import ExpenseReportRPTemplateTemplate
from anvil import *
import anvil.users
import anvil.server
from ...Controllers import ExpenseReportController
from ...Utils import Constants as const

# About amount formatting in design page's data binding field
# Refer to https://anvil.works/forum/t/formatting-float-fields-in-a-datagrid/6796

class ExpenseReportRPTemplate(ExpenseReportRPTemplateTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)
    
        # Any code you write here will run when the form opens.
        self.foreground = const.ColorSchemes.AMT_EXPENSE if self.item[const.ExpenseDBTableDefinion.Amount] < 0 else const.ColorSchemes.AMT_POS

        # Logic to generate label buttons
        if self.item[const.ExpenseDBTableDefinion.Labels] is not None:
            for j in self.item[const.ExpenseDBTableDefinion.Labels].split(","):
                if j not in (None, ''):
                    lbl_id, lbl_name = ExpenseReportController.get_label_dropdown_selected_item(int(j))
                    b = Button(
                        text=lbl_name,
                        # icon=const.Icons.REMOVE,
                        foreground=const.ColorSchemes.BUTTON_FG,
                        background=const.ColorSchemes.BUTTON_BG,
                        font_size=12,
                        align="left",
                        spacing_above="small",
                        spacing_below="small",
                        tag=lbl_id,
                        enabled=False
                    )
                    self.row_panel_labels.add_component(b, False, name=lbl_id)

        # Logic to generate account dropdowns
        self.row_dropdown_acct.items = ExpenseReportController.generate_accounts_dropdown()
        self.row_dropdown_acct.selected_value = ExpenseReportController.get_account_dropdown_selected_item(self.row_dropdown_acct.selected_value)
