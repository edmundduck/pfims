import anvil.server
from ..Utils.Constants import LinkRole

# This is a module.
# You can define variables and functions here, and use them from any form. For example, in a top-level form:

def visible_test_env_label():
    """
    Make the testing environment label visible or invisible.

    Returns:
        vis (boolean): True for testing environment, False otherwise.
    """
    return False if anvil.app.environment.name in 'Prod' else True

def visible_poc_link():
    """
    Make the POC (proof of concept) link visible or invisible.

    Returns:
        vis (boolean): True for testing environment, False otherwise.
    """
    return visible_test_env_label()

def visible_unittest_link():
    """
    Make the unit test link visible or invisible.

    Returns:
        vis (boolean): True for testing environment, False otherwise.
    """
    return visible_test_env_label()

def visible_group_links(role):
    """
    Make the group links visible or invisible.

    Returns:
        vis (boolean): True for visible, False otherwise.
    """
    if role == LinkRole.UNSELECTED:
        return False
    else:
        return True

def switch_role(role):
    """
    Return a different role to indicate a link status (clicked or unclicked) after clicking the link.

    Parameters:
        role (string): Role of the link before clicking.

    Returns:
        role (string): Role of the link after clicking.
    """
    if role == LinkRole.UNSELECTED:
        role = LinkRole.SELECTED
    else:
        role = LinkRole.UNSELECTED
    return role

def change_parent_section_icon(icon):
    """
    Return a parent section icon after clicking the link.

    Parameters:
        icon (string): Icon of the link before clicking.

    Returns:
        icon (string): Icon of the link after clicking.
    """
    from ..Utils.Constants import Icons
    return Icons.MENU_SHRINK if icon == Icons.MENU_EXPAND else Icons.MENU_EXPAND