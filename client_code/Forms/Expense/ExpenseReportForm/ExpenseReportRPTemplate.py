from ._anvil_designer import ExpenseReportRPTemplateTemplate
from anvil import *
import anvil.server
from ....Controllers import ExpenseReportController
from ....Utils.Constants import Roles
# About amount formatting in design page's data binding field
# Refer to https://anvil.works/forum/t/formatting-float-fields-in-a-datagrid/6796

class ExpenseReportRPTemplate(ExpenseReportRPTemplateTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)
    
        # Any code you write here will run when the form opens.
        from ....Entities.ExpenseTransaction import ExpenseTransaction
        
        self.row_label_amt.role = Roles.AMT_NEGATIVE if self.item[ExpenseTransaction.field_amount()] < 0 else Roles.AMT_POSITIVE

        # Logic to generate label buttons
        if self.item[ExpenseTransaction.field_labels()] is not None:
            for j in self.item[ExpenseTransaction.field_labels()]:
                if j:
                    lbl = ExpenseReportController.get_label_dropdown_selected_item(int(j))
                    lbl_id, lbl_name = lbl if isinstance(lbl, (list, tuple)) else [lbl, lbl]
                    b = Button(
                        text=lbl_name,
                        # icon=Icons.REMOVE,
                        role=Roles.LABEL,
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
