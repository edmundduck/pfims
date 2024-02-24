import anvil.server
from ..Utils.Constants import UnitTest

# This is a module.
# You can define variables and functions here, and use them from any form. For example, in a top-level form:

@anvil.server.portable_class
class TestCase:
    def __init__(self, config_line=None):
        if config_line:
            if UnitTest.DELIMITER in config_line:
                items = config_line.split(UnitTest.DELIMITER)
                self.title = items[0].strip()
                self.func = items[1].replace(" ", "").split(UnitTest.DELIMITER_FUNC) if UnitTest.DELIMITER_FUNC in items[1] else [items[1].replace(" ", "")]
            else:
                raise Error(f'Not a valid test config line.')

    def __str__(self):
        return '{0}: {1}, {2}'.format(
            self.__class__.__name__,
            self.get_title(),
            self.get_test_functions()
        )

    def get_title(self):
        return self.title

    def get_test_functions(self):
        return self.func

    def set_title(self, title):
        self.title = title

    def set_test_functions(self, func):
        if isinstance(func, (list, tuple)):
            self.func = func
        else:
            raise TypeError(f'set_test_functions parameter must be either List or Tuple.')