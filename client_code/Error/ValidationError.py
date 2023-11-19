import anvil.server
import numpy as np

# This is a module.
# You can define variables and functions here, and use them from any form. For example, in a top-level form:

# Ref - https://anvil.works/forum/t/handling-exception-coming-from-the-server-uplink-modules/1400
@anvil.server.portable_class
class ValidationError(anvil.server.AnvilWrappedError):
    def __init__(self, message=None):
        def find_unique(list_items):
            unique_dict = {}
            for i in list_items:
                if unique_dict.get(i, None) is None:
                    unique_dict[i] = i
            return unique_dict.keys()
                    
        if isinstance(message, ValidationError):
            message = str(message)
        self.message = find_unique(message)
        super().__init__(self.message)

    def __str__(self):
        return self.message

anvil.server._register_exception_type('ValidationError', ValidationError)