import anvil.server
import anvil.users
from . import Global

# This is a module.
# You can define variables and functions here, and use them from any form. For example, in a top-level form:

def startup():
    user_data = anvil.server.call('get_user_data')
    if not user_data:
        open_form('LoginForm')
    else:
        Global.userid, Global.email, Global.role = user_data
        open_form('MainForm')

if __name__ == "__main__":
    startup()