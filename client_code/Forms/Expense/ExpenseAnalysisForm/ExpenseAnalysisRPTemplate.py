from ._anvil_designer import ExpenseAnalysisRPTemplateTemplate
from anvil import *
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
        self.row_label.text = f"{self.item['name']} ({self.item[ExpenseTransaction.field_labels()]})"
