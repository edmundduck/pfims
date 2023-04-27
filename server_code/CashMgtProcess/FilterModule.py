import anvil.secrets
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server

# This is a server module. It runs on the Anvil server,
# rather than in the user's browser.

@anvil.server.callable
# Save the filter and rules
def save_filter_rules(fid, filter_obj):
    print(fid)
    print(filter_obj)