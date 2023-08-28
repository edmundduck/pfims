from ._anvil_designer import ExpenseFilePDFImportFormTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from ...Utils import Routing
from ...Utils import Caching as cache
from ...Utils.Logger import ClientLogger
from ...Utils.Validation import Validator

logger = ClientLogger()

class ExpenseFilePDFImportForm(ExpenseFilePDFImportFormTemplate):
    def __init__(self, data, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        # Any code you write here will run when the form opens.
        self.dropdown_tabs.items = anvil.server.call('generate_expensetabs_dropdown')
        self.tag = {'data': data}
        logger.debug("self.tag=", self.tag)
        # Transpose Dict of Lists (DL) to List of Dicts (LD)
        # Ref - https://stackoverflow.com/questions/37489245/transposing-pivoting-a-dict-of-lists-in-python
        DL = {
            'srccol': data[0],
            'tgtcol': [None for i in range(len(data[0]))],
            'sign': [None for i in range(len(data[0]))]
        }
        logger.trace("DL=", DL)
        self.cols_mapping_panel.items = [dict(zip(DL, col)) for col in zip(*DL.values())]
        logger.trace("self.cols_mapping_panel.items=", self.cols_mapping_panel.items)
        self.dropdown_account.items = cache.accounts_dropdown()
        self.dropdown_account.visible = False
        self.dropdown_labels.items = cache.labels_dropdown()
        self.dropdown_labels.visible = False

    def button_nav_upload_mapping_click(self, **event_args):
        """This method is called when the button is clicked"""
        Routing.open_upload_mapping_form(self)

    def button_nav_input_exp_click(self, **event_args):
        """This method is called when the button is clicked"""
        Routing.open_exp_input_form(self)

    @logger.log_function
    def button_next_click(self, **event_args):
        """This method is called when the button is clicked"""
        """Validation"""
        result = all(c._validate() for c in self.cols_mapping_panel.get_components())
        if result is not True:
            return

        print(f"{self.dropdown_account.selected_value}, {self.dropdown_labels.selected_value}")
        df = anvil.server.call('update_pdf_mapping', data=self.tag.get('data'), mapping=self.cols_mapping_panel.items, \
                              account=self.dropdown_account.selected_value[0], labels=eval(self.dropdown_labels.selected_value).get('id'))
        # logger.debug("df=", df)
        Routing.open_exp_input_form(self, tab_id=self.dropdown_tabs.selected_value, data=df)

    def cb_account_change(self, **event_args):
        """This method is called when this checkbox is checked or unchecked"""
        if self.cb_account.checked:
            self.dropdown_account.visible = True
        else:
            self.dropdown_account.visible = False
            self.dropdown_account.selected_value = None

    def cb_labels_change(self, **event_args):
        """This method is called when this checkbox is checked or unchecked"""
        if self.cb_labels.checked:
            self.dropdown_labels.visible = True
        else:
            self.dropdown_labels.visible = False
            self.dropdown_labels.selected_value = None
