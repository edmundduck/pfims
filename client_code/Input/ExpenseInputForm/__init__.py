from ._anvil_designer import ExpenseInputFormTemplate
from anvil import *
import anvil.users
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from datetime import date
from ...Utils import Constants as const
from ...Utils import Routing
from ...Utils import Caching as cache
from ...Utils.Constants import ExpenseDBTableDefinion as exptbl
from ...Utils.Validation import Validator
from ...Utils.Logger import ClientLogger
from .ExpenseInputRPTemplate import ExpenseInputRPTemplate as expintmpl

logger = ClientLogger()

class ExpenseInputForm(ExpenseInputFormTemplate):
    def __init__(self, tab_id=None, data=None, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        # Any code you write here will run when the form opens.
        self.button_add_rows.text = self.button_add_rows.text.replace('%n', str(const.ExpenseConfig.DEFAULT_ROW_NUM))
        self.input_repeating_panel.add_event_handler('x-switch-to-save-button', self._switch_to_save_button)

        if tab_id is not None:
            self.dropdown_tabs.selected_value = tab_id
            self.tab_name.text = tab_id[1]
            logger.debug("self.dropdown_tabs.selected_value=", self.dropdown_tabs.selected_value)

        if data is None:
            # Initiate repeating panel items to an empty list otherwise will throw NoneType error
            self.input_repeating_panel.items = [{} for i in range(const.ExpenseConfig.DEFAULT_ROW_NUM)]
        else:
            logger.info(f"{len(data)} rows are imported to {__name__}.")
            self.input_repeating_panel.items = data
        cache.deleted_row_reset()

    def _switch_to_submit_button(self, **event_args):
        self.button_save_exptab.text = const.ExpenseConfig.BUTTON_SUBMIT_TEXT
        self.button_save_exptab.background = const.ColorSchemes.THEME_PRIM
        self.button_save_exptab.remove_event_handler('click')
        self.button_save_exptab.add_event_handler('click', self.button_submit_click)

    def _switch_to_save_button(self, **event_args):
        self.button_save_exptab.text = const.ExpenseConfig.BUTTON_DRAFT_TEXT
        self.button_save_exptab.background = const.ColorSchemes.THEME_SEC
        self.button_save_exptab.remove_event_handler('click')
        self.button_save_exptab.add_event_handler('click', self.button_save_click)
        
    @logger.log_function
    def _getall_selected_labels(self):
        label_list = []
        for i in self.panel_labels.get_components():
            if isinstance(i, Button):
                if i.icon == const.Icons.REMOVE:
                    label_list += [i.tag]
        return label_list

    def button_file_import_click(self, **event_args):
        """This method is called when the button is clicked"""
        Routing.open_exp_file_upload_form(self)
        
    def button_add_rows_click(self, **event_args):
        """This method is called when the button is clicked"""
        self.input_repeating_panel.items = [{} for i in range(const.ExpenseConfig.DEFAULT_ROW_NUM)] + self.input_repeating_panel.items

    def button_lbl_maint_click(self, **event_args):
        """This method is called when the button is clicked"""
        Routing.open_lbl_maint_form(self)

    def button_acct_maint_click(self, **event_args):
        """This method is called when the button is clicked"""
        Routing.open_acct_maint_form(self)

    def dropdown_labels_show(self, **event_args):
        """This method is called when the DropDown is shown on the screen"""
        self.dropdown_labels.items = cache.labels_dropdown()

    @logger.log_function
    def dropdown_labels_change(self, **event_args):
        """This method is called when an item is selected"""
        # Case 001 - string dict key handling review
        # selected_lid, selected_lname = self.dropdown_labels.selected_value.values() if self.dropdown_labels.selected_value is not None else [None, None]
        selected_lid, selected_lname = eval(self.dropdown_labels.selected_value).values() if self.dropdown_labels.selected_value is not None else [None, None]
        if selected_lid is not None:
            self.input_repeating_panel.raise_event_on_children('x-create-lbl-button', selected_lid=selected_lid, selected_lname=selected_lname)
        
    def dropdown_tabs_show(self, **event_args):
        """This method is called when the DropDown is shown on the screen"""
        self.dropdown_tabs.items = anvil.server.call('generate_expensetabs_dropdown')
        self.button_delete_exptab.enabled = False if self.dropdown_tabs.selected_value in ('', None) else True

    @logger.log_function
    def dropdown_tabs_change(self, **event_args):
        """This method is called when an item is selected"""
        selected_tid = self.dropdown_tabs.selected_value[0] if self.dropdown_tabs.selected_value is not None else None
        tab_id, self.tab_name.text = anvil.server.call('get_selected_expensetab_attr', selected_tid)
        self.input_repeating_panel.items = anvil.server.call('select_transactions', selected_tid)
        if len(self.input_repeating_panel.items) < const.ExpenseConfig.DEFAULT_ROW_NUM:
            diff = const.ExpenseConfig.DEFAULT_ROW_NUM - len(self.input_repeating_panel.items)
            self.input_repeating_panel.items = self.input_repeating_panel.items + [{} for i in range(diff)]
        self.button_delete_exptab.enabled = False if self.dropdown_tabs.selected_value in ('', None) else True
        cache.deleted_row_reset()

    def cb_hide_remarks_change(self, **event_args):
        """This method is called when this checkbox is checked or unchecked"""
        if self.cb_hide_remarks.checked:
            column = [c for c in self.data_grid_1.columns if c['data_key'] == exptbl.Remarks][0]
            self.hidden_data_grid.columns.append(column)
            self.data_grid_1.columns.remove(column)
            self.data_grid_1.columns = self.data_grid_1.columns
        else:
            pos = 0
            for c in self.data_grid_1.columns:
                if c['data_key'] is not exptbl.Amount:
                    pos = pos + 1
                else:
                    break
            first_half_col = self.data_grid_1.columns[:pos+1]
            second_half_col = self.data_grid_1.columns[pos+1:]
            column = [c for c in self.hidden_data_grid.columns if c['data_key'] == exptbl.Remarks][0]
            self.data_grid_1.columns = first_half_col + [column] + second_half_col
        self.input_repeating_panel.raise_event_on_children('x-set-remarks-visible', vis=not self.cb_hide_remarks.checked)

    def cb_hide_stmtdtl_change(self, **event_args):
        """This method is called when this checkbox is checked or unchecked"""
        if self.cb_hide_stmtdtl.checked:
            logger.debug("self.data_grid_1.columns=", self.data_grid_1.columns)
            column = [c for c in self.data_grid_1.columns if c['data_key'] == exptbl.StmtDtl][0]
            self.hidden_data_grid.columns.append(column)
            self.data_grid_1.columns.remove(column)
            self.data_grid_1.columns = self.data_grid_1.columns
        else:
            pos = 0
            for c in self.data_grid_1.columns:
                if c['data_key'] is not exptbl.Amount:
                    pos = pos + 1
                else:
                    break
            first_half_col = self.data_grid_1.columns[:pos+2] if self.data_grid_1.columns[pos+1]['data_key'] == exptbl.Remarks else self.data_grid_1.columns[:pos+1] 
            second_half_col = self.data_grid_1.columns[pos+2:] if self.data_grid_1.columns[pos+1]['data_key'] == exptbl.Remarks else self.data_grid_1.columns[pos+1:]
            column = [c for c in self.hidden_data_grid.columns if c['data_key'] == exptbl.StmtDtl][0]
            self.data_grid_1.columns = first_half_col + [column] + second_half_col
        self.input_repeating_panel.raise_event_on_children('x-set-stmt-dtl-visible', vis=not self.cb_hide_stmtdtl.checked)

    @logger.log_function
    def button_save_click(self, **event_args):
        """Validation"""
        result = all(c._validate() for c in self.input_repeating_panel.get_components())
        if result is not True:
            return

        """This method is called when the button is clicked"""
        # Reload to allow changed rows (deleted, added or updated) to reflect properly
        self.reload_rp_data()
        tab_name = self.tab_name.text
        tab_id = self.dropdown_tabs.selected_value[0] if self.dropdown_tabs.selected_value is not None else None
        tab_id = anvil.server.call('save_expensetab', id=tab_id, name=tab_name)
        if tab_id is None or tab_id <= 0:
            msg = f"ERROR: Fail to save expense tab {tab_name}."
            logger.error(msg)
            Notification(msg).show()
            return

        """ Reflect the change in template dropdown """
        self.dropdown_tabs.items = anvil.server.call('generate_expensetabs_dropdown')
        self.dropdown_tabs.selected_value = [tab_id, tab_name]
        # """ Add/Update """
        result_u = anvil.server.call('upsert_transactions', tab_id, self.input_repeating_panel.items)
        # """ Delete """
        result_d = anvil.server.call('delete_transactions', tab_id, cache.get_deleted_row())

        if result_d is not None and result_u is not None:
            cache.deleted_row_reset()
            self._switch_to_submit_button()
            self._replace_iid(result_u)
            msg2 = f"Expense tab {tab_name} has been saved successfully."
            logger.info(msg2)
        else:
            if result_d is not None:
                cache.deleted_row_reset()
                msg2 = f"WARNING: Expense tab {tab_name} has been saved and transactions are deleted successfully, but technical problem occurs in update, please try again."
            elif result_u is not None:
                msg2 = f"WARNING: Expense tab {tab_name} has been saved and transactions are updated successfully, but technical problem occurs in deletion, please try again."
            else:
                msg2 = f"WARNING: Expense tab {tab_name} has been saved but technical problem occurs in saving transactions. Please try again."
            logger.warning(msg2)
        Notification(msg2).show()

    @logger.log_function
    def button_submit_click(self, **event_args):
        """This method is called when the button is clicked"""
        tab_name = self.tab_name.text
        tab_id = self.dropdown_tabs.selected_value[0] if self.dropdown_tabs.selected_value is not None else None
        result = anvil.server.call('submit_expensetab', tab_id, True)

        if result is not None and result > 0:
            """ Reflect the change in template dropdown """
            self.dropdown_tabs.items = anvil.server.call('generate_expensetabs_dropdown')
            self.dropdown_tabs.raise_event('change')
            msg = f"Expense tab {tab_name} has been submitted."
            logger.info(msg)
        else:
            msg = f"ERROR: Fail to submit expense tab {tab_name}."
            logger.error(msg)
        Notification(msg).show()

    @logger.log_function
    def button_delete_click(self, **event_args):
        """This method is called when the button is clicked"""
        to_be_del_tab_id = self.dropdown_tabs.selected_value[0] if self.dropdown_tabs.selected_value is not None else None
        to_be_del_tab_name = self.dropdown_tabs.selected_value[1] if self.dropdown_tabs.selected_value is not None else None
        msg = Label(text=f"Proceed expense tab <{to_be_del_tab_name}> deletion by clicking DELETE.")
        userconf = alert(content=msg, title="Confirm Expense Tab Deletion", buttons=[("DELETE", const.Alerts.CONFIRM), ("CANCEL", const.Alerts.CANCEL)])

        if userconf == const.Alerts.CONFIRM:
            result = anvil.server.call('delete_expensetab', tab_id=to_be_del_tab_id)
            if result is not None and result > 0:
                """ Reflect the change in tab dropdown """
                self.dropdown_tabs_show()
                self.dropdown_tabs.raise_event('change')
                cache.deleted_row_reset()
                msg2 = f"Expense tab {to_be_del_tab_name} has been deleted."
                logger.info(msg2)
            else:
                msg2 = f"ERROR: Fail to delete expense tab {to_be_del_tab_name}."
                logger.error(msg2)
            Notification(msg2).show()

    def tab_name_change(self, **event_args):
        """This method is called when the text in this text box is edited"""
        self._switch_to_save_button()

    def reload_rp_data(self, **event_args):
        for d in self.input_repeating_panel.get_components(): logger.trace("reload_rp_data d.item=", d.item)
        self.input_repeating_panel.items = [c.item for c in self.input_repeating_panel.get_components() if c.item.get('iid', None) not in cache.get_deleted_row()]

    def _replace_iid(self, iid, **event_args):
        DL = {k: [dic[k] for dic in self.input_repeating_panel.items] for k in self.input_repeating_panel.items[0]}
        DL['iid'] = iid
        self.input_repeating_panel.items = [dict(zip(DL, col)) for col in zip(*DL.values())]