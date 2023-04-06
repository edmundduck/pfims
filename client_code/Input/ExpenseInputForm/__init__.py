from ._anvil_designer import ExpenseInputFormTemplate
from anvil import *
import anvil.users
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from datetime import date
from ... import Global as glo
from ... import Routing
from ...Validation import Validator

class ExpenseInputForm(ExpenseInputFormTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        # Any code you write here will run when the form opens.
        #self.input_repeating_panel.add_event_handler('x-save-change', self.save_row_change)
        #self.input_repeating_panel.add_event_handler('x-disable-submit-button', self.disable_submit_button)

        # Initiate repeating panel items to an empty list otherwise will throw NoneType error
        self.input_repeating_panel.items = []
        #self.input_selldate.date = date.today()
        #self.templ_name.text, self.dropdown_broker.selected_value = anvil.server.call('get_selected_template_attr', self.dropdown_templ.selected_value)

        # Reset on screen change status
        #glo.reset_input_stock_change()
        #self.disable_submit_button()

    def save_row_change(self, **event_args):
        """
        *** ESSENTIAL ***
        Update child items from repeating panel to parent form items
        Refer to the following reference links for detail
        https://anvil.works/forum/t/is-it-possible-to-access-a-repeating-panels-methods-from-the-parent-form/3028/2
        https://anvil.works/forum/t/refresh-data-bindings-when-any-key-in-self-items-changes/1141/3
        https://anvil.works/forum/t/repeating-panel-to-collect-new-information/356/3
        """
        # TODO - Improve the update change logic so that don't have to go through whole list everytime
        self.input_repeating_panel.items = [c.input_data_panel_readonly.item \
                                            for c in self.input_repeating_panel.get_components()]

    def _getall_selected_labels(self):
        label_list = []
        for i in self.panel_labels.get_components():
            if isinstance(i, Button):
                if i.icon == 'fa:minus':
                    label_list += [i.tag]
        return label_list

    def button_plus_click(self, **event_args):
        """This method is called when the button is clicked"""
        v = Validator()
        v.display_when_invalid(self.valerror_title)
        v.require_date_field(self.input_date, self.valerror_1, True)
        v.require_selected(self.dropdown_acct, self.valerror_2, True)
        v.require_text_field(self.input_amt, self.valerror_3, True)

        print(self.input_date.date, self.dropdown_acct.selected_value, self.input_amt.text, self.input_remarks.text, \
              self.input_stmt_dtl.text, self.panel_labels)

        new_data = {"date": self.input_date.date,
                    "acct": self.dropdown_acct.selected_value,
                    "amt": self.input_amt.text,
                    "remarks": self.input_remarks.text,
                    "stmt_dtl": self.input_stmt_dtl.text,
                    "labels": self._getall_selected_labels(),
                    "iid": None}

        self.input_repeating_panel.items = self.input_repeating_panel.items + [new_data]
        #glo.track_input_stock_journals_change()
        #self.disable_submit_button()

    def button_erase_click(self, **event_args):
        """This method is called when the button is clicked"""
        self.input_date.date = ""
        self.dropdown_acct.selected_value = None
        self.input_amt.text = ""
        self.input_remarks.text = ""
        self.input_stmt_dtl.text = ""
        self.panel_labels.clear()
        """ Reset row delete flag """
        #glo.reset_deleted_row()

    def button_delete_click(self, **event_args):
        """This method is called when the button is clicked"""
        to_be_del_templ_name = self.dropdown_templ.selected_value
        msg = Label(text="Proceed template <{templ_name}> deletion by clicking DELETE.".format(templ_name=to_be_del_templ_name))
        userconf = alert(content=msg,
                        title=f"Alert - Template Deletion",
                        buttons=[
                        ("DELETE", "Y"),
                        ("CANCEL", "N")
                        ])

        if userconf == "Y":
            templ_id = anvil.server.call('get_template_id', to_be_del_templ_name)
            result = anvil.server.call('delete_templates', template_id=templ_id)
            if result is not None and result > 0:
                """ Reset row delete flag """
                glo.reset_deleted_row()

                """ Reflect the change in template dropdown """
                self.dropdown_templ_show()
                self.dropdown_broker_show()
                self.input_repeating_panel.items = []

                n = Notification("Template {templ_name} has been deleted.".format(templ_name=to_be_del_templ_name))
                n.show()
            else:
                n = Notification("ERROR: Fail to delete template {templ_name}.".format(templ_name=to_be_del_templ_name))
                n.show()

    def button_submit_click(self, **event_args):
        """This method is called when the button is clicked"""
        # to_be_submitted_templ_name = self.dropdown_templ.selected_value
        # templ_id = anvil.server.call('get_template_id', to_be_submitted_templ_name)
        # templ_name = self.templ_name.text
        # broker_id = self.dropdown_broker.selected_value
        # result = anvil.server.call('submit_templates', templ_id, True)

        # if result is not None and result > 0:
        #     """ Reflect the change in template dropdown """
        #     self.dropdown_templ.items = anvil.server.call('generate_template_dropdown')
        #     self.dropdown_templ.raise_event('change')

        #     n = Notification("Template {templ_name} has been submitted.\n It can be viewed in the transaction list report only.".format(templ_name=to_be_submitted_templ_name))
        #     n.show()
        # else:
        #     n = Notification("ERROR: Fail to submit template {templ_name}.".format(templ_name=to_be_submitted_templ_name))
        #     n.show()
        pass

    def templ_name_change(self, **event_args):
        """This method is called when the text in this text box is edited"""
        # glo.track_input_stock_template_change()
        # self.disable_submit_button()
        pass

    def disable_submit_button(self, **event_args):
        # self.button_submit.enabled = False
        pass

    def button_lbl_maint_click(self, **event_args):
        """This method is called when the button is clicked"""
        Routing.open_lbl_maint_form(self)

    def button_acct_maint_click(self, **event_args):
        """This method is called when the button is clicked"""
        Routing.open_acct_maint_form(self)

    def dropdown_labels_show(self, **event_args):
        """This method is called when the DropDown is shown on the screen"""
        self.dropdown_labels.items = anvil.server.call('generate_labels_dropdown')

    def dropdown_labels_change(self, **event_args):
        """This method is called when an item is selected"""
        # TODO
        b = Button(text=self.dropdown_labels.selected_value[1],
                   icon='fa:minus',
                   foreground="White",
                   background="Blue",
                   font_size=8,
                   align="left",
                   tag=self.dropdown_labels.selected_value[0]
                  )
        if self.cb_datarow.checked is True:
            self.panel_labels.add_component(b, False, name=self.dropdown_labels.selected_value[0])
            b.set_event_handler('click', self.label_button_minus_click)
        for i in self.input_repeating_panel.get_components():
            if isinstance(i, CheckBox):
                print(i.name)

    def label_button_minus_click(self, **event_args):
        b = event_args['sender']
        print(b.text)
        print(b.id)
        b.remove_from_parent()

    def dropdown_acct_show(self, **event_args):
        """This method is called when the DropDown is shown on the screen"""
        self.dropdown_acct.items = anvil.server.call('generate_accounts_dropdown')

    def dropdown_tabs_show(self, **event_args):
        """This method is called when the DropDown is shown on the screen"""
        self.dropdown_tabs.items = anvil.server.call('generate_expensetabs_dropdown')

    def dropdown_tabs_change(self, **event_args):
        """This method is called when an item is selected"""
        tab_id, self.tab_name.text = anvil.server.call('get_selected_expensetab_attr', self.dropdown_tabs.selected_value['tab_id'])
        # self.input_repeating_panel.items = anvil.server.call('select_template_journals', self.dropdown_tabs.selected_value['tab_id'])
        # # Reset on screen change status
        # glo.reset_input_stock_change()
        # if self.dropdown_templ.selected_value != glo.input_stock_default_templ_dropdown():
        #     self.button_submit.enabled = True

    def cb_hide_remarks_change(self, **event_args):
        """This method is called when this checkbox is checked or unchecked"""
        if self.cb_hide_remarks.checked:
            column = [c for c in self.data_grid_1.columns if c['data_key'] == 'remarks'][0]
            self.hidden_data_grid.columns.append(column)
            self.data_grid_1.columns.remove(column)
            self.data_grid_1.columns = self.data_grid_1.columns
        else:
            # TODO - partial hardcoded column definition, need to cater if the col definition is changed in design
            first_half_col = self.data_grid_1.columns[:3]
            second_half_col = self.data_grid_1.columns[3:]
            column = [c for c in self.hidden_data_grid.columns if c['data_key'] == 'remarks'][0]
            self.data_grid_1.columns = first_half_col + [column] + second_half_col

    def cb_hide_stmtdtl_change(self, **event_args):
        """This method is called when this checkbox is checked or unchecked"""
        if self.cb_hide_stmtdtl.checked:
            column = [c for c in self.data_grid_1.columns if c['data_key'] == 'stmt_dtl'][0]
            self.hidden_data_grid.columns.append(column)
            self.data_grid_1.columns.remove(column)
            self.data_grid_1.columns = self.data_grid_1.columns
        else:
            # TODO - partial hardcoded column definition, need to cater if the col definition is changed in design
            first_half_col = self.data_grid_1.columns[:4] if self.data_grid_1.columns[3]['data_key'] == 'remarks' else self.data_grid_1.columns[:3] 
            second_half_col = self.data_grid_1.columns[4:] if self.data_grid_1.columns[3]['data_key'] == 'remarks' else self.data_grid_1.columns[3:]
            column = [c for c in self.hidden_data_grid.columns if c['data_key'] == 'stmt_dtl'][0]
            self.data_grid_1.columns = first_half_col + [column] + second_half_col

    def button_save_click(self, **event_args):
        """This method is called when the button is clicked"""
        tab_id = anvil.server.call('save_expensetab',
                                   id=self.dropdown_tabs.selected_value,
                                   name=self.tab_name.text,
                                   )

        if tab_id is None or tab_id <= 0:
            n = Notification("ERROR: Fail to save tab {tab_name}.".format(tab_name=self.tab_name.text))
            n.show()
            return

        # """ Trigger save_row_change if del_iid is not empty """
        # if len(glo.del_iid) > 0:
        #     self.save_row_change()
        #     glo.reset_deleted_row()

        # """ Add/Update """
        result = anvil.server.call('upsert_transactions', tab_id, self.input_repeating_panel.items)

        if result is not None and result > 0:
            """ Reflect the change in template dropdown """
            self.dropdown_tabs.items = anvil.server.call('generate_expensetabs_dropdown')
            self.dropdown_tabs.selected_value = anvil.server.call('generate_template_dropdown_item', tab_id, tab_name)
            self.input_repeating_panel.items = anvil.server.call('select_template_journals', self.dropdown_templ.selected_value)
            # self.button_submit.enabled = True
            n = Notification("Tab {tab_name} has been saved successfully.".format(tab_name=tab_name))
        else:
            n = Notification("ERROR: Fail to save template {tab_name}.".format(tab_name=tab_name))
        n.show()

    def panel_labels_refreshing_data_bindings(self, **event_args):
        """This method is called when refreshing_data_bindings is called"""
        # TODO
        print('change happens')
        pass

