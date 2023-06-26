from ._anvil_designer import FileUploadMappingRPTemplateTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from ....App import Caching as cache
from ....App import Global as glo

class FileUploadMappingRPTemplate(FileUploadMappingRPTemplateTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        # Any code you write here will run before the form opens.
        self.row_dropdown_type.items = cache.get_caching_mapping_type()
        self.row_dropdown_datacol.items = cache.get_caching_exp_tbl_def()
        self.row_dropdown_extraact.items = cache.get_caching_upload_action()
        self.row_dropdown_lbl.items = cache.get_caching_labels_dropdown()
        self.row_dropdown_acct.items = cache.get_caching_accounts()

        # Generate all rules in a mapping
        if self.item.get('rule', None) is not None:
            self._generate_all_mapping_rules(self.item['rule'])

    def row_button_add_click(self, **event_args):
        """This method is called when the button is clicked"""
        excelcol = self.row_dropdown_excelcol.selected_value
        datacol_id, datacol = self.row_dropdown_datacol.selected_value.values() if self.row_dropdown_datacol.selected_value is not None else [None, None]
        extraact_id, extraact = self.row_dropdown_extraact.selected_value.values() if self.row_dropdown_extraact.selected_value is not None else [None, None]
        lbl_id, lbl = self.row_dropdown_lbl.selected_value.values() if self.row_dropdown_lbl.selected_value is not None else [None, None]
        acct_id, acct = self.row_dropdown_acct.selected_value.values() if self.row_dropdown_acct.selected_value is not None else [None, None]
        self._generate_mapping_rule(excelcol, datacol_id, extraact_id, lbl_id, acct_id)

    def mapping_button_minus_click(self, **event_args):
        b = event_args['sender']
        if b.parent.tag[0] is not None: self.row_hidden_del_fid.text = self.row_hidden_del_fid.text + f"{b.parent.tag[0]},"
        b.parent.remove_from_parent()

    def row_button_save_click(self, **event_args):
        """This method is called when the button is clicked"""
        userid = anvil.server.call('get_current_userid')
        id = self.row_hidden_id.text if self.row_hidden_id.text not in (None, '') else None
        name = self.row_mapping_name.text
        filetype = self.row_dropdown_type.selected_value
        rules = []
        del_iid = self.row_hidden_del_fid.text[:-1].split(",") if self.row_hidden_del_fid.text else None
        for i in self.get_components():
            if isinstance(i, FlowPanel) and (i.tag is not None and isinstance(i.tag, list)):
                rules.append(i.tag)
                # TODO to regenerate iid after saving
                i.remove_from_parent()
        result = anvil.server.call('save_mapping_rules', uid=userid, id=id, \
                                   mapping_rules={"name":name, "filetype":filetype, "rules":rules}, del_iid=del_iid)

        id = result['id']
        if id is not None and result['count'] is not None and result['dcount'] is not None:
            self.row_hidden_id.text = id
            self.row_hidden_del_fid.text = ''
            n = Notification(f"mapping {name} has been saved successfully.")
        else:
            n = Notification(f"WARNING: Problem occurs when saving mapping {name}.")
        # TODO to regenerate iid after saving
        self.item = (anvil.server.call('select_mapping_rules', userid, id))[0]
        self.row_dropdown_type.selected_value = self.item.get('filetype')
        if self.item.get('rule', None) is not None:
            self._generate_all_mapping_rules(self.item['rule'])
        n.show()

    def row_button_delete_click(self, **event_args):
        """This method is called when the button is clicked"""
        userid = anvil.server.call('get_current_userid')
        to_be_del_fid = self.row_hidden_id.text
        to_be_del_fname = self.row_mapping_name.text
        msg = Label(text=f"Proceed mapping <{to_be_del_fname}> deletion by clicking DELETE.")
        userconf = alert(content=msg,
                        title=f"Alert - mapping Deletion",
                        buttons=[
                        ("DELETE", "Y"),
                        ("CANCEL", "N")
                        ])

        if userconf == "Y":
            if to_be_del_fid not in (None, ''):
                result = anvil.server.call('delete_mapping', uid=userid, fid=to_be_del_fid)
                if result is not None and result > 0:
                    """ Reflect the change in tab dropdown """
                    self.remove_from_parent()
                    n = Notification(f"mapping {to_be_del_fname} has been deleted.")
                else:
                    n = Notification(f"ERROR: Fail to delete mapping {to_be_del_fname}.")
                n.show()
            else:
                self.remove_from_parent()

    def row_dropdown_extraact_show(self, **event_args):
        """This method is called when the DropDown is shown on the screen"""
        self.row_dropdown_lbl.visible = True if self.row_dropdown_extraact.selected_value is not None and self.row_dropdown_extraact.selected_value['id'] == "L" else False
        self.row_dropdown_acct.visible = True if self.row_dropdown_extraact.selected_value is not None and self.row_dropdown_extraact.selected_value['id'] == "A" else False

    def row_dropdown_extraact_change(self, **event_args):
        """This method is called when an item is selected"""
        self.row_dropdown_lbl.visible = True if self.row_dropdown_extraact.selected_value is not None and self.row_dropdown_extraact.selected_value['id'] == "L" else False
        self.row_dropdown_acct.visible = True if self.row_dropdown_extraact.selected_value is not None and self.row_dropdown_extraact.selected_value['id'] == "A" else False

    def _generate_mapping_rule(self, excelcol, datacol_id, extraact_id, lbl_id, acct_id, **event_args):
        dict_exp_tbl_def = cache.to_dict_caching_exp_tbl_def()
        dict_extraact = cache.to_dict_caching_upload_action()
        dict_lbl = cache.to_dict_caching_labels()
        datacol = dict_exp_tbl_def.get(datacol_id, None)
        extraact = dict_extraact.get(extraact_id, None)
        lbl = dict_lbl.get(lbl_id, None)
        rule = f"{self.row_lbl_1.text}{excelcol}{self.row_lbl_2.text}{datacol}."
        rule = f"{rule} Extra action(s): {extraact} {lbl}" if extraact is not None else rule
        
        lbl_obj = Label(text=rule, font_size=12, foreground='indigo', icon='fa:info')
        fp = FlowPanel(spacing_above="small", spacing_below="small", tag=[excelcol, datacol_id, extraact_id, lbl_id, rule])
        b = Button(
            icon='fa:minus',
            foreground="Blue",
            font_size=12,
            align="left",
            spacing_above="small",
            spacing_below="small",
        )
        self.add_component(fp)
        fp.add_component(lbl_obj)
        fp.add_component(b)
        b.set_event_handler('click', self.mapping_button_minus_click)

    def _generate_all_mapping_rules(self, rules, **event):
        for r in rules:
            excelcol, datacol_id, extraact_id, lbl_id = r
            # Without converting to int it cannot fetch the value in get method below
            lbl_id = int(lbl_id) if lbl_id is not None else lbl_id
            self._generate_mapping_rule(excelcol, datacol_id, extraact_id, lbl_id)
        