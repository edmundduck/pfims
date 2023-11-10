from ._anvil_designer import ExpenseInputFormTemplate
from anvil import *
from ....Controllers import ExpenseInputController
from ....Utils.ButtonModerator import ButtonModerator
from ....Utils.Logger import ClientLogger

logger = ClientLogger()
btnmod = ButtonModerator()

class ExpenseInputForm(ExpenseInputFormTemplate):
    def __init__(self, tab_id=None, data=None, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        # Any code you write here will run when the form opens.
        ExpenseInputController.init_cache()
        self.dropdown_labels.items = ExpenseInputController.generate_labels_dropdown()
        self.dropdown_tabs.items = ExpenseInputController.generate_expense_tabs_dropdown()
        self.button_delete_exptab.enabled = ExpenseInputController.enable_expense_group_delete_button(self.dropdown_tabs.selected_value)
        self.button_add_rows.text = ExpenseInputController.get_blank_row_button_text(self.button_add_rows.text)
        self.input_repeating_panel.add_event_handler('x-switch-to-save-button', self._switch_to_save_button)
        self.input_repeating_panel.add_event_handler('x-deleted-row', self._deleted_iid_row_active)

        if tab_id is not None:
            self.dropdown_tabs.selected_value = tab_id
            self.tab_name.text = tab_id[1]
            logger.debug("self.dropdown_tabs.selected_value=", self.dropdown_tabs.selected_value)

        self.input_repeating_panel.items = ExpenseInputController.populate_repeating_panel_items(data)
        self._deleted_iid_row_reset()

    def _switch_to_submit_button(self, **event_args):
        """
        Change the save button to submit.
        """
        from ....Utils.Constants import ExpenseConfig
        self.button_save_exptab.text = ExpenseConfig.BUTTON_SUBMIT_TEXT
        self.button_save_exptab.remove_event_handler('click')
        self.button_save_exptab.add_event_handler('click', self.button_submit_click)

    def _switch_to_save_button(self, **event_args):
        """
        Change the submit button to save.
        """
        from ....Utils.Constants import ExpenseConfig
        self.button_save_exptab.text = ExpenseConfig.BUTTON_DRAFT_TEXT
        self.button_save_exptab.remove_event_handler('click')
        self.button_save_exptab.add_event_handler('click', self.button_save_click)
        
    def button_file_import_click(self, **event_args):
        """This method is called when the button is clicked"""
        from ....Utils import Routing
        Routing.open_exp_file_upload_form(self)

    @btnmod.one_click_only
    def button_add_rows_click(self, **event_args):
        """This method is called when the button is clicked"""
        self.input_repeating_panel.items = ExpenseInputController.populate_repeating_panel_items() + ExpenseInputController.populate_repeating_panel_items(self.input_repeating_panel.items, reload=self.tag['reload'])
        self._deleted_iid_row_reset()

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
        self.tab_name.text = ExpenseInputController.get_group_name(self.dropdown_tabs.selected_value)
        self.input_repeating_panel.items = ExpenseInputController.populate_repeating_panel_items(ExpenseInputController.get_transactions(self.dropdown_tabs.selected_value))
        self.button_delete_exptab.enabled = ExpenseInputController.enable_expense_group_delete_button(self.dropdown_tabs.selected_value)
        self._deleted_iid_row_reset()

    def cb_hide_remarks_change(self, **event_args):
        """This method is called when this checkbox is checked or unchecked"""
        from ....Entities.ExpenseTransaction import ExpenseTransaction
        if self.cb_hide_remarks.checked:
            column = [c for c in self.data_grid_1.columns if c['data_key'] == ExpenseTransaction.field_remarks()][0]
            self.hidden_data_grid.columns.append(column)
            self.data_grid_1.columns.remove(column)
            self.data_grid_1.columns = self.data_grid_1.columns
        else:
            pos = 0
            for c in self.data_grid_1.columns:
                if c['data_key'] is not ExpenseTransaction.field_amount():
                    pos = pos + 1
                else:
                    break
            first_half_col = self.data_grid_1.columns[:pos+1]
            second_half_col = self.data_grid_1.columns[pos+1:]
            column = [c for c in self.hidden_data_grid.columns if c['data_key'] == ExpenseTransaction.field_remarks()][0]
            self.data_grid_1.columns = first_half_col + [column] + second_half_col
        self.input_repeating_panel.raise_event_on_children('x-set-remarks-visible', vis=not self.cb_hide_remarks.checked)

    def cb_hide_stmtdtl_change(self, **event_args):
        """This method is called when this checkbox is checked or unchecked"""
        from ....Entities.ExpenseTransaction import ExpenseTransaction
        if self.cb_hide_stmtdtl.checked:
            logger.debug("self.data_grid_1.columns=", self.data_grid_1.columns)
            column = [c for c in self.data_grid_1.columns if c['data_key'] == ExpenseTransaction.field_statement_detail()][0]
            self.hidden_data_grid.columns.append(column)
            self.data_grid_1.columns.remove(column)
            self.data_grid_1.columns = self.data_grid_1.columns
        else:
            pos = 0
            for c in self.data_grid_1.columns:
                if c['data_key'] is not ExpenseTransaction.field_amount():
                    pos = pos + 1
                else:
                    break
            first_half_col = self.data_grid_1.columns[:pos+2] if self.data_grid_1.columns[pos+1]['data_key'] == ExpenseTransaction.field_remarks() else self.data_grid_1.columns[:pos+1] 
            second_half_col = self.data_grid_1.columns[pos+2:] if self.data_grid_1.columns[pos+1]['data_key'] == ExpenseTransaction.field_remarks() else self.data_grid_1.columns[pos+1:]
            column = [c for c in self.hidden_data_grid.columns if c['data_key'] == ExpenseTransaction.field_statement_detail()][0]
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
        self.input_repeating_panel.items = ExpenseInputController.populate_repeating_panel_items(self.input_repeating_panel.items, reload=True)
        tab_original_id, tab_original_name = self.dropdown_tabs.selected_value if self.dropdown_tabs.selected_value is not None else [None, None]
        tab_name = self.tab_name.text
        try:
            tab_id, self.input_repeating_panel.items = ExpenseInputController.save_expense_transaction_group(self.dropdown_tabs.selected_value, tab_name, self.input_repeating_panel.items)
            if tab_name != tab_original_name or (not tab_original_id and tab_id):
                # Only trigger expense tab dropdown refresh when new tab is created or tab name is changed
                self.dropdown_tabs.items = ExpenseInputController.generate_expense_tabs_dropdown(reload=True)
                self.dropdown_tabs.selected_value = ExpenseInputController.get_expense_tabs_dropdown_selected_item(tab_id)
            self._deleted_iid_row_reset()
            self._switch_to_submit_button()
            msg = f"Expense transaction group [{tab_name} ({tab_id})] has been saved successfully."
            logger.info(msg)
        except Exception as err:
            logger.error(err)
            msg = Notification(f"ERROR occurs when saving expense transaction group [{tab_name} ({tab_original_id})].") if tab_original_id else \
                Notification(f"ERROR occurs when saving expense transaction group [{tab_name}].") 
        Notification(msg).show()

    @btnmod.one_click_only
    @logger.log_function
    def button_submit_click(self, **event_args):
        """This method is called when the button is clicked"""
        tab_id, tab_name = self.dropdown_tabs.selected_value if self.dropdown_tabs.selected_value is not None else [None, None]
        try:
            result = ExpenseInputController.submit_expense_transaction_group(self.dropdown_tabs.selected_value)
            """ Reflect the change in template dropdown """
            self.dropdown_tabs.items = ExpenseInputController.generate_expense_tabs_dropdown(reload=True)
            self.dropdown_tabs.selected_value = None
            self.tab_name.text = None
            self.button_delete_exptab.enabled = False
            self._deleted_iid_row_reset()
            self.input_repeating_panel.items = ExpenseInputController.populate_repeating_panel_items()
            msg = "Expense transaction group [{0} ({1})] has been submitted.".format(tab_name, tab_id)
            logger.info(msg)
        except Exception as err:
            logger.error(err)
            msg = f"ERROR occurs when submitting expense transaction group [{tab_name} ({tab_id})]."
        Notification(msg).show()

    @btnmod.one_click_only
    @logger.log_function
    def button_delete_click(self, **event_args):
        """This method is called when the button is clicked"""
        from ....Utils.Constants import Alerts
        exp_grp_id, exp_grp_name = self.dropdown_tabs.selected_value if self.dropdown_tabs.selected_value is not None else [None, None]
        confirm = Label(text=f"Proceed expense transaction group [{exp_grp_name} ({exp_grp_id})] deletion by clicking PROCEED.")
        userconf = alert(content=confirm, title='Alert - Confirm to delete expense transaction group', buttons=[('PROCEED', Alerts.CONFIRM), ('CANCEL', Alerts.CANCEL)])

        if userconf == Alerts.CONFIRM:
            try:
                result = ExpenseInputController.delete_expense_transaction_group(self.dropdown_tabs.selected_value)
                """ Reflect the change in tab dropdown """
                self.dropdown_tabs.items = ExpenseInputController.generate_expense_tabs_dropdown(reload=True)
                self.dropdown_tabs.selected_value = None
                self.tab_name.text = None
                self.button_delete_exptab.enabled = False
                self._deleted_iid_row_reset()
                self.input_repeating_panel.items = ExpenseInputController.populate_repeating_panel_items()
                msg = f"Expense tab [{exp_grp_name} ({exp_grp_id})] has been deleted."
                logger.info(msg)
                Notification(msg).show()
                return btnmod.override_end_state(False)
            except Exception as err:
                logger.error(err)
                msg = f"ERROR occurs when deleting expense transaction group [{exp_grp_name} ({exp_grp_id})]."
                Notification(msg).show()

    def tab_name_change(self, **event_args):
        """This method is called when the text in this text box is edited"""
        self._switch_to_save_button()

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
