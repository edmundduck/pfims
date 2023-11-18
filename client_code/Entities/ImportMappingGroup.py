import anvil.server
from .BaseEntity import BaseEntity
from .ImportMappingRule import ImportMappingRule

# This is a module.
# You can define variables and functions here, and use them from any form. For example, in a top-level form:

@anvil.server.portable_class
class ImportMappingGroup(BaseEntity):
    __db_column_def__ = ['userid', 'id', 'name', 'filetype', 'description', 'lastsave']
    __property_def__ = __db_column_def__ + ['rules']
    
    def __init__(self, data=None):
        super().__init__(data)

    @staticmethod
    def get_column_definition():
        return ', '.join(c for c in ImportMappingGroup.__db_column_def__)

    def get_user_id(self):
        return getattr(self, self.__property_def__[0], None)
        
    def get_id(self):
        return getattr(self, self.__property_def__[1], None)

    def get_name(self):
        return getattr(self, self.__property_def__[2], None)
    
    def get_file_type(self):
        return getattr(self, self.__property_def__[3], None)

    def get_description(self):
        return getattr(self, self.__property_def__[4], None)

    def get_lastsaved_time(self):
        return getattr(self, self.__property_def__[5], None)

    def get_mapping_rules(self):
        return getattr(self, self.__property_def__[6], [])

    def set_user_id(self, userid):
        return self.set_single_attribute(0, userid)

    def set_id(self, id):
        rules = self.get_mapping_rules()
        if rules and len(rules) > 0:
            for t in range(len(rules)):
                rules[t] = rules[t].set_group_id(id)
        return self.set_single_attribute(1, id)
        
    def set_name(self, name):
        return self.set_single_attribute(2, name)
        
    def set_file_type(self, filetype):
        return self.set_single_attribute(3, filetype)
        
    def set_description(self, desc):
        return self.set_single_attribute(4, desc)
        
    def set_lastsaved_time(self, lastsaved_time):
        return self.set_single_attribute(5, lastsaved_time)
        
    def set_mapping_rules(self, rules):
        if isinstance(rules, ImportMappingRule):
            return self.set_single_attribute(6, [rules.set_group_id(self.get_id())])
        elif isinstance(rules, list):
            rule_list = []
            for r in rules:
                if isinstance(r, ImportMappingRule):
                    rule_list.append(r.set_group_id(self.get_id()))
                elif isinstance(r, dict):
                    rule_list.append(ImportMappingRule(r).set_group_id(self.get_id()))
            return self.set_single_attribute(6, rule_list)
        
    def copy(self):
        return ImportMappingGroup(self.get_dict())

    def is_valid(self):
        group_name, filetype, desc, rules = [self.get_name(), self.get_file_type(), self.get_description(), self.get_mapping_rules()]
        if not group_name or group_name.isspace(): return False
        if not filetype or filetype.isspace(): return False
        if len(desc) > 120: return False
        for r in rules:
            if not r.is_valid:
                return False
        return True
