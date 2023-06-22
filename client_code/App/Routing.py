import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

# This is a module.
# You can define variables and functions here, and use them from any form. For example, in a top-level form:

def open_exp_input_form(self, tab_id=None, data=None, **event_args):
    from ..Input.ExpenseInputForm import ExpenseInputForm
    # The following doesn't work, but open_acct_maint_form one works, no idea why
    # self.clear()
    # self.add_component(ExpenseInputForm())
    anvil.get_open_form().content_panel.clear()
    anvil.get_open_form().content_panel.add_component(ExpenseInputForm(tab_id=tab_id, data=data))

def open_exp_file_upload_form(self, **event_args):
    from ..Input.ExpenseFileUploadForm import ExpenseFileUploadForm
    anvil.get_open_form().content_panel.clear()
    anvil.get_open_form().content_panel.add_component(ExpenseFileUploadForm())

def open_exp_file_upload_form_p2(self, dataframe, labels, **event_args):
    from ..Input.ExpenseFileUploadFormP2 import ExpenseFileUploadFormP2
    anvil.get_open_form().content_panel.clear()
    anvil.get_open_form().content_panel.add_component(ExpenseFileUploadFormP2(dataframe, labels))

def open_upload_mapping_form(self, **event_args):
    from ..Input.FileUploadMappingForm import FileUploadMappingForm
    anvil.get_open_form().content_panel.clear()
    anvil.get_open_form().content_panel.add_component(FileUploadMappingForm())

def open_lbl_maint_form(self, **event_args):
    from ..Input.LabelMaintForm import LabelMaintForm
    anvil.get_open_form().content_panel.clear()
    anvil.get_open_form().content_panel.add_component(LabelMaintForm())
    
def open_acct_maint_form(self, **event_args):
    from ..Input.AccountMaintForm import AccountMaintForm
    anvil.get_open_form().content_panel.clear()
    anvil.get_open_form().content_panel.add_component(AccountMaintForm())
