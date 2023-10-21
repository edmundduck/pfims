from ._anvil_designer import PDFColumnsMappingRPTemplateTemplate
from anvil import *
from .....Utils.ClientCache import ClientCache
from .....Utils import Constants as const
from .....Utils.Logger import ClientLogger
from .....Utils.Validation import Validator

logger = ClientLogger()

class PDFColumnsMappingRPTemplate(PDFColumnsMappingRPTemplateTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        # Any code you write here will run before the form opens.
        cache_exp_tbl_def = ClientCache('generate_expense_tbl_def_dropdown')
        self.dropdown_col_map_to.items = cache_exp_tbl_def.get_cache()
        self.dropdown_sign.items = (('+ Inflow', '+'), ('- Outflow', '-'))
        self.dropdown_sign.visible = False

    def dropdown_col_map_to_change(self, **event_args):
        """This method is called when an item is selected"""
        from .....Entities.ExpenseTransaction import ExpenseTransaction
        logger.debug("self.dropdown_col_map_to.selected_value=", self.dropdown_col_map_to.selected_value)
        if self.dropdown_col_map_to.selected_value is not None and self.dropdown_col_map_to.selected_value[0] == ExpenseTransaction.field_amount():
            self.dropdown_sign.visible = True
        else:
            self.dropdown_sign.visible = False

    def cb_required_change(self, **event_args):
        """This method is called when this checkbox is checked or unchecked"""
        if self.cb_required.checked == True:
            self.dropdown_col_map_to.visible = True
        else:    
            self.dropdown_col_map_to.selected_value = None
            self.dropdown_col_map_to.visible = False
            self.dropdown_sign.selected_value = None
            self.dropdown_sign.visible = False

    def _validate(self, **event_args):
        """This method is called when the button is clicked"""
        from .....Entities.ExpenseTransaction import ExpenseTransaction
        v = Validator()
        cache_exp_tbl_def = ClientCache('generate_expense_tbl_def_dropdown')

        logger.trace("self.parent.parent.parent.parent.valerror_1.text=", self.parent.parent.parent.parent.valerror_1.text)
        v.display_when_invalid(self.parent.parent.parent.parent.valerror_title)
        v.require_selected_dependent_on_checkbox(self.dropdown_col_map_to, self.cb_required, self.parent.parent.parent.parent.valerror_1, True)
        v.require_selected_dependent_on_dropdown(self.dropdown_sign, self.dropdown_col_map_to, cache_exp_tbl_def.get_complete_key(ExpenseTransaction.field_amount()), self.parent.parent.parent.parent.valerror_2, True)
        v.highlight_when_invalid(self.dropdown_col_map_to, const.ColorSchemes.VALID_ERROR, const.ColorSchemes.VALID_NORMAL)
        v.highlight_when_invalid(self.dropdown_sign, const.ColorSchemes.VALID_ERROR, const.ColorSchemes.VALID_NORMAL)

        return v.is_valid()
