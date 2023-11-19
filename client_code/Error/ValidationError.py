import anvil.server

# This is a module.
# You can define variables and functions here, and use them from any form. For example, in a top-level form:

# Ref - https://anvil.works/forum/t/handling-exception-coming-from-the-server-uplink-modules/1400
@anvil.server.portable_class
class ValidationError(anvil.server.AnvilWrappedError):
    def __init__(self, message=None):
        if isinstance(message, ValidationError):
            message = str(message)
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return self.message

anvil.server._register_exception_type('ValidationError', ValidationError)