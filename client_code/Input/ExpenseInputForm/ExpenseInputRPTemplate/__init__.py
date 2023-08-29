from ._anvil_designer import ExpenseInputRPTemplateTemplate
from anvil import *
import anvil.users
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from ....Utils import Constants as const
from ....Utils.Constants import ExpenseDBTableDefinion as exptbl
from ....Utils import Caching as cache
from ....Utils.Validation import Validator
from ....Utils.Logger import ClientLogger

logger = ClientLogger()

class ExpenseInputRPTemplate(ExpenseInputRPTemplateTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        # Any code you write here will run when the form opens.
        self.row_acct.items = cache.accounts_dropdown()
        # Account dropdown key is a list. If it's just int which is populated from file upload, then has to lookup the desc to form a key
        acct_dict = cache.accounts_dict()
        logger.debug("self.row_acct.selected_value=", self.row_acct.selected_value)
        if self.row_acct.selected_value is not None and not isinstance(self.row_acct.selected_value, list):
            self.row_acct.selected_value = [self.row_acct.selected_value, acct_dict.get(self.row_acct.selected_value, None)]
        
        self._generateall_selected_labels(self.hidden_lbls_id.text)
        self.add_event_handler('x-create-lbl-button', self._create_lbl_button)
        self.add_event_handler('x-set-remarks-visible', self._set_remarks_visible)
        self.add_event_handler('x-set-stmt-dtl-visible', self._set_stmt_dtl_visible)
        # This setting allows multiple buttons to place in the same row
        # https://anvil.works/forum/t/add-component-and-dynamically-positioning-components-side-by-side/14793
        self.row_panel_labels.full_width_row = False
        
    @logger.log_function
    def _generateall_selected_labels(self, label_list):
        if label_list not in ('', None):
            lbls = cache.labels_list()
            trimmed_list = label_list[:-1].split(",") if label_list[-1] == ',' else label_list.split(",")
            logger.trace(f"trimmed_list={trimmed_list}, lbls={lbls}")
            for i in trimmed_list:
                # Don't generate label if following conditions are met -
                # 1. label ID is 0 (which is possible from file upload)
                # 2. label ID is not integer
                # 3. label ID is NaN
                if i.isdigit() and int(i) != 0:
                    lbl_name = None
                    for j in lbls:
                        if str(j.get("id")).strip() == i:
                            lbl_name = j.get("name").strip()
                    b = Button(text=lbl_name,
                            # icon=const.Icons.REMOVE,
                            foreground=const.ColorSchemes.BUTTON_FG,
                            background=const.ColorSchemes.BUTTON_BG,
                            font_size=10,
                            align="left",
                            spacing_above="small",
                            spacing_below="small",
                            tag=i
                            )
                    # self.row_panel_labels.add_component(b, False, name=lbl_name, expand=True)
                    self.row_panel_labels.add_component(b, False, name=lbl_name)
                    b.set_event_handler('click', self.label_button_minus_click)

    @logger.log_function
    def label_button_minus_click(self, **event_args):
        b = event_args['sender']
        loc = self.hidden_lbls_id.text.find(str(b.tag))
        if loc+len(str(b.tag))+1 >= len(self.hidden_lbls_id.text):
            self.hidden_lbls_id.text = self.hidden_lbls_id.text[:loc]
        else:
            self.hidden_lbls_id.text = self.hidden_lbls_id.text[:loc] + self.hidden_lbls_id.text[(loc+len(str(b.tag))+1):]
        # Without self.item[exptbl.Labels] assignment the data binding won't work
        self.item[exptbl.Labels] = self.hidden_lbls_id.text
        b.remove_from_parent()
        self.parent.raise_event('x-switch-to-save-button')

    @logger.log_function
    def _create_lbl_button(self, selected_lid, selected_lname, **event_args):
        if self.row_cb_datarow.checked is True:
            b = Button(text=selected_lname,
                    # icon=const.Icons.REMOVE,
                    foreground=const.ColorSchemes.BUTTON_FG,
                    background=const.ColorSchemes.BUTTON_BG,
                    font_size=10,
                    align="left",
                    spacing_above="small",
                    spacing_below="small",
                    tag=selected_lid
                    )
            # Label ID from file upload can be withouth comma, hence needs to add back otherwise labels display will be messed up
            if self.hidden_lbls_id.text not in (None, '') and self.hidden_lbls_id.text[-1] != ',':
                self.hidden_lbls_id.text = self.hidden_lbls_id.text + ','
            self.hidden_lbls_id.text = self.hidden_lbls_id.text + str(selected_lid) + ','
            # Without self.item[exptbl.Labels] assignment the data binding won't work
            self.item[exptbl.Labels] = self.hidden_lbls_id.text
            # self.row_panel_labels.add_component(b, False, name=selected_lid, expand=True)
            self.row_panel_labels.add_component(b, False, name=selected_lid)
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
        logger.trace("self.parent.parent.parent.valerror_1.text=", self.parent.parent.parent.valerror_1.text)
        v.display_when_invalid(self.parent.parent.parent.valerror_title)
        v.require_date_field(self.row_date, self.parent.parent.parent.valerror_1, True)
        v.require_selected(self.row_acct, self.parent.parent.parent.valerror_2, True)
        v.require_text_field(self.row_amt, self.parent.parent.parent.valerror_3, True)
        v.highlight_when_invalid(self.row_date, const.ColorSchemes.VALID_ERROR, const.ColorSchemes.VALID_NORMAL)
        v.highlight_when_invalid(self.row_acct, const.ColorSchemes.VALID_ERROR, const.ColorSchemes.VALID_NORMAL)
        v.highlight_when_invalid(self.row_amt, const.ColorSchemes.VALID_ERROR, const.ColorSchemes.VALID_NORMAL)

        return v.is_valid()

    def _set_remarks_visible(self, vis, **event_args):
        self.row_remarks.visible = vis
        
    def _set_stmt_dtl_visible(self, vis, **event_args):
        self.row_stmt_dtl.visible = vis

    @logger.log_function
    def button_delete_click(self, **event_args):
        """This method is called when the button is clicked"""
        self.parent.raise_event('x-switch-to-save-button')
        if self.item.get('iid') is not None: cache.add_deleted_row(self.item['iid'])
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
