import anvil.server

# This is a module.
# You can define variables and functions here, and use them from any form. For example, in a top-level form:

class AppError():
    def __init__(self, err):
        self.err = err

    def __bool__(self):
        # As this class represents error, it always return false representing 'invalid'.
        return False

    def get_error(self):
        return self.err

    def set_error(self, err):
        self.err = err
