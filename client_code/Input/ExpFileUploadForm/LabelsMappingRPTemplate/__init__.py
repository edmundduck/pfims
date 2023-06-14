from ._anvil_designer import LabelsMappingRPTemplateTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from ....App import Caching as cache

class LabelsMappingRPTemplate(LabelsMappingRPTemplateTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        # Any code you write here will run before the form opens.
        self.tgt_label.items = cache.to_dict_caching_labels()