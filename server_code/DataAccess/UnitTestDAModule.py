import anvil.files
from anvil.files import data_files
import anvil.server

# This is a server module. It runs on the Anvil server,
# rather than in the user's browser.

@anvil.server.callable
def access_unit_test_data():
    with open(data_files['load_unittest_data.sql']) as f:
        print(f"{list(line.strip() for line in f)}")