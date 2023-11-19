import anvil.server
# This is a module.
# You can define variables and functions here, and use them from any form. For example, in a top-level form:

class ButtonModerator:

    OVERRIDE_KEY = 'one_click_only_override'
    
    def __init__(self):
        pass

    def one_click_only(self, func):
        """
        A decorator which disables the clicked button from 2nd click during the wrapped function execution. Return the original state ('enabled') after execution.

        The state after wrapped function execution can be overwritten by adding a dictionary with key='one_click_only_override'.

        Parameters:
            func (function): Wrapped function to execute before and after the button enabled state to change.

        Returns:
            result (object): Any data type which the wrapped function returns.
        """
        def wrapper(*args, **kwargs):
            btn_source, btn_source_state = [kwargs.get('sender', None), None]
            if btn_source is not None:
                btn_source_state = btn_source.enabled
                btn_source.enabled = False
            result = func(*args, **kwargs)
            if btn_source_state is not None:
                if isinstance(result, dict) and result.get(self.OVERRIDE_KEY, None) is not None:
                    btn_source.enabled = result.get(self.OVERRIDE_KEY)
                elif isinstance(result, (list, tuple)):
                    btn_source.enabled = btn_source_state
                    for r in result:
                        if isinstance(r, dict) and r.get(self.OVERRIDE_KEY, None):
                            btn_source.enabled = r.get(self.OVERRIDE_KEY)
                            continue
                else:
                    btn_source.enabled = btn_source_state
            return result
        return wrapper

    def override_end_state(self, state):
        """
        Provide a dictionary which contains override state. Add it in the wrapped function return for one_click_only function to handle.

        Parameters:
            state (boolean): The end state of the button, True for enabled, False for disabled.

        Returns:
            dict: A dictionary which contains the override key and value.
        """
        return { self.OVERRIDE_KEY: state }