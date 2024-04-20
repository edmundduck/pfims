import anvil.server
import pytest
from ..DataAccess import FileImportMappingDAModule
from ..Entities.ImportMappingGroup import ImportMappingGroup
from ..Entities.ImportMappingRule import ImportMappingRule
from ..Entities.TestModule import TestModule
from ..Utils import MockUpData

# This is a server module. It runs on the Anvil server,
# rather than in the user's browser.

class TestFileImportMappingDAModule(TestModule):
    def test_generate_mapping_list(self):
        err = ["Retrieved mapping list is expected to be either list or tuple only."]
        try:
            assert isinstance(FileImportMappingDAModule.generate_mapping_list(MockUpData.get_mockup_filetype()), (list, tuple)), err[0]
        except AssertionError:
            return err[0]

    def test_generate_mapping_type_list(self):
        err = ["Retrieved mapping type list is expected to be either list or tuple only."]
        try:
            assert isinstance(FileImportMappingDAModule.generate_mapping_type_list(), (list, tuple)), err[0]
        except AssertionError:
            return err[0]

    def test_generate_expense_tbl_def_list(self):
        err = ["Retrieved expense table definition list is expected to be either list or tuple only."]
        try:
            assert isinstance(FileImportMappingDAModule.generate_expense_tbl_def_list(), (list, tuple)), err[0]
        except AssertionError:
            return err[0]

    def test_generate_generate_upload_action_list(self):
        err = ["Retrieved upload action list is expected to be either list or tuple only."]
        try:
            assert isinstance(FileImportMappingDAModule.generate_upload_action_list(), (list, tuple)), err[0]
        except AssertionError:
            return err[0]

    def test_select_mapping_rules(self):
        err = [
            "Retrieved mapping rules from database are not the same as expected."
        ]
        mock_mapping_grp_rules = MockUpData.get_first_element(MockUpData.get_mockup_mapping_groups)()
        db_mapping_grp_rules = FileImportMappingDAModule.select_mapping_rules(mock_mapping_grp_rules["id"])
        mock_mapping_grp_rules['rule'] = MockUpData.convert_mapping_rules_list(MockUpData.get_mockup_mapping_rules)()
        try:
            # Should mock_mapping_grp_rules be in list by default, or db_mapping_grp_rules be removed from list?
            assert [mock_mapping_grp_rules] == db_mapping_grp_rules, err[0]
        except AssertionError:
            return err[0]

    def test_select_mapping_matrix(self):
        err = [
            "Retrieved mapping matrix from database are not the same as expected."
        ]
        mock_mapping_grp = MockUpData.get_first_element(MockUpData.get_mockup_mapping_groups)()
        db_mapping_matrix = FileImportMappingDAModule.select_mapping_matrix(mock_mapping_grp["id"])
        mock_mapping_matrix = MockUpData.get_mockup_mapping_matrix()
        try:
            assert mock_mapping_matrix == db_mapping_matrix, err[0]
        except AssertionError:
            return err[0]

    def test_select_mapping_extra_actions(self):
        err = [
            "Retrieved mapping extra actions from database are not the same as expected."
        ]
        mock_mapping_grp = MockUpData.get_first_element(MockUpData.get_mockup_mapping_groups)()
        db_mapping_extra_actions = FileImportMappingDAModule.select_mapping_extra_actions(mock_mapping_grp["id"])
        mock_mapping_extra_actions = MockUpData.get_mockup_mapping_extra_actions()
        try:
            assert mock_mapping_extra_actions == db_mapping_extra_actions, err[0]
        except AssertionError:
            return err[0]

    def test_save_mapping_group_create_delete(self):
        err = [
            "Created mapping group returned from database does not match the originally defined attributes.", 
            "Created mapping group remains in database after deletion.",
            "Fail to delete the created mapping group."
        ]
        # Current BaseEntity.set(data) cannot accept a data param as list with dict inside.
        new_mock_mapping_grp = ImportMappingGroup(MockUpData.get_new_mockup_mapping_groups()[0])
        id = FileImportMappingDAModule.save_mapping_group(new_mock_mapping_grp)
        new_mock_mapping_grp = new_mock_mapping_grp.set_id(id)
        new_db_mapping_grp = ImportMappingGroup(FileImportMappingDAModule.select_mapping_rules(id)[0])
        try:
            assert new_db_mapping_grp == new_mock_mapping_grp, err[0]
        except AssertionError:
            return err[0]
        result = FileImportMappingDAModule.delete_mapping(id)
        if result and result > 0:
            try:
                assert not bool(FileImportMappingDAModule.select_mapping_rules(id)), err[1]
            except AssertionError:
                return err[1]
        else:
            return err[2]

    def test_save_mapping_group_update(self):
        err = [
            "Updated mapping group returned from database does not match the originally defined attributes."
        ]
        mock_mapping_grp = ImportMappingGroup(MockUpData.get_first_element(MockUpData.get_mockup_mapping_groups)())
        mock_mapping_grp.set_name("New Unit Test Mapping Group")
        id = FileImportMappingDAModule.save_mapping_group(mock_mapping_grp)
        db_mapping_grp = ImportMappingGroup(FileImportMappingDAModule.select_mapping_rules(id)[0])
        try:
            assert db_mapping_grp == mock_mapping_grp, err[0]
        except AssertionError:
            return err[0]
        mock_mapping_grp.set_name("Unit Test Mapping Group")
        FileImportMappingDAModule.save_mapping_group(mock_mapping_grp)

    # def test_save_mapping_rules_n_matrix(self):
    #     err = [
    #         "Saved mapping matrix returned from database does not match the originally defined attributes."
    #     ]
    #     mock_mapping_grp = ImportMappingGroup(MockUpData.get_first_element(MockUpData.get_mockup_mapping_groups)())
    #     mock_mapping_grp = mock_mapping_grp.set_mapping_rules([ImportMappingRule(mr) for mr in MockUpData.get_new_mockup_mapping_rules()])
    #     # mock_mapping_grp['rules'] = MockUpData.convert_mapping_rules_list(MockUpData.get_new_mockup_mapping_rules)()
    #     FileImportMappingDAModule.save_mapping_rules_n_matrix(mock_mapping_grp, MockUpData.get_mockup_mapping_matrix_mogstr(), None)
    #     db_mapping_grp_rules = FileImportMappingDAModule.select_mapping_rules(mock_mapping_grp.get_id())
    #     try:
    #         assert db_mapping_grp_rules == [mock_mapping_grp], err[0]
    #     except AssertionError:
    #         return err[0]
