import anvil.server
from .BaseEntity import BaseEntity

# This is a module.
# You can define variables and functions here, and use them from any form. For example, in a top-level form:

@anvil.server.portable_class
class ImportMappingRule(BaseEntity):
    __db_column_def__ = ['gid', 'col', 'col_code', 'eaction', 'etarget', 'rule']
    __property_def__ = ['userid'] + __db_column_def__
    
    def __init__(self, data=None):
        super().__init__(data)

    @staticmethod
    def get_column_definition():
        return ', '.join(c for c in ImportMappingRule.__db_column_def__)

    @staticmethod
    def field_group_id():
        return ImportMappingRule.__property_def__[1]
    
    @staticmethod
    def field_column_id():
        return ImportMappingRule.__property_def__[2]
    
    @staticmethod
    def field_mapped_column_type():
        return ImportMappingRule.__property_def__[3]
    
    @staticmethod
    def field_extra_action():
        return ImportMappingRule.__property_def__[4]
    
    @staticmethod
    def field_extra_action_target_code():
        return ImportMappingRule.__property_def__[5]
    
    @staticmethod
    def field_rule_desc():
        return ImportMappingRule.__property_def__[6]
    
    def get_user_id(self):
        return getattr(self, self.__property_def__[0], None)
        
    def get_group_id(self):
        return getattr(self, self.__property_def__[1], None)

    def get_column_id(self):
        return getattr(self, self.__property_def__[2], None)
    
    def get_mapped_column_type(self):
        return getattr(self, self.__property_def__[3], None)

    def get_extra_action(self):
        return getattr(self, self.__property_def__[4], None)

    def get_extra_action_target_code(self):
        return getattr(self, self.__property_def__[5], None)

    def get_rule_desc(self):
        return getattr(self, self.__property_def__[6], None)

    def set_user_id(self, userid):
        return self.set_single_attribute(0, userid)

    def set_group_id(self, gid):
        return self.set_single_attribute(1, gid)
        
    def set_column_id(self, colid):
        return self.set_single_attribute(2, colid)
        
    def set_mapped_column_type(self, col_code):
        return self.set_single_attribute(3, col_code)
        
    def set_extra_action(self, eaction):
        return self.set_single_attribute(4, eaction)
        
    def set_extra_action_target_code(self, etarget):
        return self.set_single_attribute(5, etarget)
        
    def get_rule_desc(self, rule_str):
        return self.set_single_attribute(6, rule_str)
        
    def copy(self):
        return ImportMappingRule(self.get_dict())

    def is_valid(self):
        from ..Error.ValidationError import ValidationError

        gid, col_id, col_code = [self.get_group_id(), self.get_column_id(), self.get_mapped_column_type()]
        err_msg = ""
        if not gid or gid.isspace(): err_msg = err_msg + '- Group ID cannot be empty\n'
        if not col_id or col_id.isspace(): err_msg = err_msg + '- Column ID cannot be empty\n'
        if not col_code or col_code.isspace(): err_msg = err_msg + '- Data column cannot be empty\n'
        if not err_msg:
            return True
        else:
            self.set_exception(ValidationError(err_msg))
            return False
