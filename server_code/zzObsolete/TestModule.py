import anvil.secrets
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
import camelot

# This is a server module. It runs on the Anvil server,
# rather than in the user's browser.
#
# To allow anvil.server.call() to call functions here, we mark
# them with @anvil.server.callable.
# Here is an example - you can replace it with your own:
#
# @anvil.server.callable
# def say_hello(name):
#   print("Hello, " + name + "!")
#   return 42
#

@anvil.server.callable
def zz_test_session():
    print(anvil.server.session)
    if anvil.server.session is None:
        print("It's none")
    else:
        print("It's not none")
    if not anvil.server.session:
        print("It's empty")
    else:
        print("It's not empty")

class NewLog:
    def __init__(self):
        print("NewLog=", anvil.server.session)

def test_camelot(file):
    tables = camelot.read_pdf(file)
    print(tables)