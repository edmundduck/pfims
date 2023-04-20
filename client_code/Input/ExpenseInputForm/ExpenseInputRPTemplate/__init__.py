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
        self._generateall_selected_labels(self.hidden_lbls_id.text)
        self.add_event_handler('x-create-lbl-button', self._create_lbl_button)
        self.row_panel_labels.full_width_row = False
        
        # if self.item['amt'] < 0:
        #     self.foreground = 'Black'
        # else:
        #     self.foreground = 'Green'

    def _generateall_selected_labels(self, label_list):
        if label_list not in ('', None):
            lbl_attr = cache.get_caching_labels_dropdown()
            print(lbl_attr)
            for i in label_list.split(","):
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
        loc = self.hidden_lbls_id.text.find(str(b.tag))
        if loc+len(str(b.tag))+1 >= len(self.hidden_lbls_id.text):
            self.hidden_lbls_id.text = self.hidden_lbls_id.text[:loc]
        else:
            self.hidden_lbls_id.text = self.hidden_lbls_id.text[:loc] + self.hidden_lbls_id.text[loc+len(str(b.tag))+1]
        b.remove_from_parent()
        self.parent.raise_event('x-switch-to-save-button')

    def _create_lbl_button(self, selected_lid, selected_lname, **event_args):
        if self.row_cb_datarow.checked is True:
            b = Button(text=selected_lname,
                    icon='fa:minus',
                    foreground="White",
                    background="Blue",
                    font_size=8,
                    align="left",
                    tag=selected_lid
                    )
            self.hidden_lbls_id.text = self.hidden_lbls_id.text + str(selected_lid) + ","
            # Without self.item['labels'] assignment the data binding won't work
            self.item['labels'] = self.hidden_lbls_id.text
            self.row_panel_labels.add_component(b, False, name=selected_lid, expand=True)
            b.set_event_handler('click', self.label_button_minus_click)
            self.parent.raise_event('x-switch-to-save-button')
        
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
        v.highlight_when_invalid(self.row_date, glo.validation_errfield_colour(), self.row_date.background)
        v.highlight_when_invalid(self.row_acct, glo.validation_errfield_colour(), self.row_acct.background)
        v.highlight_when_invalid(self.row_amt, glo.validation_errfield_colour(), self.row_amt.background)

        return v.is_valid()

    def button_delete_click(self, **event_args):
        """This method is called when the button is clicked"""
        self.parent.raise_event('x-switch-to-save-button')
        if self.item.get('iid') is not None: glo.add_deleted_row(self.item['iid'])
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
