from ._anvil_designer import ExpenseInputRPTemplateTemplate
from anvil import *
import anvil.server
from .....Controllers import ExpenseInputController
from .....Entities.ExpenseTransaction import ExpenseTransaction
from .....Utils.ButtonModerator import ButtonModerator
from .....Utils.Logger import ClientLogger

logger = ClientLogger()
btnmod = ButtonModerator()

class ExpenseInputRPTemplate(ExpenseInputRPTemplateTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        # Any code you write here will run when the form opens.
        self.row_acct.items = ExpenseInputController.generate_accounts_dropdown()
        self.row_acct.selected_value = ExpenseInputController.get_account_dropdown_selected_item(self.row_acct.selected_value)

        lbl_list = ExpenseInputController.generate_label_id_list(self.item[ExpenseTransaction.field_labels()])
        self._generateall_selected_labels(lbl_list)
        self.tag = {ExpenseTransaction.field_labels(): lbl_list}
        self.item[ExpenseTransaction.field_labels()] = lbl_list
        self.add_event_handler('x-create-lbl-button', self._create_lbl_button)
        self.add_event_handler('x-set-remarks-visible', self._set_remarks_visible)
        self.add_event_handler('x-set-stmt-dtl-visible', self._set_stmt_dtl_visible)
        # This setting allows multiple buttons to place in the same row
        # https://anvil.works/forum/t/add-component-and-dynamically-positioning-components-side-by-side/14793
        self.row_panel_labels.full_width_row = False
        
    def _generateall_selected_labels(self, label_id_list):
        from .....Utils.Constants import Icons, Roles
        lbls_list = ExpenseInputController.generate_label_objects(label_id_list)
        for lbl in lbls_list:
            b = Button(
                text=lbl.get_name(),
                # icon=Icons.REMOVE,
                role=Roles.LABEL,
                align="left",
                spacing_above="small",
                spacing_below="small",
                tag=lbl.get_id()
            )
            # self.row_panel_labels.add_component(b, False, name=lbl.get_name(), expand=True)
            self.row_panel_labels.add_component(b, False, name=lbl.get_name())
            b.set_event_handler('click', self.label_button_minus_click)
        return label_id_list

    def label_button_minus_click(self, **event_args):
        b = event_args['sender']
        # Without self.item[ExpenseTransaction.field_labels()] assignment the data binding won't work
        self.item[ExpenseTransaction.field_labels()] = ExpenseInputController.remove_label_id(self.tag.get(ExpenseTransaction.field_labels(), []), b.tag)
        self.tag.update({ExpenseTransaction.field_labels(): self.item[ExpenseTransaction.field_labels()]})
        b.remove_from_parent()
        self.parent.raise_event('x-switch-to-save-button')

    def _create_lbl_button(self, selected_lid, selected_lname, **event_args):
        from .....Utils.Constants import Icons, Roles
        if self.row_cb_datarow.checked is True:
            b = Button(
                text=selected_lname,
                # icon=Icons.REMOVE,
                role=Roles.LABEL,
                align="left",
                spacing_above="small",
                spacing_below="small",
                tag=selected_lid
            )
            # Without self.item[ExpenseTransaction.field_labels()] assignment the data binding won't work
            self.item[ExpenseTransaction.field_labels()] = ExpenseInputController.add_label_id(self.tag.get(ExpenseTransaction.field_labels(), []), selected_lid)
            self.tag.update({ExpenseTransaction.field_labels(): self.item[ExpenseTransaction.field_labels()]})
            # self.row_panel_labels.add_component(b, False, name=selected_lid, expand=True)
            self.row_panel_labels.add_component(b, False, name=selected_lid)
            b.set_event_handler('click', self.label_button_minus_click)
            self.parent.raise_event('x-switch-to-save-button')
        
    def _validate(self, **event_args):
        """This method is called when the button is clicked"""
        from .....Utils.Validation import Validator
        
        v = Validator()
        # To access the parent form, needs to access 3 parent levels ...
        # self.parent = Repeating Panel
        # self.parent.parent = Data Grid
        # self.parent.parent.parent = Parent Form
        v.display_when_invalid(self.parent.parent.parent.valerror_title)
        v.require_date_field(self.row_date, self.parent.parent.parent.valerror_1, True)
        v.require_selected(self.row_acct, self.parent.parent.parent.valerror_2, True)
        v.require_text_field(self.row_amt, self.parent.parent.parent.valerror_3, True)
        v.highlight_when_invalid(self.row_date)
        v.highlight_when_invalid(self.row_acct)
        v.highlight_when_invalid(self.row_amt)

        return v.is_valid()

    def _set_remarks_visible(self, vis, **event_args):
        self.row_remarks.visible = vis
        
    def _set_stmt_dtl_visible(self, vis, **event_args):
        self.row_stmt_dtl.visible = vis

    @btnmod.one_click_only
    def button_delete_click(self, **event_args):
        """This method is called when the button is clicked"""
        ExpenseInputController.delete_item(self.item.get('iid', None))
        if self.item.get('iid') is not None: 
            self.parent.raise_event('x-deleted-row')
        self.parent.raise_event('x-switch-to-save-button')
        for i in self.item.keys():
            # To allow reload_rp_data to filter this record.
            self.item[i] = None 
        self.remove_from_parent()
        # event_args['sender'].parent.trigger('writeback')
        
    def row_date_change(self, **event_args):
        """This method is called when the selected date changes"""
        self.parent.raise_event('x-switch-to-save-button')

    def row_acct_change(self, **event_args):
        """This method is called when an item is selected"""
        self.item[ExpenseTransaction.field_account()] = self.row_acct.selected_value[0] if isinstance(self.row_acct.selected_value, list) else self.row_acct.selected_value
        self.parent.raise_event('x-switch-to-save-button')

    def row_amt_change(self, **event_args):
        """This method is called when the text in this text box is edited"""
        self.parent.raise_event('x-switch-to-save-button')

    def row_amt_lost_focus(self, **event_args):
        """This method is called when the TextBox loses focus"""
        self.row_amt.text = ExpenseInputController.add_currency_symbol(self.row_acct.selected_value, self.row_amt.text)

    def row_amt_focus(self, **event_args):
        """This method is called when the TextBox gets focus"""
        self.row_amt.text = ExpenseInputController.remove_currency_symbol(self.row_amt.text)

    def row_remarks_change(self, **event_args):
        """This method is called when the text in this text box is edited"""
        self.parent.raise_event('x-switch-to-save-button')

    def row_stmt_dtl_change(self, **event_args):
        """This method is called when the text in this text box is edited"""
        self.parent.raise_event('x-switch-to-save-button')
