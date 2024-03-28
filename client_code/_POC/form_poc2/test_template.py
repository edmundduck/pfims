from ._anvil_designer import test_templateTemplate
from anvil import *
import anvil.server
from ...Utils.Constants import Roles

class test_template(test_templateTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

# Any code you write here will run when the form opens.
    self.row_label_pnl.role = Roles.AMT_NEGATIVE if self.item['pnl'] < 0 else Roles.AMT_POSITIVE

  def button_vis_click(self, **event_args):
    """This method is called when the button is clicked"""
    self.visible = False
    self.parent.raise_event_on_children('x-vis')

