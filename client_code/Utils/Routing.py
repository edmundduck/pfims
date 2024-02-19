import anvil.server

# This is a module.
# You can define variables and functions here, and use them from any form. For example, in a top-level form:

def open_dashboard_form(self, **event_args):
    from ..Forms.DashboardForm import DashboardForm
    anvil.get_open_form().content_panel.clear()
    anvil.get_open_form().content_panel.add_component(DashboardForm())

def open_setting_form(self, **event_args):
    from ..Forms.Admin.UserSettingForm import UserSettingForm
    anvil.get_open_form().content_panel.clear()
    anvil.get_open_form().content_panel.add_component(UserSettingForm())

def open_stock_txn_input_form(self, **event_args):
    from ..Forms.Investment.StockTradingTxnDetailForm import StockTradingTxnDetailForm
    anvil.get_open_form().content_panel.clear()
    anvil.get_open_form().content_panel.add_component(StockTradingTxnDetailForm())

def open_exp_input_form(self, tab_id=None, data=None, **event_args):
    from ..Forms.Expense.ExpenseInputForm import ExpenseInputForm
    # The following doesn't work, but open_acct_maint_form one works, no idea why
    # self.clear()
    # self.add_component(ExpenseInputForm())
    anvil.get_open_form().content_panel.clear()
    anvil.get_open_form().content_panel.add_component(ExpenseInputForm(tab_id=tab_id, data=data))

def open_exp_file_upload_form(self, **event_args):
    from ..Forms.Expense.ExpenseFileUploadForm import ExpenseFileUploadForm
    anvil.get_open_form().content_panel.clear()
    anvil.get_open_form().content_panel.add_component(ExpenseFileUploadForm(),)

def open_exp_file_excel_import_form(self, data, labels, accounts, **event_args):
    from ..Forms.Expense.ExpenseFileExcelImportForm import ExpenseFileExcelImportForm
    anvil.get_open_form().content_panel.clear()
    anvil.get_open_form().content_panel.add_component(ExpenseFileExcelImportForm(data, labels, accounts))

def open_exp_file_pdf_import_form(self, data, **event_args):
    from ..Forms.Expense.ExpenseFilePDFImportForm import ExpenseFilePDFImportForm
    anvil.get_open_form().content_panel.clear()
    anvil.get_open_form().content_panel.add_component(ExpenseFilePDFImportForm(data))

def open_upload_mapping_form(self, **event_args):
    from ..Forms.Expense.UploadMappingRulesForm import UploadMappingRulesForm
    anvil.get_open_form().content_panel.clear()
    anvil.get_open_form().content_panel.add_component(UploadMappingRulesForm())

def open_lbl_maint_form(self, **event_args):
    from ..Forms.Expense.LabelMaintForm import LabelMaintForm
    anvil.get_open_form().content_panel.clear()
    anvil.get_open_form().content_panel.add_component(LabelMaintForm())
    
def open_acct_maint_form(self, **event_args):
    from ..Forms.Expense.AccountMaintForm import AccountMaintForm
    anvil.get_open_form().content_panel.clear()
    anvil.get_open_form().content_panel.add_component(AccountMaintForm())

def open_tranx_list_form(self, **event_args):
    from ..Forms.Investment.InvestmentReportSearchPanelForm import InvestmentReportSearchPanelForm
    from ..Forms.Investment.TransactionReportForm import TransactionReportForm
    anvil.get_open_form().content_panel.clear()
    anvil.get_open_form().content_panel.add_component(InvestmentReportSearchPanelForm(TransactionReportForm()))

def open_pnl_report_form(self, **event_args):
    from ..Forms.Investment.InvestmentReportSearchPanelForm import InvestmentReportSearchPanelForm
    from ..Forms.Investment.PnLReportForm import PnLReportForm
    anvil.get_open_form().content_panel.clear()
    anvil.get_open_form().content_panel.add_component(InvestmentReportSearchPanelForm(PnLReportForm()))

def open_exp_list_form(self, **event_args):
    from ..Forms.Expense.ExpenseReportSearchPanelForm import ExpenseReportSearchPanelForm
    from ..Forms.Expense.ExpenseReportForm import ExpenseReportForm
    anvil.get_open_form().content_panel.clear()
    anvil.get_open_form().content_panel.add_component(ExpenseReportSearchPanelForm(ExpenseReportForm()))

def open_exp_analysis_form(self, **event_args):
    from ..Forms.Expense.ExpenseReportSearchPanelForm import ExpenseReportSearchPanelForm
    from ..Forms.Expense.ExpenseAnalysisForm import ExpenseAnalysisForm
    anvil.get_open_form().content_panel.clear()
    anvil.get_open_form().content_panel.add_component(ExpenseReportSearchPanelForm(ExpenseAnalysisForm()))

def open_unittest_main_form(self, **event_args):
    from ..Forms.UnitTest.UnitTestMainForm import UnitTestMainForm
    anvil.get_open_form().content_panel.clear()
    anvil.get_open_form().content_panel.add_component(UnitTestMainForm())

def open_poc_main_form(self, **event_args):
    from .._POC.form_poc_main import form_poc_main
    anvil.get_open_form().content_panel.clear()
    anvil.get_open_form().content_panel.add_component(form_poc_main())
