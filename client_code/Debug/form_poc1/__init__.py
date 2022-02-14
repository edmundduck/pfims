from ._anvil_designer import form_poc1Template
from anvil import *
import anvil.users
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

class form_poc1(form_poc1Template):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run when the form opens.
    """
    #dict_test = {'a': 1, 'b': 2}
    dict_test = {}
    a, b = dict_test.get('a', [0, 0])
    print("a={}, b={}".format(a, b))
    """
