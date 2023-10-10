import anvil.server
import anvil.users
# This is a module.
# You can define variables and functions here, and use them from any form. For example, in a top-level form:

@anvil.server.portable_class
class Setting:
    def __init__(self, data):
        self.set(data)

    def __str__(self):
        return "{0}: {1}, {2}, {3}, {4}, {5}".format(
            self.__class__,
            self.default_broker, 
            self.default_interval, 
            self.default_datefrom, 
            self.default_dateto, 
            self.logging_level)

    def get(self):
        return [self.default_broker, self.default_interval, self.default_datefrom, self.default_dateto, self.logging_level]

    def get_broker(self):
        return self.default_broker

    def get_search_interval(self):
        return self.default_interval

    def get_search_datefrom(self):
        return self.default_datefrom

    def get_search_dateto(self):
        return self.default_dateto

    def get_logging_level(self):
        return self.logging_level

    def set(self, data):
        if data:
            self.userid = data.get('userid')
            self.default_broker = data.get('default_broker')
            self.default_interval = data.get('default_interval')
            self.default_datefrom = data.get('default_datefrom')
            self.default_dateto = data.get('default_dateto')
            self.logging_level = data.get('logging_level')

    def is_valid(self):
        return True

    def __serialize__(self, global_data):
        global_data[f"Setting_{self.userid}"] = self.get()
        return self.userid

    def __deserialize__(self, userid, global_data):
        data = [userid] + global_data[f"Setting_{userid}"]
        self.__init__(data)