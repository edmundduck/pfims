import anvil.server

# This is a module.
# You can define variables and functions here, and use them from any form. For example, in a top-level form:

# Ref - https://anvil.works/forum/t/handling-exception-coming-from-the-server-uplink-modules/1400
class ValidationError(anvil.server.AnvilWrappedError):
    def __init__(self, message=None):
        if isinstance(message, ValidationError):
            message = str(message)
        self.message = message
        super().__init__(message)

    def __str__(self):
        return self.message

    def __bool__(self):
        # As this class represents error, it always return false representing 'invalid'.
        return False

    def append(self, message):
        if message is not None:
            if isinstance(message, ValidationError):
                message = str(message)
            self.message = '\n'.join((self.message, message))

    def is_empty(self):
        return True if not self.message else False
        
anvil.server._register_exception_type('ValidationError', ValidationError)