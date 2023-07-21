from ._anvil_designer import ExpenseFileUploadFormTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from ...Utils import Routing
from ...Utils import Caching as cache
from ...Utils.Logging import dump, debug, info, warning, error, critical

class ExpenseFileUploadForm(ExpenseFileUploadFormTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)
    
        # Any code you write here will run when the form opens.
        self.file_loader_1.enabled = False
        self.button_next.visible = False

    def button_nav_upload_mapping_click(self, **event_args):
        """This method is called when the button is clicked"""
        Routing.open_upload_mapping_form(self)

    def button_nav_input_exp_click(self, **event_args):
        """This method is called when the button is clicked"""
        Routing.open_exp_input_form(self)

    def dropdown_filetype_show(self, **event_args):
        """This method is called when the DropDown is shown on the screen"""
        self.dropdown_filetype.items = cache.mapping_rules_filetype_dropdown()

    def dropdown_filetype_change(self, **event_args):
        """This method is called when an item is selected"""
        filetype_id, filetype = self.dropdown_filetype.selected_value
        debug.log(f"filetype_id={filetype_id}, filetype={filetype}")
        if filetype_id is None:
            self.dropdown_mapping_rule.items = []
        else:
            self.dropdown_mapping_rule.items = anvil.server.call('generate_mapping_dropdown', filetype_id)

    def dropdown_mapping_rule_change(self, **event_args):
        """This method is called when an item is selected"""
        if self.dropdown_mapping_rule.selected_value is None:
            self.file_loader_1.enabled = False
        else:
            self.file_loader_1.enabled = True

    @debug.log_function
    def file_loader_1_change(self, file, **event_args):
        """This method is called when a new file is loaded into this FileLoader"""
        if file is not None:
            self.label_filename.text = f"Uploaded filename: {file.name}"
            xls = anvil.server.call('preview_file', file=file)
            for i in xls:
                cb = CheckBox(
                    text=i,
                    font_size=12,
                    align="left",
                    spacing_above="small",
                    spacing_below="small"
                )
                self.sheet_tabs_panel.add_component(cb)
                cb.set_event_handler('change', self.enable_next_button)

    def enable_next_button(self, **event_args):
        cb = event_args['sender']
        vis = False
        if cb.checked:
            vis = True
        else:
            for i in cb.parent.get_components():
                if isinstance(i, CheckBox) and i.checked:
                    vis = True
        self.button_next.visible = vis

    @debug.log_function
    def button_next_click(self, **event_args):
        """This method is called when the button is clicked"""
        tablist = []
        for i in self.sheet_tabs_panel.get_components():
            if isinstance(i, CheckBox) and i.checked:
                tablist.append(i.text)
        info.log(f"{len(tablist)} tabs are chosen in {__name__}.")
        matrix = anvil.server.call('select_mapping_matrix', id=self.dropdown_mapping_rule.selected_value)
        debug.log("matrix=", matrix)
        extra = anvil.server.call('select_mapping_extra_actions', id=self.dropdown_mapping_rule.selected_value)
        debug.log("extra=", extra)
        df, lbls = anvil.server.call('import_file', file=self.file_loader_1.file, tablist=tablist, rules=matrix, extra=extra)
        dump.log("df=", df)
        debug.log("lbls=", lbls)
        Routing.open_exp_file_upload_form_p2(self, data=df, labels=lbls)
