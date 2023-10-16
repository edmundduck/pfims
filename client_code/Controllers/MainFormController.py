import anvil.users

# This is a module.
# You can define variables and functions here, and use them from any form. For example, in a top-level form:

def visible_test_env_label():
    """
    Return current environment name (testing or None for production).

    Returns:
        anvil.app.environment.name (string): Anvil testing environment name, None for production.
    """
    return anvil.app.environment.name if anvil.app.environment.name in 'Dev' else None

def switch_role(role):
    """
    Return a different role to indicate a link status (clicked or unclicked) after clicking the link.

    Parameters:
        role (string): Role of the link before clicking.

    Returns:
        role (string): Role of the link after clicking.
    """
    from ..Utils.Constants import LinkRole
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