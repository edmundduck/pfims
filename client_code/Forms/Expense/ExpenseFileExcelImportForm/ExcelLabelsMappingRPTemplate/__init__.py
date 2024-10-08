from ._anvil_designer import ExcelLabelsMappingRPTemplateTemplate
from anvil import *
import anvil.server
from .....Controllers import ExpenseFileExcelImportController
from .....Utils.Logger import ClientLogger

logger = ClientLogger()

class ExcelLabelsMappingRPTemplate(ExcelLabelsMappingRPTemplateTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        # Any code you write here will run before the form opens.
        self.dropdown_lbl_action.items = ExpenseFileExcelImportController.generate_labels_mapping_action_dropdown()
        self.dropdown_lbl_map_to.items, self.dropdown2_lbl_map_to.items, self.dropdown3_lbl_map_to.items, self.dropdown4_lbl_map_to.items = [ExpenseFileExcelImportController.generate_labels_dropdown()] * 4
        self.dropdown_lbl_map_to.visible, self.dropdown2_lbl_map_to.visible, self.dropdown3_lbl_map_to.visible, self.dropdown4_lbl_map_to.visible = [False] * 4
        self.dropdown2_lbl_map_to.selected_value, self.dropdown3_lbl_map_to.selected_value, self.dropdown4_lbl_map_to.selected_value = [None] * 3
        self.hidden_lbl_action.text = None
        self.input_label.visible = False

        # Prefill "labels map to" dropdown by finding high proximity choices
        self.dropdown_lbl_map_to.selected_value = ExpenseFileExcelImportController.get_label_dropdown_selected_item(self.item['tgtlbl'] if self.item['tgtlbl'] is not None else None)
        self.add_event_handler('x-apply-action-to-all-labels', self.apply_action_to_all_labels)

    def form_show(self, **event_args):
        """This method is called when the form is shown on the page"""
        # self.parent = RepearingPanel / .parent = DataGrid / .parent = FlowPanel / .parent = Form
        self.parent.parent.parent.parent.raise_event('x-row-show')

    @logger.log_function
    def dropdown_lbl_action_change(self, **event_args):
        """This method is called when an item is selected"""
        from .....Utils.Constants import FileImportLabelMappingExtraAction
        
        action, _ = self.dropdown_lbl_action.selected_value if self.dropdown_lbl_action.selected_value is not None else [None, None]
        self.dropdown_lbl_map_to.visible = ExpenseFileExcelImportController.visible_account_label_map_to_dropdown(self.dropdown_lbl_action.selected_value)
        self.dropdown2_lbl_map_to.visible = self.dropdown_lbl_map_to.visible and ExpenseFileExcelImportController.visible_account_label_map_to_extra_dropdown(self.dropdown_lbl_map_to.selected_value)
        self.dropdown3_lbl_map_to.visible = self.dropdown_lbl_map_to.visible and ExpenseFileExcelImportController.visible_account_label_map_to_extra_dropdown(self.dropdown2_lbl_map_to.selected_value)
        self.dropdown4_lbl_map_to.visible = self.dropdown_lbl_map_to.visible and ExpenseFileExcelImportController.visible_account_label_map_to_extra_dropdown(self.dropdown3_lbl_map_to.selected_value)
        self.input_label.visible = ExpenseFileExcelImportController.visible_account_label_textfield(self.dropdown_lbl_action.selected_value)
        prev = self.hidden_lbl_action.text
        self.hidden_lbl_action.text = action
        self.parent.raise_event('x-handle-action-count', action=action, prev=prev)

    def apply_action_to_all_labels(self, action, **event_args):
        self.dropdown_lbl_action.selected_value = ExpenseFileExcelImportController.get_labels_mapping_action_dropdown_selected_item(action)
        self.item['action'] = ExpenseFileExcelImportController.get_labels_mapping_action_dropdown_selected_item(action)
        self.dropdown_lbl_action_change()

    def dropdown_lbl_map_to_change(self, **event_args):
        """This method is called when an item is selected"""
        self.dropdown2_lbl_map_to.visible = ExpenseFileExcelImportController.visible_account_label_map_to_extra_dropdown(self.dropdown_lbl_map_to.selected_value)
        if not self.dropdown_lbl_map_to.selected_value:
            self.dropdown3_lbl_map_to.visible, self.dropdown4_lbl_map_to.visible = [self.dropdown2_lbl_map_to.visible] * 2
            self.item['tgtlbl2'], self.item['tgtlbl3'], self.item['tgtlbl4'] = [None] * 3
            self.refresh_data_bindings()

    def dropdown2_lbl_map_to_change(self, **event_args):
        """This method is called when an item is selected"""
        self.dropdown3_lbl_map_to.visible = ExpenseFileExcelImportController.visible_account_label_map_to_extra_dropdown(self.dropdown2_lbl_map_to.selected_value)
        if not self.dropdown2_lbl_map_to.selected_value:
            self.dropdown4_lbl_map_to.visible = self.dropdown3_lbl_map_to.visible
            self.item['tgtlbl3'], self.item['tgtlbl4'] = [None] * 2
            self.refresh_data_bindings()
 
    def dropdown3_lbl_map_to_change(self, **event_args):
        """This method is called when an item is selected"""
        self.dropdown4_lbl_map_to.visible = ExpenseFileExcelImportController.visible_account_label_map_to_extra_dropdown(self.dropdown3_lbl_map_to.selected_value)
        if not self.dropdown3_lbl_map_to.selected_value: 
            self.item['tgtlbl4'] = None
            # Refresh data binding instead of manually set selected_value as None to keep the code clean
            # self.dropdown4_lbl_map_to.selected_value = None
            self.refresh_data_bindings()
