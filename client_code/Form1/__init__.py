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
        # self.add_component(self.current_form)
        self.add_component(ExpenseReportSearchPanelForm(ExpenseAnalysisForm()), slot="default")
