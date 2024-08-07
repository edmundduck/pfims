from ._anvil_designer import ExpenseAnalysisFormTemplate
from anvil import *
import anvil.server
import plotly.graph_objects as go
from ....Utils.Constants import ExpenseReportType, ReportFormTag
from ....Entities.ExpenseTransaction import ExpenseTransaction
from ....Utils.Logger import ClientLogger

logger = ClientLogger()

class ExpenseAnalysisForm(ExpenseAnalysisFormTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        # Any code you write here will run when the form opens.
        self.data_grid.rows_per_page = self.dropdown_displayrow.selected_value
        self.tag= {ReportFormTag.REPORT_TAG: ReportFormTag.EXP_ANALYSIS_RPT}

    def dropdown_displayrow_change(self, **event_args):
        """This method is called when an item is selected"""
        self.data_grid.rows_per_page = self.dropdown_displayrow.selected_value

    def set_column_visibility(self, report_type, **event_args):
        if report_type:
            if report_type == ExpenseReportType.EXP_PER_LABEL:
                required_column = [c for c in self.hidden_data_grid.columns if c['data_key'] == ExpenseTransaction.field_labels()]
                unwanted_column = [c for c in self.data_grid.columns if c['data_key'] == ExpenseTransaction.field_account()][0]
                self.hidden_data_grid.columns.append(unwanted_column)
                self.data_grid.columns.remove(unwanted_column)
                if required_column:
                    self.data_grid.columns = [required_column[0]] + self.data_grid.columns
                else:                    
                    self.data_grid.columns = self.data_grid.columns
            elif report_type == ExpenseReportType.BAL_ACCT:
                required_column = [c for c in self.hidden_data_grid.columns if c['data_key'] == ExpenseTransaction.field_account()]
                unwanted_column = [c for c in self.data_grid.columns if c['data_key'] == ExpenseTransaction.field_labels()][0]
                self.hidden_data_grid.columns.append(unwanted_column)
                self.data_grid.columns.remove(unwanted_column)
                if required_column:
                    self.data_grid.columns = [required_column[0]] + self.data_grid.columns
                else:                    
                    self.data_grid.columns = self.data_grid.columns
