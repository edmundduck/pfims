import anvil.server
from ..Entities.TestCase import TestCase
from ..Utils.Constants import UnitTest

# This is a module.
# You can define variables and functions here, and use them from any form. For example, in a top-level form:

def retrieve_test_cases():
    return anvil.server.call('access_unit_test_config_file')

def submit_server_test_cases(module):
    return anvil.server.call('execute_server_test_cases', module)
