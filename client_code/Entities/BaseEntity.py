import anvil.server
import anvil.users
# This is a module.
# You can define variables and functions here, and use them from any form. For example, in a top-level form:

@anvil.server.portable_class
class BaseEntity:
    __db_column_def__ = ['userid']
    __property_def__ = __db_column_def__
    
    def __init__(self, data=None):
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
        return ', '.join(c for c in BaseEntity.__db_column_def__)

    def get_dict(self):
        return { self.__property_def__[i]: getattr(self, self.__property_def__[i]) for i in range(len(self.__property_def__)) }

    def get_list(self):
        return [ getattr(self, self.__property_def__[i]) for i in range(len(self.__property_def__)) ]

    def set(self, data):
        if data:
            if isinstance(data, dict):
                for i in range(len(self.__property_def__)):
                    setattr(self, self.__property_def__[i], data.get(self.__property_def__[i], None))
            elif isinstance(data, (list, tuple)):
                for i in range(len(self.__property_def__)):
                    setattr(self, self.__property_def__[i], data[i])
        else:
            raise TypeError(f'Function \'set\' only accepts dict, list or tuple as parameter.')
            

    def copy(self):
        return BaseEntity(self.get_dict())

    def is_valid(self):
        return True

    def __serialize__(self, global_data):
        global_data[f"{__class__.__name__}_{self.userid}"] = self.get_dict()
        return self.userid

    def __deserialize__(self, userid, global_data):
        data = global_data[f"{__class__.__name__}_{userid}"]
        self.__init__(data)
