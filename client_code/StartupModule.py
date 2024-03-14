import anvil.server
import anvil.users
from . import Global
from .Utils import Routing

# This is a module.
# You can define variables and functions here, and use them from any form. For example, in a top-level form:

def startup():
    user_data = anvil.server.call('get_user_data')
    if not user_data:
        Routing.open_general_front_form()
    else:
        Global.userid, Global.email, Global.role, Global.settings = user_data
        Routing.open_logged_on_main_form()

if __name__ == "__main__":
    startup()