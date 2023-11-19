import anvil.server

# This is a module.
# You can define variables and functions here, and use them from any form. For example, in a top-level form:

# Ref - https://anvil.works/forum/t/handling-exception-coming-from-the-server-uplink-modules/1400
class ValidationError(anvil.server.AnvilWrappedError):
    # def __init__(self, message, *args):
    #     self.message = message
    #     self.args = args
    
    # def __str__(self):
    #     return "[{}] {} {}".format(type(self).__name__, self.message, " ".join(self.args))
    pass
    
anvil.server._register_exception_type('ValidationError', ValidationError)