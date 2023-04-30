from ._anvil_designer import UploadFilterRPTemplateTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from ....App import Caching as cache
from ....App import Global as glo

class UploadFilterRPTemplate(UploadFilterRPTemplateTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        # Any code you write here will run before the form opens.
        self.row_dropdown_type.items = cache.get_caching_filter_type()
        self.row_dropdown_datacol.items = cache.get_caching_exp_tbl_def()
        self.row_dropdown_extraact.items = cache.get_caching_upload_action()
        self.row_dropdown_lbl.items = cache.get_caching_labels_dropdown()

        # Generate all rules in a filter
        if self.item.get('frules', None) is not None:
            self._generate_all_filter_rules(self.item['frules'])

    def row_button_add_click(self, **event_args):
        """This method is called when the button is clicked"""
        excelcol = self.row_dropdown_excelcol.selected_value
        datacol_id, datacol = self.row_dropdown_datacol.selected_value.values() if self.row_dropdown_datacol.selected_value is not None else [None, None]
        extraact_id, extraact = self.row_dropdown_extraact.selected_value.values() if self.row_dropdown_extraact.selected_value is not None else [None, None]
        lbl_id, lbl = self.row_dropdown_lbl.selected_value.values() if self.row_dropdown_lbl.selected_value is not None else [None, None]
        self._generate_filter_rule(None, excelcol, datacol_id, extraact_id, lbl_id)

    def filter_button_minus_click(self, **event_args):
        b = event_args['sender']
        if b.parent.tag[0] is not None: self.row_hidden_del_fid.text = self.row_hidden_del_fid.text + f"{b.parent.tag[0]},"
        b.parent.remove_from_parent()

    def row_button_save_click(self, **event_args):
        """This method is called when the button is clicked"""
        userid = anvil.server.call('get_current_userid')
        fid = self.row_hidden_fid.text if self.row_hidden_fid.text not in (None, '') else None
        fname = self.row_filter_name.text
        ftype = self.row_dropdown_type.selected_value
        frules = []
        del_iid = self.row_hidden_del_fid.text[:-1].split(",") if self.row_hidden_del_fid.text else None
        for i in self.get_components():
            if isinstance(i, FlowPanel) and (i.tag is not None and isinstance(i.tag, list)):
                frules.append(i.tag)
                # TODO to regenerate iid after saving
                i.remove_from_parent()
        result = anvil.server.call('save_filter_rules', uid=userid, fid=fid, \
                                   filter_obj={"name":fname, "type":ftype, "rules":frules}, del_iid=del_iid)

        fid = result['fid']
        if fid is not None and result['count'] is not None and result['dcount'] is not None:
            self.row_hidden_fid.text = fid
            self.row_hidden_del_fid.text = ''
            n = Notification(f"Filter {fname} has been saved successfully.")
        else:
            n = Notification(f"WARNING: Problem occurs when saving filter {fname}.")
        # TODO to regenerate iid after saving
        self.item = (anvil.server.call('select_filter_rules', userid, fid))[0]
        if self.item.get('frules', None) is not None:
            print(self.item['frules'])
            self._generate_all_filter_rules(self.item['frules'])
        n.show()

    def row_button_delete_click(self, **event_args):
        """This method is called when the button is clicked"""
        userid = anvil.server.call('get_current_userid')
        to_be_del_fid = self.row_hidden_fid.text
        to_be_del_fname = self.row_filter_name.text
        msg = Label(text=f"Proceed filter <{to_be_del_fname}> deletion by clicking DELETE.")
        userconf = alert(content=msg,
                        title=f"Alert - Filter Deletion",
                        buttons=[
                        ("DELETE", "Y"),
                        ("CANCEL", "N")
                        ])

        if userconf == "Y":
            if to_be_del_fid not in (None, ''):
                result = anvil.server.call('delete_filter', uid=userid, fid=to_be_del_fid)
                if result is not None and result > 0:
                    """ Reflect the change in tab dropdown """
                    self.remove_from_parent()
                    n = Notification(f"Filter {to_be_del_fname} has been deleted.")
                else:
                    n = Notification(f"ERROR: Fail to delete filter {to_be_del_fname}.")
                n.show()
            else:
                self.remove_from_parent()

    def row_dropdown_extraact_show(self, **event_args):
        """This method is called when the DropDown is shown on the screen"""
        self.row_dropdown_lbl.visible = False if self.row_dropdown_extraact.selected_value is None else True

    def row_dropdown_extraact_change(self, **event_args):
        """This method is called when an item is selected"""
        self.row_dropdown_lbl.visible = False if self.row_dropdown_extraact.selected_value is None else True

    def _generate_filter_rule(self, iid, excelcol, datacol_id, extraact_id, lbl_id, **event_args):
        dict_exp_tbl_def = cache.to_dict_caching_exp_tbl_def()
        dict_extraact = cache.to_dict_caching_upload_action()
        dict_lbl = cache.to_dict_caching_labels()
        datacol = dict_exp_tbl_def.get(datacol_id, None)
        extraact = dict_extraact.get(extraact_id, None)
        lbl = dict_lbl.get(lbl_id, None)
        rule = f"{self.row_lbl_1.text}{excelcol}{self.row_lbl_2.text}{datacol}."
        rule = f"{rule} Extra action(s): {extraact} {lbl}" if extraact is not None else rule
        
        lbl_obj = Label(text=rule, font_size=12, foreground='indigo', icon='fa:info')
        fp = FlowPanel(spacing_above="small", spacing_below="small", tag=[iid, excelcol, datacol_id, extraact_id, lbl_id])
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
        b.set_event_handler('click', self.filter_button_minus_click)

    def _generate_all_filter_rules(self, rules, **event):
        for r in rules:
            iid, excelcol, datacol_id, extraact_id, lbl_id = r
            # Without converting to int it cannot fetch the value in get method below
            lbl_id = int(lbl_id) if lbl_id is not None else lbl_id
            self._generate_filter_rule(iid, excelcol, datacol_id, extraact_id, lbl_id)
        