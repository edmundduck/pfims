from ._anvil_designer import Form1Template
from anvil import *
import anvil.server
import anvil.users

class Form1(Form1Template):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        # Any code you write here will run when the form opens.
        from ..Forms.Expense.ExpenseReportSearchPanelForm import ExpenseReportSearchPanelForm
        from ..Forms.Expense.ExpenseAnalysisForm import ExpenseAnalysisForm
        self.content_panel1.width = 1800
        self.content_panel1.add_component(ExpenseReportSearchPanelForm(ExpenseAnalysisForm(), full_width_row=True))
