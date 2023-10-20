from ._anvil_designer import ExpenseFilePDFImportFormTemplate
from anvil import *
import anvil.server
from ...Controllers import ExpenseFilePDFImportController
from ...Utils.ButtonModerator import ButtonModerator
from ...Utils.Logger import ClientLogger
from ...Utils.Validation import Validator

logger = ClientLogger()
btnmod = ButtonModerator()

class ExpenseFilePDFImportForm(ExpenseFilePDFImportFormTemplate):
    def __init__(self, data, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        # Any code you write here will run when the form opens.
        self.dropdown_tabs.items = ExpenseFilePDFImportController.generate_expense_tabs_dropdown()
        self.tag = {'data': data}
        logger.debug("self.tag=", self.tag)
        # Transpose Dict of Lists (DL) to List of Dicts (LD)
        # Ref - https://stackoverflow.com/questions/37489245/transposing-pivoting-a-dict-of-lists-in-python
        self.cols_mapping_panel.items = ExpenseFilePDFImportController.populate_repeating_panel_items(data)
        logger.trace("self.cols_mapping_panel.items=", self.cols_mapping_panel.items)
        self.dropdown_account.items = ExpenseFilePDFImportController.generate_accounts_dropdown()
        self.dropdown_account.visible = False
        self.dropdown_labels.items = ExpenseFilePDFImportController.generate_labels_dropdown()
        self.dropdown_labels.visible = False

    def button_nav_upload_mapping_click(self, **event_args):
        """This method is called when the button is clicked"""
        from ....Utils import Routing
        Routing.open_upload_mapping_form(self)

    def button_nav_input_exp_click(self, **event_args):
        """This method is called when the button is clicked"""
        from ....Utils import Routing
        Routing.open_exp_input_form(self)

    @btnmod.one_click_only
    @logger.log_function
    def button_next_click(self, **event_args):
        """This method is called when the button is clicked"""
        from ....Utils import Routing
        from ....Utils.Constants import ColorSchemes
        
        """Validation"""
        v = Validator()

        v.display_when_invalid(self.valerror_title)
        v.require_selected_dependent_on_checkbox(self.dropdown_account, self.cb_account, self.valerror_3, True)
        v.require_selected_dependent_on_checkbox(self.dropdown_labels, self.cb_labels, self.valerror_4, True)
        v.highlight_when_invalid(self.dropdown_account, ColorSchemes.VALID_ERROR, ColorSchemes.VALID_NORMAL)
        v.highlight_when_invalid(self.dropdown_labels, ColorSchemes.VALID_ERROR, ColorSchemes.VALID_NORMAL)

        result = all(c._validate() for c in self.cols_mapping_panel.get_components())
        if result is not True:
            return

        if v.is_valid():
            selected_account = self.dropdown_account.selected_value[0] if self.dropdown_account.selected_value else None
            selected_label = self.dropdown_labels.selected_value[0] if self.dropdown_labels.selected_value else None
            df = anvil.server.call('update_pdf_mapping', self.tag.get('data'), self.cols_mapping_panel.items, selected_account, selected_label)
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
