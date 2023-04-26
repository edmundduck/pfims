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
        self.row_dropdown_datacol.items = cache.get_caching_exp_tbl_def()
        self.row_dropdown_extraact.items = cache.get_caching_upload_action()
        self.row_dropdown_lbl.items = cache.get_caching_labels_dropdown()

    def row_button_add_click(self, **event_args):
        """This method is called when the button is clicked"""
        excelcol = self.row_dropdown_excelcol.selected_value
        datacol_id, datacol = self.row_dropdown_datacol.selected_value.values() if self.row_dropdown_datacol.selected_value is not None else [None, None]
        extraact_id, extraact = self.row_dropdown_extraact.selected_value.values() if self.row_dropdown_extraact.selected_value is not None else [None, None]
        lbl = self.row_dropdown_lbl.selected_value[1] if self.row_dropdown_lbl.selected_value is not None else None
        rule = self.row_lbl_1.text + excelcol + self.row_lbl_2.text + datacol + "."
        rule = rule + " Extra action(s): " + extraact + " " + lbl if extraact is not None else rule
        lbl_obj = Label(text=rule, font_size=12, foreground='indigo', tag=[excelcol, datacol_id, extraact_id, lbl], icon='fa:info')
        fp = FlowPanel(spacing_above="small", spacing_below="small")
        b = Button(
            icon='fa:minus',
            foreground="Blue",
            font_size=12,
            align="left",
            spacing_above="small",
            spacing_below="small",
            tag=[excelcol, datacol_id]
        )
        self.add_component(fp)
        fp.add_component(lbl_obj)
        fp.add_component(b)
        b.set_event_handler('click', self.filter_button_minus_click)

    def filter_button_minus_click(self, **event_args):
        b = event_args['sender']
        # TODO ... remove only minus button and the label
        b.parent.remove_from_parent()

    def row_button_save_click(self, **event_args):
        """This method is called when the button is clicked"""
        fid = self.row_hidden_fid.text if self.row_hidden_fid.text is not None else None
        fname = self.row_filter_name.text
        ftype = self.row_dropdown_type.selected_value
        frules = None
        for i in self.get_components():
            print(dict(i))
            if isinstance(i, FlowPanel):
                print(i)
