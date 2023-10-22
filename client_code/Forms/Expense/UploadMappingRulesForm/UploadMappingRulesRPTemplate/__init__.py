from ._anvil_designer import UploadMappingRulesRPTemplateTemplate
from anvil import *
import anvil.server
from ....Controllers import UploadMappingRulesController
from ....Utils import Constants as const
from ....Utils.ButtonModerator import ButtonModerator
from ....Utils.ClientCache import ClientCache
from ....Utils.Logger import ClientLogger

logger = ClientLogger()
btnmod = ButtonModerator()

class UploadMappingRulesRPTemplate(UploadMappingRulesRPTemplateTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        # Any code you write here will run before the form opens.
        cache_exp_tbl_def = ClientCache('generate_expense_tbl_def_dropdown')
        cache_filetype = ClientCache('generate_mapping_type_dropdown')
        cache_extraaction = ClientCache('generate_upload_action_dropdown')
        self.row_dropdown_type.items = cache_filetype.get_cache()
        self.row_dropdown_datacol.items = cache_exp_tbl_def.get_cache()
        self.row_dropdown_extraact.items = cache_extraaction.get_cache()
        self.row_dropdown_lbl.items = UploadMappingRulesController.generate_labels_dropdown()
        self.row_dropdown_acct.items = UploadMappingRulesController.generate_accounts_dropdown()

        # Generate all rules in a mapping
        if self.item.get('rule', None) is not None:
            self._generate_all_mapping_rules(self.item['rule'])

    @logger.log_function
    def row_button_add_click(self, **event_args):
        """This method is called when the button is clicked"""
        excelcol = self.row_dropdown_excelcol.selected_value
        # Remove the column from to be deleted list (row_hidden_del_fid) if it's updated (removed and added back)
        self.row_hidden_del_fid.text = ",".join([x for x in self.row_hidden_del_fid.text.split(",") if x != excelcol])
        datacol_id, datacol = self.row_dropdown_datacol.selected_value if self.row_dropdown_datacol.selected_value is not None else [None, None]
        extraact_id, extraact = self.row_dropdown_extraact.selected_value if self.row_dropdown_extraact.selected_value is not None else [None, None]
        lbl_id, lbl = self.row_dropdown_lbl.selected_value if self.row_dropdown_lbl.selected_value is not None else [None, None]
        acct_id, acct = self.row_dropdown_acct.selected_value if self.row_dropdown_acct.selected_value is not None else [None, None]
        extratgt_id = lbl_id if extraact_id == "L" else acct_id
        self._generate_mapping_rule(excelcol, datacol_id, extraact_id, extratgt_id, True)

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
        id = self.row_hidden_id.text if self.row_hidden_id.text not in (None, '') else None
        name = self.row_mapping_name.text
        filetype_id, filetype = self.row_dropdown_type.selected_value
        rules = []
        del_iid = self.row_hidden_del_fid.text[:-1].split(",") if self.row_hidden_del_fid.text else None
        for i in self.get_components():
            if isinstance(i, FlowPanel) and (i.tag is not None and isinstance(i.tag, list)):
                rules.append(i.tag)
                i.remove_from_parent()
        result = anvil.server.call('save_mapping_rules', id=id, mapping_rules={"name":name, "filetype":filetype_id, "rules":rules}, del_iid=del_iid)

        id = result['id']
        if id is not None and result['count'] is not None and result['dcount'] is not None:
            self.row_hidden_id.text = id
            self.row_hidden_del_fid.text = ''
            msg = f"Mapping {name} has been saved successfully."
            logger.info(msg)
        else:
            msg = f"WARNING: Problem occurs when saving mapping {name}."
            logger.warning(msg)
        self.item = (anvil.server.call('select_mapping_rules', id))[0]
        self.row_dropdown_type.selected_value = [filetype_id, filetype]
        if self.item.get('rule', None) is not None:
            self._generate_all_mapping_rules(self.item['rule'])
        Notification(msg).show()
        self.parent.raise_event('x-reload-rp')

    @btnmod.one_click_only
    @logger.log_function
    def row_button_delete_click(self, **event_args):
        """This method is called when the button is clicked"""
        to_be_del_id = self.row_hidden_id.text
        to_be_del_name = self.row_mapping_name.text
        confirm = Label(text=f"Proceed mapping <{to_be_del_name}> deletion by clicking DELETE.")
        userconf = alert(content=confirm,
                        title=f"Alert - mapping Deletion",
                        buttons=[("DELETE", const.Alerts.CONFIRM), ("CANCEL", const.Alerts.CANCEL)])

        if userconf == const.Alerts.CONFIRM:
            # Save the self.parent first so that remove_from_parent can be called before raising event
            #https://anvil.works/forum/t/children-to-parent-update/6324/4
            parent = self.parent
            if to_be_del_id not in (None, ''):
                result = anvil.server.call('delete_mapping', id=to_be_del_id)
                if result is not None and result > 0:
                    """ Reflect the change in tab dropdown """
                    self.remove_from_parent()
                    msg = f"Mapping {to_be_del_name} has been deleted."
                    logger.info(msg)
                    parent.raise_event('x-reload-rp', del_id=to_be_del_id)
                else:
                    msg = f"ERROR: Fail to delete mapping {to_be_del_name}."
                    logger.error(msg)
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

    @logger.log_function
    def _generate_mapping_rule(self, excelcol, datacol_id, extraact_id, extratgt_id, is_new=False, **event_args):
        logger.debug(f"excelcol={excelcol}, datacol_id={datacol_id}, extraact_id={extraact_id}, extratgt_id={extratgt_id}")
        cache_exp_tbl_def = ClientCache('generate_expense_tbl_def_dropdown')
        cache_extraact = ClientCache('generate_upload_action_dropdown')
        dict_exp_tbl_def = {k[1][0]: k[1][1] for k in cache_exp_tbl_def.get_cache()}
        dict_extraact = {k[1][0]: k[1][1] for k in cache_extraact.get_cache()}
        dict_lbl = {k[1][0]: k[1][1] for k in UploadMappingRulesController.generate_labels_dropdown()}
        dict_acct =  {k[1][0]: k[1][1] for k in UploadMappingRulesController.generate_accounts_dropdown()}
        datacol = dict_exp_tbl_def.get(datacol_id, None)
        extraact = dict_extraact.get(extraact_id, None)
        extratgt = dict_lbl.get(extratgt_id, None) if extraact_id == "L" else dict_acct.get(extratgt_id, None)
        rule = f"{self.row_lbl_1.text}{excelcol}{self.row_lbl_2.text}{datacol}."
        rule = f"{rule} Extra action(s): {extraact} {extratgt}" if extraact is not None else rule
        
        lbl_obj = Label(text=rule, font_size=12, foreground='indigo', icon=const.Icons.BULLETPOINT)
        fp = FlowPanel(spacing_above="small", spacing_below="small", tag=[excelcol, datacol_id, extraact_id, extratgt_id, rule, is_new])
        b = Button(
            icon=const.Icons.REMOVE,
            foreground=const.ColorSchemes.BUTTON_BG,
            font_size=12,
            align="left",
            spacing_above="small",
            spacing_below="small",
        )
        self.add_component(fp)
        fp.add_component(lbl_obj)
        fp.add_component(b)
        b.set_event_handler('click', self.mapping_button_minus_click)

    @logger.log_function
    def _generate_all_mapping_rules(self, rules, **event):
        for r in rules:
            excelcol, datacol_id, extraact_id, extratgt_id = r
            # Without converting to int it cannot fetch the value in get method below
            extratgt_id = int(extratgt_id) if extratgt_id is not None else extratgt_id
            self._generate_mapping_rule(excelcol, datacol_id, extraact_id, extratgt_id)
        