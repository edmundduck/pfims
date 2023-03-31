import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

# This is a module.
# You can define variables and functions here, and use them from any form. For example, in a top-level form:
#
#    from . import Module1
#
#    Module1.say_hello()
#

def open_exp_input_form(self, **event_args):
    from .Input.ExpenseInputForm import ExpenseInputForm
    self.clear()
    print("exp", (i.text for i in self.item))
    #self.add_component(ExpenseInputForm())
    anvil.get_open_form().add_component(ExpenseInputForm())

def open_acct_maint_form(self, **event_args):
    from .Input.AccountMaintForm import AccountMaintForm
    self.clear()
    print("acct", self.label_1.text)
    self.add_component(AccountMaintForm())