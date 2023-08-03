from ._anvil_designer import form_poc4Template
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import tabula

class form_poc4(form_poc4Template):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        # Any code you write here will run before the form opens.

    def file_loader_1_change(self, file, **event_args):
        """This method is called when a new file is loaded into this FileLoader"""
        if file is not None:
            print("file.content_type=", file.content_type)
            if 'pdf' in file.content_type :
                anvil.server.call('test_tabula', file=file)
            else:
                result = anvil.server.call('import_file', file=file)
                for i in result:
                    cb = CheckBox(text=i)
                    self.flow_panel_3.add_component(cb)