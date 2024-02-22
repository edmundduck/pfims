import anvil.files
from anvil.files import data_files
from ..Utils.Constants import UnitTest
import anvil.server
import re

# This is a server module. It runs on the Anvil server,
# rather than in the user's browser.

@anvil.server.callable
def access_unit_test_config_file(mode=None):
    with open(data_files[UnitTest.TEST_CONFIG_FILE]) as f:
        if not mode:
            return list(line for line in f if UnitTest.DELIMITER in line)
        elif mode == UnitTest.CLIENT_ONLY:
            # part = re.search(r'# Client(.*)[#]*?', f.read(), re.DOTALL | re.DEBUG)
            part = re.search(r'# Client(.*)[#]*?', f.read(), re.DOTALL)
            print(list(line for line in part[1] if UnitTest.DELIMITER in part[1]) if part else None)
            return list(line for line in part[1] if UnitTest.DELIMITER in part[1]) if part else None
        elif mode == UnitTest.SERVER_ONLY:
            # part = re.search(r'# Server(.*)[#]*?', f.read(), re.DOTALL | re.DEBUG)
            part = re.search(r'# Server(.*)[#]*?', f.read(), re.DOTALL)
            print(part)
            print(part[1])
            print(list(line for line in part[1] if UnitTest.DELIMITER in part[1]) if part else None)
            return list(line for line in part[1] if UnitTest.DELIMITER in part[1]) if part else None
