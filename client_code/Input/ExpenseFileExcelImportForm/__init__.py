from ._anvil_designer import ExpenseFileExcelImportFormTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from ...Utils import Routing
from ...Utils.ClientCache import ClientCache
from ...Utils.Logger import ClientLogger

logger = ClientLogger()

class ExpenseFileExcelImportForm(ExpenseFileExcelImportFormTemplate):
    def __init__(self, data, labels, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        # Any code you write here will run when the form opens.
        cache_labels = ClientCache('generate_labels_dropdown')
        self.dropdown_tabs.items = ClientCache('generate_expensetabs_dropdown')
        self.tag = {'data': data}
        logger.debug("self.tag=", self.tag)
        self.button_next.visible = False
        # Prefill "labels map to" dropdown by finding high proximity choices
        relevant_lbls = anvil.server.call('predict_relevant_labels', srclbl=labels, curlbl=cache_labels.get_cache())
        logger.debug("relevant_lbls=", relevant_lbls)
        # Transpose Dict of Lists (DL) to List of Dicts (LD)
        # Ref - https://stackoverflow.com/questions/37489245/transposing-pivoting-a-dict-of-lists-in-python
        DL = {
            'srclbl': labels,
            'action': [ None for i in range(len(labels))],
            'tgtlbl': relevant_lbls,
            'new': labels
        }
        logger.trace("DL=", DL)
        self.labels_mapping_panel.items = [dict(zip(DL, col)) for col in zip(*DL.values())]
        logger.trace("self.labels_mapping_panel.items=", self.labels_mapping_panel.items)
        self.hidden_action_count.text = len(labels)
        self.labels_mapping_panel.add_event_handler('x-handle-action-count', self.handle_action_count)
        self.labels_mapping_panel.add_event_handler('x-refresh-label-cache', self.refresh_label_cache)

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
        df = anvil.server.call('update_mapping', data=self.tag.get('data'), mapping=self.labels_mapping_panel.items)
        Routing.open_exp_input_form(self, tab_id=self.dropdown_tabs.selected_value, data=df)

    def handle_action_count(self, action, prev, **event_args):
        if action is None:
            self.hidden_action_count.text = int(self.hidden_action_count.text) + 1
        elif prev is None:
            self.hidden_action_count.text = int(self.hidden_action_count.text) - 1
        else:
            pass
        self.enable_next_button()

    def refresh_label_cache(self, **event_args):
        cache_labels = ClientCache('generate_labels_dropdown')
        cache_labels.clear_cache()