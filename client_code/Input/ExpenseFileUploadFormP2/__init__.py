from ._anvil_designer import ExpenseFileUploadFormP2Template
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from ...App import Routing
from ...App import Caching as cache

class ExpenseFileUploadFormP2(ExpenseFileUploadFormP2Template):
    def __init__(self, dataframe, labels, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        # Any code you write here will run when the form opens.
        self.button_next.visible = False
        # Transpose Dict of List (DL) to List of Dict (LD)
        # Ref - https://stackoverflow.com/questions/37489245/transposing-pivoting-a-dict-of-lists-in-python
        DL = {
            'srclbl': labels,
            'action': [ None for i in range(len(labels))],
            'tgtlbl': [ None for i in range(len(labels))],
            'new': labels
        }
        self.labels_mapping_panel.items = [dict(zip(DL, col)) for col in zip(*DL.values())]
        self.hidden_action_count.text = len(labels)
        self.labels_mapping_panel.add_event_handler('x-handle-action-count', self.handle_action_count)

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

    def button_next_click(self, **event_args):
        """This method is called when the button is clicked"""
        # 1. Get all items with action = 'C', and grab new field to create new labels
        # DL = Dict of Lists
        DL = {k: [dic[k] for dic in self.labels_mapping_panel.items] for k in self.labels_mapping_panel.items[0]}
        DL_action = {k: [dic[k] for dic in DL['action']] for k in DL['action'][0]}
        pos_create = [x for x in range(len(DL_action['id'])) if DL_action['id'][x] == 'C']
        lbl_mogstr = {
            'name': [DL['new'][x] for x in pos_create],
            'keywords': [ None for i in range(len(pos_create)) ],
            'status': [ True for i in range(len(pos_create)) ]
        }
        # labels param is transposed from DL to LD (List of Dicts)
        lbl_id = anvil.server.call('create_label', labels=[dict(zip(lbl_mogstr, col)) for col in zip(*lbl_mogstr.values())])

        if lbl_id is None:
            n = Notification("ERROR: Fail to create new labels. Abort the labe mapping process.")
            return

        # 2. Replace labels with action = 'C' to the newly created label codes in step 1
        print(lbl_id)
        for lbl_loc in range(len(lbl_id)):
            DL['tgtlbl'][pos_create[lbl_loc]] = lbl_id[lbl_loc]
        print(DL)
    
        # 3. Replace labels with action = 'M' and 'C' to the target label codes in df


    def handle_action_count(self, action, prev, **event_args):
        if action is None:
            self.hidden_action_count.text = int(self.hidden_action_count.text) + 1
        elif prev is None:
            self.hidden_action_count.text = int(self.hidden_action_count.text) - 1
        else:
            pass
        self.enable_next_button()
