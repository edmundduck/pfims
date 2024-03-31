import anvil.server
from ..Utils.Constants import UnitTest

# This is a module.
# You can define variables and functions here, and use them from any form. For example, in a top-level form:

def retrieve_test_cases():
    # DEBUG
    print(f"retrieve_test_cases={anvil.server.call('access_unit_test_data')}")
    return anvil.server.call('access_unit_test_list')

def submit_server_test_cases(module):
    result = anvil.server.call('execute_server_test_cases', module)
    if result.get(module):
        single_result = result.get(module)
        error_msg = "\n".join(single_result.get(UnitTest.FAIL_MSG)) if single_result.get(UnitTest.FAIL_MSG) else None
        return single_result.get(UnitTest.SUCCESS_CNT), single_result.get(UnitTest.FAIL_CNT), error_msg
    else:
        return 0, 0, None
