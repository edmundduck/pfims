from ._anvil_designer import UploadMappingRulesRPTemplateTemplate
from anvil import *
import anvil.server
from .....Controllers import UploadMappingRulesController
from .....Utils.ButtonModerator import ButtonModerator
from .....Utils.Logger import ClientLogger

logger = ClientLogger()
btnmod = ButtonModerator()

class UploadMappingRulesRPTemplate(UploadMappingRulesRPTemplateTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        # Any code you write here will run before the form opens.
        self.row_dropdown_type.items = UploadMappingRulesController.generate_file_mapping_type_dropdown()
        self.row_dropdown_datacol.items = UploadMappingRulesController.generate_expense_table_definition_dropdown()
        self.row_dropdown_extraact.items = UploadMappingRulesController.generate_import_extra_action_dropdown()
        self.row_dropdown_lbl.items = UploadMappingRulesController.generate_labels_dropdown()
        self.row_dropdown_acct.items = UploadMappingRulesController.generate_accounts_dropdown()

        # Generate all rules in a mapping
        if self.item.get('rule', None) is not None:
            result = UploadMappingRulesController._generate_all_mapping_rules(self.item['rule'])
            for r in result:
                properties_list, rule = r
                self.add_mapping_rules_criteria(properties_list, rule)

    @logger.log_function
    def row_button_add_click(self, **event_args):
        """This method is called when the button is clicked"""
        from .....Utils.Constants import UploadMappingRulesInput
        user_input = {
            UploadMappingRulesInput.EXCEL_COL: self.row_dropdown_excelcol.selected_value,
            UploadMappingRulesInput.DATA_COL: self.row_dropdown_datacol.selected_value,
            UploadMappingRulesInput.ACTION: self.row_dropdown_extraact.selected_value,
            UploadMappingRulesInput.ACCOUNT: self.row_dropdown_acct.selected_value,
            UploadMappingRulesInput.LABEL: self.row_dropdown_lbl.selected_value
        }
        # Remove the column from to be deleted list (row_hidden_del_fid) if it's updated (removed and added back)
        self.row_hidden_del_fid.text = ",".join([x for x in self.row_hidden_del_fid.text.split(",") if x != self.row_dropdown_excelcol.selected_value])
        properties_list, rule = UploadMappingRulesController.add_mapping_rules_criteria(user_input, True)
        self.add_mapping_rules_criteria(properties_list, rule)

    @logger.log_function
    def mapping_button_minus_click(self, **event_args):
        b = event_args['sender']
        logger.trace("b.parent.tag[0]=", b.parent.tag[0])
        if b.parent.tag[0] is not None and not b.parent.tag[-1]: self.row_hidden_del_fid.text = self.row_hidden_del_fid.text + f"{b.parent.tag[0]},"
        b.parent.remove_from_parent()

    @btnmod.one_click_only
    @logger.log_function
    def row_button_save_click(self, **event_args):
        """This method is called when the button is clicked"""
        rules = []
        for i in self.get_components():
            if isinstance(i, FlowPanel) and (i.tag is not None and isinstance(i.tag, list)):
                rules.append(i.tag)
                i.remove_from_parent()
        result = UploadMappingRulesController.save_mapping_rule(self.row_hidden_id.text, self.row_mapping_name.text, self.row_dropdown_type.selected_value, rules, self.row_hidden_del_fid.text)

        id = result['id']
        if id is not None and result['count'] is not None and result['dcount'] is not None:
            self.row_hidden_id.text = id
            self.row_hidden_del_fid.text = ''
            msg = f"Mapping {name} has been saved successfully."
            logger.info(msg)
        else:
            msg = f"WARNING: Problem occurs when saving mapping {name}."
            logger.warning(msg)
        # self.item = (anvil.server.call('select_mapping_rules', id))[0]
        self.item = UploadMappingRulesController.save_mapping_rule(id)
        self.row_dropdown_type.selected_value = [filetype_id, filetype]
        if self.item.get('rule', None) is not None:
            self._generate_all_mapping_rules(self.item['rule'])
        Notification(msg).show()
        self.parent.raise_event('x-reload-rp')

    @btnmod.one_click_only
    @logger.log_function
    def row_button_delete_click(self, **event_args):
        """This method is called when the button is clicked"""
        from .....Utils.Constants import Alerts
        to_be_del_id = self.row_hidden_id.text
        to_be_del_name = self.row_mapping_name.text
        confirm = Label(text=f"Proceed mapping [{to_be_del_name}] deletion by clicking PROCEED.")
        userconf = alert(content=confirm, title='Alert - Confirm to delete mapping rule', buttons=[('PROCEED', Alerts.CONFIRM), ('CANCEL', Alerts.CANCEL)])

        if userconf == Alerts.CONFIRM:
            # Save the self.parent first so that remove_from_parent can be called before raising event
            #https://anvil.works/forum/t/children-to-parent-update/6324/4
            parent = self.parent
            if to_be_del_id:
                try:
                    result = UploadMappingRulesController.delete_mapping_rule(to_be_del_id)
                except Exception as err:
                    logger.error(err)
                    msg = f"ERROR: Fail to delete mapping {to_be_del_name}."
                else:
                    self.remove_from_parent()
                    msg = f"Mapping {to_be_del_name} has been deleted."
                    logger.info(msg)
                    parent.raise_event('x-reload-rp', del_id=to_be_del_id)
                finally:
                    Notification(msg).show()
            else:
                self.remove_from_parent()
                parent.raise_event('x-reload-rp')

    def row_dropdown_extraact_show(self, **event_args):
        """This method is called when the DropDown is shown on the screen"""
        self.row_dropdown_lbl.visible = True if self.row_dropdown_extraact.selected_value is not None and self.row_dropdown_extraact.selected_value[0] == "L" else False
        self.row_dropdown_acct.visible = True if self.row_dropdown_extraact.selected_value is not None and self.row_dropdown_extraact.selected_value[0] == "A" else False

    def row_dropdown_extraact_change(self, **event_args):
        """This method is called when an item is selected"""
        self.row_dropdown_lbl.visible = True if self.row_dropdown_extraact.selected_value is not None and self.row_dropdown_extraact.selected_value[0] == "L" else False
        self.row_dropdown_acct.visible = True if self.row_dropdown_extraact.selected_value is not None and self.row_dropdown_extraact.selected_value[0] == "A" else False

    def add_mapping_rules_criteria(self, tag_value, rule, **event_args):
        from .....Utils.Constants import ColorSchemes, Icons
        lbl_obj = Label(text=rule, font_size=12, foreground='indigo', icon=Icons.BULLETPOINT)
        fp = FlowPanel(spacing_above="small", spacing_below="small", tag=tag_value)
        b = Button(
            icon=Icons.REMOVE,
            foreground=ColorSchemes.BUTTON_BG,
            font_size=12,
            align="left",
            spacing_above="small",
            spacing_below="small",
        )
        self.add_component(fp)
        fp.add_component(lbl_obj)
        fp.add_component(b)
        b.set_event_handler('click', self.mapping_button_minus_click)
