import anvil.server
from ..Utils.Constants import UnitTest

# This is a module.
# You can define variables and functions here, and use them from any form. For example, in a top-level form:

def retrieve_test_cases():
    return anvil.server.call('access_unit_test_config_file', UnitTest.CLIENT_ONLY)
