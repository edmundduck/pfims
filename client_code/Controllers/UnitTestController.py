import anvil.server
from ..Utils.Constants import UnitTest
from ..Utils.ClientCache import ClientCache
from ..Utils.Logger import ClientLogger

# This is a module.
# You can define variables and functions here, and use them from any form. For example, in a top-level form:

logger = ClientLogger()

def retrieve_test_cases():
    """
    Return the list of unit test cases.

    Returns:
        list (list): A list of module names where module names match the unit test module standard.
    """
    return anvil.server.call('access_unit_test_list')

def submit_server_test_cases(module):
    """
    Execute all the server code test cases.

    Parameters:
        module (list of str): A list of module or class names to be included for test.

    Returns:
        success_count (int): The count of successful test cases per executed module.
        failure_count (int): The count of failure test cases per executed module.
        error_msg (list of str): The list of error messages returned from failure test cases.
    """
    logger.debug(f"Initializing unit test data ...")
    anvil.server.call('initialize_unit_test_data')
    logger.debug(f"Executing test cases {module} ...")
    result = anvil.server.call('execute_server_test_cases', module)
    logger.debug(f"Clearing all caches ...")
    ClientCache.clear_all_cache()
    if result.get(module):
        single_result = result.get(module)
        error_msg = "\n".join(single_result.get(UnitTest.FAIL_MSG)) if single_result.get(UnitTest.FAIL_MSG) else None
        return single_result.get(UnitTest.SUCCESS_CNT), single_result.get(UnitTest.FAIL_CNT), error_msg
    else:
        return 0, 0, None
