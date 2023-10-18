from ._anvil_designer import ExpenseInputFormTemplate
from anvil import *
import anvil.server
from datetime import date
from ....Controllers import ExpenseInputController
from ....Utils import Constants as const
from ....Utils.ButtonModerator import ButtonModerator
from ....Utils.ClientCache import ClientCache
from ....Utils.Constants import ExpenseDBTableDefinion as exptbl
from ....Utils.Logger import ClientLogger
from .ExpenseInputRPTemplate import ExpenseInputRPTemplate as expintmpl

logger = ClientLogger()
btnmod = ButtonModerator()

class ExpenseInputForm(ExpenseInputFormTemplate):
    def __init__(self, tab_id=None, data=None, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        # Any code you write here will run when the form opens.
        self.dropdown_labels.items = ExpenseInputController.generate_labels_dropdown()
        self.dropdown_tabs.items = ExpenseInputController.generate_expense_tabs_dropdown()
        self.button_delete_exptab.enabled = ExpenseInputController.enable_expense_group_delete_button(self.dropdown_tabs.selected_value)
        self.button_add_rows.text = self.button_add_rows.text.replace('%n', str(const.ExpenseConfig.DEFAULT_ROW_NUM))
        self.input_repeating_panel.add_event_handler('x-switch-to-save-button', self._switch_to_save_button)
        self.input_repeating_panel.add_event_handler('x-deleted-row', self._deleted_iid_row_active)

        if tab_id is not None:
            self.dropdown_tabs.selected_value = tab_id
            self.tab_name.text = tab_id[1]
            logger.debug("self.dropdown_tabs.selected_value=", self.dropdown_tabs.selected_value)

        self.input_repeating_panel.items = ExpenseInputController.populate_repeating_panel_items(data)
        self._deleted_iid_row_reset()
        cache_del_iid = ClientCache(const.CacheKey.EXP_INPUT_DEL_IID, [])
        cache_del_iid.clear_cache()

    def _switch_to_submit_button(self, **event_args):
        """
        Change the save button to submit.
        """
        self.button_save_exptab.text = const.ExpenseConfig.BUTTON_SUBMIT_TEXT
        self.button_save_exptab.background = const.ColorSchemes.THEME_PRIM
        self.button_save_exptab.remove_event_handler('click')
        self.button_save_exptab.add_event_handler('click', self.button_submit_click)

    def _switch_to_save_button(self, **event_args):
        """
        Change the submit button to save.
        """
        self.button_save_exptab.text = const.ExpenseConfig.BUTTON_DRAFT_TEXT
        self.button_save_exptab.background = const.ColorSchemes.THEME_SEC
        self.button_save_exptab.remove_event_handler('click')
        self.button_save_exptab.add_event_handler('click', self.button_save_click)
        
    def button_file_import_click(self, **event_args):
        """This method is called when the button is clicked"""
        from ....Utils import Routing
        Routing.open_exp_file_upload_form(self)
        
    def button_add_rows_click(self, **event_args):
        """This method is called when the button is clicked"""
        self.button_add_rows.enabled = False
        if self.tag['reload']:
            # TODO - Integrate reload flag into populate_repeating_panel_items
            self.input_repeating_panel.items = ExpenseInputController.populate_repeating_panel_items(self.input_repeating_panel.items)
            self.tag['reload'] = False
        else:
            self.input_repeating_panel.items = ExpenseInputController.populate_repeating_panel_items() + self.input_repeating_panel.items
        self.button_add_rows.enabled = True

    def button_lbl_maint_click(self, **event_args):
        """This method is called when the button is clicked"""
        from ....Utils import Routing
        Routing.open_lbl_maint_form(self)

    def button_acct_maint_click(self, **event_args):
        """This method is called when the button is clicked"""
        from ....Utils import Routing
        Routing.open_acct_maint_form(self)

    @logger.log_function
    def dropdown_labels_change(self, **event_args):
        """This method is called when an item is selected"""
        selected_lid, selected_lname = self.dropdown_labels.selected_value if self.dropdown_labels.selected_value is not None else [None, None]
        if selected_lid is not None:
            self.input_repeating_panel.raise_event_on_children('x-create-lbl-button', selected_lid=selected_lid, selected_lname=selected_lname)
        
    @logger.log_function
    def dropdown_tabs_change(self, **event_args):
        """This method is called when an item is selected"""
        cache_del_iid = ClientCache(const.CacheKey.EXP_INPUT_DEL_IID, [])
        selected_tid = self.dropdown_tabs.selected_value[0] if self.dropdown_tabs.selected_value is not None else None
        tab_id, self.tab_name.text, self.input_repeating_panel.items = anvil.server.call('proc_exp_tab_change', selected_tid)
        self.input_repeating_panel.items = ExpenseInputController.populate_repeating_panel_items(self.input_repeating_panel.items)
        self.button_delete_exptab.enabled = ExpenseInputController.enable_expense_group_delete_button(self.dropdown_tabs.selected_value)
        self._deleted_iid_row_reset()
        cache_del_iid.clear_cache()

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

    @btnmod.one_click_only
    @logger.log_function
    def button_save_click(self, **event_args):
        """Validation"""
        result = all(c._validate() for c in self.input_repeating_panel.get_components())
        if result is not True:
            return

        """This method is called when the button is clicked"""
        self.input_repeating_panel.items = ExpenseInputController.populate_repeating_panel_items(self.input_repeating_panel.items)
        tab_name = self.tab_name.text
        tab_id, tab_original_name = self.dropdown_tabs.selected_value if self.dropdown_tabs.selected_value is not None else [None, None]
        cache_del_iid = ClientCache(const.CacheKey.EXP_INPUT_DEL_IID, [])
        try:
            tab_id, result_u, result_d = anvil.server.call('proc_save_exp_tab', tab_id, tab_name, self.input_repeating_panel.items, cache_del_iid.get_cache())
            if tab_name != tab_original_name or tab_id is None:
                # Only trigger expense tab dropdown refresh when new tab is created or tab name is changed
                self.dropdown_tabs.items = ExpenseInputController.generate_expense_tabs_dropdown(reload=True)
                self.dropdown_tabs.selected_value = [tab_id, tab_name]
            if result_u is None and result_d is None:
                msg = f"WARNING: Expense tab {tab_name} has been saved but technical problem occurs in saving transactions. Please try again."
                logger.warning(msg)
            elif result_u is None:
                self._deleted_iid_row_reset()
                cache_del_iid.clear_cache()
                msg = f"WARNING: Expense tab {tab_name} has been saved and transactions are deleted successfully, but technical problem occurs in update, please try again."
                logger.warning(msg)
            elif result_d is None:
                self.input_repeating_panel.items = ExpenseInputController.replace_repeating_panel_iid(result_u)
                msg = f"WARNING: Expense tab {tab_name} has been saved and transactions are updated successfully, but technical problem occurs in deletion, please try again."
                logger.warning(msg)
            else:
                self._deleted_iid_row_reset()
                cache_del_iid.clear_cache()
                self.input_repeating_panel.items = ExpenseInputController.replace_repeating_panel_iid(result_u)
                self._switch_to_submit_button()
                msg = f"Expense tab {tab_name} has been saved successfully."
                logger.info(msg)
            logger.debug(f"Tab ID={tab_id}, IID list={result_u}, Deleted count={result_d}")
            Notification(msg).show()
        except Exception as err:
            logger.error(err)
            Notification(err).show()

    @btnmod.one_click_only
    @logger.log_function
    def button_submit_click(self, **event_args):
        """This method is called when the button is clicked"""
        tab_name = self.tab_name.text
        tab_id = self.dropdown_tabs.selected_value[0] if self.dropdown_tabs.selected_value is not None else None
        result = anvil.server.call('submit_expensetab', tab_id, True)

        if result is not None and result > 0:
            """ Reflect the change in template dropdown """
            self.dropdown_tabs.items = ExpenseInputController.generate_expense_tabs_dropdown(reload=True)
            self.dropdown_tabs.selected_value = None
            tab_id, self.tab_name.text, self.input_repeating_panel.items = [None, None, ExpenseInputController.populate_repeating_panel_items()]
            self.button_delete_exptab.enabled = False
            msg = f"Expense tab {tab_name} has been submitted."
            logger.info(msg)
        else:
            msg = f"ERROR: Fail to submit expense tab {tab_name}."
            logger.error(msg)
        Notification(msg).show()

    @btnmod.one_click_only
    @logger.log_function
    def button_delete_click(self, **event_args):
        """This method is called when the button is clicked"""
        to_be_del_tab_id, to_be_del_tab_name = self.dropdown_tabs.selected_value if self.dropdown_tabs.selected_value is not None else [None, None]
        msg = Label(text=f"Proceed expense tab <{to_be_del_tab_name}> deletion by clicking DELETE.")
        userconf = alert(content=msg, title="Confirm Expense Tab Deletion", buttons=[("DELETE", const.Alerts.CONFIRM), ("CANCEL", const.Alerts.CANCEL)])

        if userconf == const.Alerts.CONFIRM:
            result = anvil.server.call('delete_expensetab', tab_id=to_be_del_tab_id)
            if result is not None and result > 0:
                """ Reflect the change in tab dropdown """
                cache_del_iid = ClientCache(const.CacheKey.EXP_INPUT_DEL_IID, [])
                self.dropdown_tabs.items = ExpenseInputController.generate_expense_tabs_dropdown(reload=True)
                self.dropdown_tabs.selected_value = None
                tab_id, self.tab_name.text, self.input_repeating_panel.items = [None, None, ExpenseInputController.populate_repeating_panel_items()]
                self._deleted_iid_row_reset()
                cache_del_iid.clear_cache()
                msg2 = f"Expense tab {to_be_del_tab_name} has been deleted."
                logger.info(msg2)
                Notification(msg2).show()
                return btnmod.override_end_state(False)
            else:
                msg2 = f"ERROR: Fail to delete expense tab {to_be_del_tab_name}."
                logger.error(msg2)
                Notification(msg2).show()

    def tab_name_change(self, **event_args):
        """This method is called when the text in this text box is edited"""
        self._switch_to_save_button()

    @logger.log_function
    def reload_rp_data(self, extra=[], **event_args):
        """
        Reload the repeating panel to allow changed rows (deleted, added or updated) to reflect properly.

        Parameters:
            extra (list): Extra list to add to resultant repeating panel.
        """
        def filter_valid_rows(row):
            cache_del_iid = ClientCache(const.CacheKey.EXP_INPUT_DEL_IID, [])
            if row.get('iid', None) and row.get('iid') in cache_del_iid.get_cache():
                # Filter out all rows in deleted IID cache
                return False
            if all(v is None for v in row.values()):
                # Filter out all None rows
                return False
            return True
        self.input_repeating_panel.items = extra + list(filter(filter_valid_rows, self.input_repeating_panel.items))

    def _deleted_iid_row_active(self, **event_args):
        """
        Mark reload tag as True as row with IID has been deleted, reload repeating panel is required.
        """
        self.tag = {'reload': True}

    def _deleted_iid_row_reset(self, **event_args):
        """
        Reset reload tag (i.e. False) as not required to reload repeating panel.

        Scenario 1 - Repeating panel reload has already been completed.
        Scenario 2 - Page/Tab has just been loaded or refreshed.
        """
        self.tag = {'reload': False}
