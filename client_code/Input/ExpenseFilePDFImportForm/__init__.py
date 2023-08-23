from ._anvil_designer import ExpenseFilePDFImportFormTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from ...Utils import Routing
from ...Utils import Caching as cache
from ...Utils.Logger import ClientLogger

logger = ClientLogger()

class ExpenseFilePDFImportForm(ExpenseFilePDFImportFormTemplate):
    def __init__(self, data, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        # Any code you write here will run when the form opens.
        self.dropdown_tabs.items = anvil.server.call('generate_expensetabs_dropdown')
        # self.tag = {'data': data}
        # logger.debug("self.tag=", self.tag)
        self.button_next.visible = False
        # Transpose Dict of Lists (DL) to List of Dicts (LD)
        # Ref - https://stackoverflow.com/questions/37489245/transposing-pivoting-a-dict-of-lists-in-python
        DL = {
            'srccol': data[0],
            'tgtcol': [],
            'sign': []
        }
        logger.trace("DL=", DL)
        self.cols_mapping_panel.items = [dict(zip(DL, col)) for col in zip(*DL.values())]
        logger.trace("self.cols_mapping_panel.items=", self.cols_mapping_panel.items)
        # self.hidden_action_count.text = len(labels)
        # self.cols_mapping_panel.add_event_handler('x-handle-mapping-count', self.handle_mapping_count)
        # self.cols_mapping_panel.add_event_handler('x-refresh-label-cache', self.handle_action_count)

    def button_nav_upload_mapping_click(self, **event_args):
        """This method is called when the button is clicked"""
        Routing.open_upload_mapping_form(self)

    def button_nav_input_exp_click(self, **event_args):
        """This method is called when the button is clicked"""
        Routing.open_exp_input_form(self)

    def enable_next_button(self, **event_args):
        if self.hidden_action_count.text == 0:
            self.button_next.visible = True
        else:
            self.button_next.visible = False

    @logger.log_function
    def button_next_click(self, **event_args):
        """This method is called when the button is clicked"""
        df = anvil.server.call('update_pdf_mapping', data=self.tag.get('data'), mapping=self.cols_mapping_panel.items)
        Routing.open_exp_input_form(self, tab_id=self.dropdown_tabs.selected_value, data=df)

    def handle_mapping_count(self, action, prev, **event_args):
        if action is None:
            self.hidden_mapping_count.text = int(self.hidden_mapping_count.text) + 1
        elif prev is None:
            self.hidden_mapping_count.text = int(self.hidden_mapping_count.text) - 1
        else:
            pass
        self.enable_next_button()

    def refresh_label_cache(self, **event_args):
        cache.labels_reset()
