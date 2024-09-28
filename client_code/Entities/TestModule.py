import anvil.server
from ..Utils.Constants import UnitTest
import inspect

# This is a module.
# You can define variables and functions here, and use them from any form. For example, in a top-level form:

@anvil.server.portable_class
class TestModule:
    def __init__(self):
        pass

    def test_all_methods(self):
        success_count = 0
        failure_count = 0
        failure_msg = []
        this_name = inspect.currentframe().f_code.co_name
        for method in dir(self):
            if callable(getattr(self, method)) and method.startswith("test") and method != this_name:
                func = getattr(self, method)
                result = func()
                if result:
                    failure_count += 1
                    failure_msg.append(result)
                else:
                    success_count += 1
        return {
            UnitTest.SUCCESS_CNT: success_count,
            UnitTest.FAIL_CNT: failure_count,
            UnitTest.FAIL_MSG: failure_msg
        }
