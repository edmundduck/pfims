from ._anvil_designer import ExpenseInputRPTemplateTemplate
from anvil import *
import anvil.users
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from .... import Global as glo
from ....Validation import Validator

class ExpenseInputRPTemplate(ExpenseInputRPTemplateTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        # Any code you write here will run when the form opens.
        self.row_acct.items = anvil.server.call('generate_accounts_dropdown')
        # isButtonGenerated = False
        # for i in self.row_panel_labels.get_components():
        #     if isinstance(i, CheckBox):
        #         isButtonGenerated = True
        # if not isButtonGenerated:
        #     pass
            # self._generateall_selected_labels(self.item['labels'])
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

    def button_edit_click(self, **event_args):
        """This method is called when the button is clicked"""
        self.row_selldate.date = self.item['sell_date']
        self.row_buydate.date = self.item['buy_date']
        self.row_symbol.text = self.item['symbol']
        self.row_qty.text = self.item['qty']
        self.row_sales.text = self.item['sales']
        self.row_cost.text = self.item['cost']
        self.row_fee.text = self.item['fee']
        self.row_sell_price.text = self.item['sell_price']
        self.row_buy_price.text = self.item['buy_price']
        self.row_pnl.text = self.item['pnl']
        self.row_iid.text = self.item['iid']

        self.input_data_panel_readonly.visible = False
        self.input_data_panel_editable.visible = True

        glo.track_input_stock_journals_change()

    def button_save_click(self, **event_args):
        """This method is called when the button is clicked"""
        v = Validator()

        # To access the parent form, needs to access 3 parent levels ...
        # self.parent = Repeating Panel
        # self.parent.parent = Data Grid
        # self.parent.parent.parent = Parent Form
        #print(self.parent.parent.parent.valerror_1.text)
        v.display_when_invalid(self.parent.parent.parent.valerror_title)
        v.require_date_field(self.row_selldate, self.parent.parent.parent.valerror_1, True)
        v.require_date_field(self.row_buydate, self.parent.parent.parent.valerror_2, True)
        v.require_text_field(self.row_symbol, self.parent.parent.parent.valerror_3, True)
        v.require_text_field(self.row_qty, self.parent.parent.parent.valerror_4, True)
        v.require_text_field(self.row_sales, self.parent.parent.parent.valerror_5, True)
        v.require_text_field(self.row_cost, self.parent.parent.parent.valerror_6, True)
        v.require_text_field(self.row_fee, self.parent.parent.parent.valerror_7, True)

        if v.is_valid():
            self.row_sell_price.text = anvil.server.call('cal_price' ,self.row_sales.text, self.row_qty.text)
            self.row_buy_price.text = anvil.server.call('cal_price', self.row_cost.text, self.row_qty.text)
            self.row_pnl.text = anvil.server.call('cal_profit', self.row_sales.text, self.row_cost.text, self.row_fee.text)

            # Lesson learnt ... THIS LINE DOESN'T WORK!!
            # new_data = {"sell_date": self.row_selldate.date,
            #                "buy_date": self.row_buydate.date,
            #                "symbol": self.row_symbol.text,
            #                "qty": self.row_qty.text,
            #                "sales": self.row_sales.text,
            #                "cost": self.row_cost.text,
            #                "sell_price": self.row_sell_price.text,
            #                "buy_price": self.row_buy_price.text,
            #                "iid": self.row_iid.text}
            # self.item = self.row_symbol.text
            # self.item = new_data
            self.item = {"sell_date": self.row_selldate.date,
                        "buy_date": self.row_buydate.date,
                        "symbol": self.row_symbol.text,
                        "qty": self.row_qty.text,
                        "sales": float(self.row_sales.text),
                        "cost": float(self.row_cost.text),
                        "fee": float(self.row_fee.text),
                        "sell_price": self.row_sell_price.text,
                        "buy_price": self.row_buy_price.text,
                        "pnl": self.row_pnl.text,
                        "iid": self.row_iid.text}

            self.input_data_panel_readonly.visible = True
            self.input_data_panel_editable.visible = False

            glo.track_input_stock_journals_change()
            self.parent.raise_event('x-disable-submit-button')

            #self.parent.raise_event('x-save-change', iid=self.row_iid.text)
            self.parent.raise_event('x-save-change')

    def button_delete_click(self, **event_args):
        """This method is called when the button is clicked"""
        if self.item['iid'] is not None: glo.add_deleted_row(self.item['iid'])
        glo.track_input_stock_journals_change()
        self.parent.raise_event('x-disable-submit-button')
        self.remove_from_parent()
