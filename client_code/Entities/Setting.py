import anvil.server
import anvil.users
# This is a module.
# You can define variables and functions here, and use them from any form. For example, in a top-level form:

@anvil.server.portable_class
class Setting:
    __db_column_def__ = ['userid', 'default_broker', 'default_interval', 'default_datefrom', 'default_dateto', 'logging_level']
    __property_def__ = __db_column_def__
    
    def __init__(self, data):
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
        return ', '.join(c for c in Setting.__db_column_def__)

    def get_dict(self):
        return { self.__property_def__[i]: getattr(self, self.__property_def__[i]) for i in range(len(self.__property_def__)) }

    def get_list(self):
        return [ getattr(self, self.__property_def__[i]) for i in range(len(self.__property_def__)) ]

    def get_broker(self):
        return getattr(self, self.__property_def__[1])

    def get_search_interval(self):
        return getattr(self, self.__property_def__[2])

    def get_search_datefrom(self):
        return getattr(self, self.__property_def__[3])

    def get_search_dateto(self):
        return getattr(self, self.__property_def__[4])

    def get_logging_level(self):
        return getattr(self, self.__property_def__[5])

    def set(self, data):
        if data:
            if isinstance(data, dict):
                for i in range(len(self.__property_def__)):
                    setattr(self, self.__property_def__[i], data.get(self.__property_def__[i], None))
            elif isinstance(data, (list, tuple)):
                for i in range(len(self.__property_def__)):
                    setattr(self, self.__property_def__[i], data[i])

    def copy(self):
        return Setting(self.get_dict())

    def is_valid(self):
        return True

    def __serialize__(self, global_data):
        global_data[f"{__class__.__name__}_{self.userid}"] = self.get_dict()
        return self.userid

    def __deserialize__(self, userid, global_data):
        data = global_data[f"{__class__.__name__}_{userid}"]
        self.__init__(data)