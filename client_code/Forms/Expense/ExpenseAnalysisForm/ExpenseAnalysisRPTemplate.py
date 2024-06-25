from ._anvil_designer import ExpenseAnalysisRPTemplateTemplate
from anvil import *
import anvil.server
from ....Controllers import ExpenseReportController
from ....Utils.Constants import Roles
# About amount formatting in design page's data binding field
# Refer to https://anvil.works/forum/t/formatting-float-fields-in-a-datagrid/6796

class ExpenseAnalysisRPTemplate(ExpenseAnalysisRPTemplateTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        # Any code you write here will run when the form opens.
        from ....Entities.ExpenseTransaction import ExpenseTransaction

        self.row_amount.role = Roles.AMT_NEGATIVE if self.item[ExpenseTransaction.field_amount()] < 0 else Roles.AMT_POSITIVE

        # Logic to generate label buttons
        if self.item.get(ExpenseTransaction.field_labels(), None):
            self.row_label.text = f"{self.item['name']} ({self.item[ExpenseTransaction.field_labels()]})"
        elif self.item.get(ExpenseTransaction.field_account(), None):
            self.row_account.text = f"{self.item['name']} ({self.item[ExpenseTransaction.field_account()]})"
