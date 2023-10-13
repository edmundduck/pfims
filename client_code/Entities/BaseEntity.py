import anvil.server
import anvil.users
# This is a module.
# You can define variables and functions here, and use them from any form. For example, in a top-level form:

@anvil.server.portable_class
class BaseEntity:
    # Each child class must implement the following 2 private variables.
    __db_column_def__ = None
    __property_def__ = __db_column_def__
    
    def __init__(self, data=None):
        if not self.__db_column_def__ or not self.__property_def__:
            raise NotImplementedError(f'Private class variables __db_column_def__ and __property_def__ must be implemented in child class inheriting BaseEntity.')
        if data:
            self.set(data)
        else:
            self.set([None]*len(self.__property_def__))

    def __str__(self):
        return '{0}: {1}'.format(
            self.__class__.__name__,
            self.get_dict()
        )

    @staticmethod
    def get_column_definition():
        raise NotImplementedError(f'Static function get_column_definition() must be implemented in child class.')

    def get_dict(self):
        return { self.__property_def__[i]: getattr(self, self.__property_def__[i], None) for i in range(len(self.__property_def__)) }

    def get_list(self):
        return [ getattr(self, self.__property_def__[i], None) for i in range(len(self.__property_def__)) ]

    def set(self, data):
        if data:
            if isinstance(data, dict):
                for i in range(len(self.__property_def__)):
                    setattr(self, self.__property_def__[i], data.get(self.__property_def__[i], None))
            elif isinstance(data, (list, tuple)):
                for i in range(len(self.__property_def__)):
                    setattr(self, self.__property_def__[i], data[i])
            return self
        else:
            raise TypeError(f'Method set() only accepts dict, list or tuple as parameter.')
            
    def copy(self):
        raise NotImplementedError(f'Method copy() must be implemented in child class.')

    def is_valid(self):
        raise NotImplementedError(f'Method is_valid() must be implemented in child class.')

    def __serialize__(self, global_data):
        global_data[f"{__class__.__name__}_{self.userid}"] = self.get_dict()
        return self.userid

    def __deserialize__(self, userid, global_data):
        data = global_data[f"{__class__.__name__}_{userid}"]
        self.__init__(data)
