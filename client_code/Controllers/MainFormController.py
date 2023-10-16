import anvil.server
import anvil.users

# This is a module.
# You can define variables and functions here, and use them from any form. For example, in a top-level form:

def switch_role(role):
    from ..Utils.Constants import LinkRole
    if role == LinkRole.UNSELECTED:
        role = LinkRole.SELECTED
    else:
        role = LinkRole.UNSELECTED
    return role