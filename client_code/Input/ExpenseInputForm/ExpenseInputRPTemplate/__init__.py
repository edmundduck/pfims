from ._anvil_designer import ExpenseInputRPTemplateTemplate
from anvil import *
import anvil.users
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from ....App import Global as glo
from ....App import Caching as cache
from ....App.Validation import Validator

class ExpenseInputRPTemplate(ExpenseInputRPTemplateTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        # Any code you write here will run when the form opens.
        self.row_acct.items = cache.get_caching_accounts()
        # self.add_event_handler('x-validate', self._validate)
        
        # if self.item['amt'] < 0:
        #     self.foreground = 'Black'
        # else:
        #     self.foreground = 'Green'

    def _generateall_selected_labels(self, label_list):
        for i in label_list:
            lbl_attr = anvil.server.call('get_selected_label_attr', i)
            b = Button(text=lbl_attr[1],
                    icon='fa:minus',
                    foreground="White",
                    background="Blue",
                    font_size=8,
                    align="left",
                    tag=lbl_attr[0]
                    )
            self.row_panel_labels.add_component(b, False, name=lbl_attr[0])
            b.set_event_handler('click', self.label_button_minus_click)

    def label_button_minus_click(self, **event_args):
        b = event_args['sender']
        print(b.text)
        print(b.id)
        b.remove_from_parent()

    def _validate(self, **event_args):
        """This method is called when the button is clicked"""
        if self.row_acct.selected_value in (None, '') and self.row_amt.text in (None, '') and self.row_date.date in (None, ''):
            return True
        v = Validator()

        # To access the parent form, needs to access 3 parent levels ...
        # self.parent = Repeating Panel
        # self.parent.parent = Data Grid
        # self.parent.parent.parent = Parent Form
        #print(self.parent.parent.parent.valerror_1.text)
        v.display_when_invalid(self.parent.parent.parent.valerror_title)
        v.require_date_field(self.row_date, self.parent.parent.parent.valerror_1, True)
        v.require_selected(self.row_acct, self.parent.parent.parent.valerror_2, True)
        v.require_text_field(self.row_amt, self.parent.parent.parent.valerror_3, True)
        v.highlight_when_invalid(self.row_date, 'rgb(245,135,200)', self.row_date.background)
        v.highlight_when_invalid(self.row_acct, 'rgb(245,135,200)', self.row_acct.background)
        v.highlight_when_invalid(self.row_amt, 'rgb(245,135,200)', self.row_amt.background)

        return v.is_valid()

    def button_delete_click(self, **event_args):
        """This method is called when the button is clicked"""
        self.parent.raise_event('x-switch-to-save-button')
        if self.item['iid'] is not None: glo.add_deleted_row(self.item['iid'])
        self.remove_from_parent()

    def row_date_change(self, **event_args):
        """This method is called when the selected date changes"""
        self.parent.raise_event('x-switch-to-save-button')

    def row_acct_change(self, **event_args):
        """This method is called when an item is selected"""
        self.parent.raise_event('x-switch-to-save-button')

    def row_amt_change(self, **event_args):
        """This method is called when the text in this text box is edited"""
        self.parent.raise_event('x-switch-to-save-button')

    def row_remarks_change(self, **event_args):
        """This method is called when the text in this text box is edited"""
        self.parent.raise_event('x-switch-to-save-button')

    def row_stmt_dtl_change(self, **event_args):
        """This method is called when the text in this text box is edited"""
        self.parent.raise_event('x-switch-to-save-button')
