from ._anvil_designer import QnATemplate
from anvil import *
import anvil.server

class QnA(QnATemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        # Any code you write here will run before the form opens.
        self.label_q.text = self.question
        self.label_a.text = self.answer