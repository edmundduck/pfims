import anvil.files
from anvil.files import data_files
from ..Utils.Constants import UnitTest
import anvil.server
import re
import sys
import inspect

# This is a server module. It runs on the Anvil server,
# rather than in the user's browser.

@anvil.server.callable
def access_unit_test_list():
    """
    Return the list of unit test cases.

    Returns:
        list (list): A list of module names where module names match the unit test module standard.
    """
    return [v.__name__ for k, v in sys.modules.items() if '.Test.' in k]

@anvil.server.callable
def execute_server_test_cases(class_list=[]):
    """
    Execute all the server code test cases.

    Parameters:
        class_list (list of str): A list of module or class names to be included for test.

    Returns:
        result (dict of dict): Result dictionary which contains each module's unit test result, and the result is also a dictionary which includes all the test attributes.
    """
    # Return list of corresponding methods of classes under modules named with '.Test'
    all_methods = {}
    result = {}

    if not isinstance(class_list, (tuple, list)):
        class_list = [class_list]
    # for module in [v for k, v in sys.modules.items() if '.Test' in k]:
    for module in [v for k, v in sys.modules.items() if any(c in k for c in class_list)]:
        module_name = module.__name__

        for name, obj in inspect.getmembers(module, inspect.isclass):
            # Only the class name matches exactly the same as class_list can proceed, in order to filer out those imported classes
            if name in class_list[0]:
                methods = [method for method in dir(obj) if not method.startswith('__') and method.startswith('test')]
                if methods:
                    # Debug
                    # Only initiate a module in the dictionary when specific methods are available
                    if module_name not in all_methods:
                        all_methods[module_name] = []
                    all_methods[module_name].append((name, methods))

                    if module_name not in result:
                        result[module_name] = {}

                    if getattr(obj, 'test_all_methods', None):
                        cls = obj()
                        result[module_name] = cls.test_all_methods()
    return result