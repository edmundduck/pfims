from ._anvil_designer import ExpFileUploadFormTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from ...App import Routing
from ...App import Caching as cache

class ExpFileUploadForm(ExpFileUploadFormTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)
    
        # Any code you write here will run when the form opens.
        self.dropdown_filetype.items = cache.get_caching_filter_type()
        self.file_loader_1.enabled = False

    def button_upload_filter_click(self, **event_args):
        """This method is called when the button is clicked"""
        Routing.open_upload_filter_form(self)

    def button_input_exp_click(self, **event_args):
        """This method is called when the button is clicked"""
        Routing.open_exp_input_form(self)

    def dropdown_filetype_show(self, **event_args):
        """This method is called when the DropDown is shown on the screen"""
        self.dropdown_filetype.items = cache.get_caching_filter_type()

    def dropdown_filetype_change(self, **event_args):
        """This method is called when an item is selected"""
        # TODO cache the filter dropdown
        userid = anvil.server.call('get_current_userid')
        if self.dropdown_filetype.selected_value is None:
            self.dropdown_filter.items = []
        else:
            self.dropdown_filter.items = anvil.server.call('generate_filter_dropdown', userid, self.dropdown_filetype.selected_value)

    def dropdown_filter_change(self, **event_args):
        """This method is called when an item is selected"""
        if self.dropdown_filter.selected_value is None:
            self.file_loader_1.enabled = False
        else:
            self.file_loader_1.enabled = True

    def file_loader_1_change(self, file, **event_args):
        """This method is called when a new file is loaded into this FileLoader"""
        if file is not None:
            self.label_filename.text = f"Filename: {file.name}"
            xls, frules = anvil.server.call('preview_file', file=file, fid=self.dropdown_filter.selected_value)
            for i in xls:
                cb = CheckBox(
                    text=i,
                    font_size=12,
                    align="left",
                    spacing_above="small",
                    spacing_below="small"
                )
                self.sheet_tabs_panel.add_component(cb)