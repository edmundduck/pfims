import anvil.files
from anvil.files import data_files
import anvil.server
import os

# This is a server module. It runs on the Anvil server,
# rather than in the user's browser.

@anvil.server.callable
def access_unit_test_data():
    unittest_dir = data_files['unittest']

    with os.scandir(unittest_dir) as directory:
        for file in directory:
            if not file.name.startswith('.') and file.is_file():
                print(file.name)