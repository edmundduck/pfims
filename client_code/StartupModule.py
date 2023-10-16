import anvil.server
import anvil.users

# This is a module.
# You can define variables and functions here, and use them from any form. For example, in a top-level form:

def startup():
    user_data = anvil.server.call('get_current_username')
  if user_data is None:
    open_form('LoginForm')
  else:
    _globals.active, _globals.clients, _globals.projects, _globals.project_rows, \
    _globals.tags, _globals.time_trackers, _globals.user = user_data
    open_form('MainForm')

if __name__ == "__main__":
    startup()