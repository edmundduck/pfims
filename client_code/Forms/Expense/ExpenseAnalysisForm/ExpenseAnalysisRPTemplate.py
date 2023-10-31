from ._anvil_designer import ExpenseAnalysisRPTemplateTemplate
from anvil import *
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
from ....Controllers import ExpenseReportController
from ....Utils.Constants import ColorSchemes
# About amount formatting in design page's data binding field
# Refer to https://anvil.works/forum/t/formatting-float-fields-in-a-datagrid/6796

class ExpenseAnalysisRPTemplate(ExpenseAnalysisRPTemplateTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        # Any code you write here will run when the form opens.
        from ....Entities.ExpenseTransaction import ExpenseTransaction

        self.foreground = ColorSchemes.AMT_EXPENSE if self.item[ExpenseTransaction.field_amount()] < 0 else ColorSchemes.AMT_POS

        # Logic to generate label buttons
        if self.item[ExpenseTransaction.field_labels()] is not None:
            for j in self.item[ExpenseTransaction.field_labels()].split(","):
                if j:
                    lbl = ExpenseReportController.get_label_dropdown_selected_item(int(j))
                    lbl_id, lbl_name = lbl if isinstance(lbl, (list, tuple)) else [lbl, lbl]
                    b = Button(
                        text=lbl_name,
                        # icon=Icons.REMOVE,
                        foreground=ColorSchemes.BUTTON_FG,
                        background=ColorSchemes.BUTTON_BG,
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
