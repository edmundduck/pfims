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

    def validate(self, **event_args):
        """This method is called when the button is clicked"""
        v = Validator()

        # To access the parent form, needs to access 3 parent levels ...
        # self.parent = Repeating Panel
        # self.parent.parent = Data Grid
        # self.parent.parent.parent = Parent Form
        #print(self.parent.parent.parent.valerror_1.text)
        v.display_when_invalid(self.parent.parent.parent.valerror_title)
        v.require_date_field(self.row_date, self.parent.parent.parent.valerror_1, True)
        v.require_text_field(self.row_acct, self.parent.parent.parent.valerror_2, True)
        v.require_text_field(self.row_amt, self.parent.parent.parent.valerror_3, True)

        if v.is_valid():
            self.row_sell_price.text = anvil.server.call('cal_price' ,self.row_sales.text, self.row_qty.text)
            self.row_buy_price.text = anvil.server.call('cal_price', self.row_cost.text, self.row_qty.text)
            self.row_pnl.text = anvil.server.call('cal_profit', self.row_sales.text, self.row_cost.text, self.row_fee.text)

            self.input_data_panel_readonly.visible = True
            self.input_data_panel_editable.visible = False

            glo.track_input_stock_journals_change()
            self.parent.raise_event('x-disable-submit-button')

            #self.parent.raise_event('x-save-change', iid=self.row_iid.text)
            self.parent.raise_event('x-save-change')

    def button_delete_click(self, **event_args):
        """This method is called when the button is clicked"""
        if self.item['iid'] is not None: glo.add_deleted_row(self.item['iid'])
        self.remove_from_parent()
