import anvil.server
import anvil.users
from .Logger import ClientLogger

class Validator:
    """
A Validator instance performs form validation. You give it
a set of components, and for each component you specify
a checking function (a predicate), and optionally an error
label that will be shown if the component is *not* valid.

It will show error labels when the component is not valid

Add components to it with the require() method. Eg:

  validator.require(self.text_box_1, ['change', 'lost_focus'],
                    lambda tb: tb.text != '',
                    self.error_lbl_1)
                    
It also has some utility functions for common requirements
such as "this text box must have text in it", or
"this checkbox must be checked".

Use the enable_when_valid() method to provide a component
that will be enabled (via its `enable` property) only when
all requirements are met. Or just use the is_valid() method
to check the status of the form.

  validator.enable_when_valid(self.submit_button)

    """
    def __init__(self):
        self._validity = {}
        self._actions = []
        self._component_checks = []
        self._colours = []
        
    def require(self, component, event_list, predicate, error_lbl=None, show_errors_immediately=False, dependent=None):
        def check_this_component(**e):
            result = predicate(component, dependent) if dependent else predicate(component)
            # logger.trace(f"component.text=", component.text)
            # logger.trace(f"predicate(component)=", predicate(component))
            self._validity[component] = result
            if error_lbl is not None:
                error_lbl.visible = not result
            self._check()
        
        for e in event_list:
            # component.set_event_handler(e, check_this_component)
            component.add_event_handler(e, check_this_component)
        self._component_checks.append(check_this_component)
    
        if show_errors_immediately:
            check_this_component()
        else:
            # By default, won't show the error until the event triggers,
            # but we will (eg) disable buttons
            if error_lbl is not None:
                error_lbl.visible = False
            self._validity[component] = predicate(component, dependent) if dependent else predicate(component)
            self._check()
    
    def require_text_field(self, text_box, error_lbl=None, show_errors_immediately=False):
        self.require(text_box, ['change', 'lost_focus'],
                    lambda tb: tb.text not in ('', None),
                    error_lbl, show_errors_immediately)
            
    def require_date_field(self, date_field, error_lbl=None, show_errors_immediately=False):
        self.require(date_field, ['change'],
                    lambda df: df.date not in ('', None),
                    error_lbl, show_errors_immediately)
            
    def require_checked(self, check_box, error_lbl=None, show_errors_immediately=False):
        self.require(check_box, ['change'],
                    lambda cb: cb.checked,
                    error_lbl, show_errors_immediately)
        
    def require_selected(self, dropdown_box, error_lbl=None, show_errors_immediately=False):
        self.require(dropdown_box, ['change'],
                    lambda dd: dd.selected_value not in ('', None),
                    error_lbl, show_errors_immediately)

    def require_selected_dependent_on_checkbox(self, dropdown_box, check_box, error_lbl=None, show_errors_immediately=False):
        self.require(dropdown_box, ['change'],
                    lambda dd, cb: (cb.checked and dd.selected_value not in ('', None)) or not cb.checked,
                    error_lbl, show_errors_immediately, check_box)
    
    def require_selected_dependent_on_dropdown(self, dropdown_box, dropdown_box_dep, dep_key, error_lbl=None, show_errors_immediately=False):
        self.require(dropdown_box, ['change'],
                    lambda dd, dd_dep: (dd_dep.selected_value == dep_key and dd.selected_value not in ('', None)) or dd_dep.selected_value != dep_key,
                    error_lbl, show_errors_immediately, dropdown_box_dep)
    
    def enable_when_valid(self, component):
        def on_change(is_valid):
            component.enabled = is_valid
        self._actions.append(on_change)
        self._check()
    
    """For displaying an 'Error Summary' whenever the form is invalid with one or more errors"""
    def display_when_invalid(self, component):
        def on_change(is_valid):
            component.visible = not is_valid
        self._actions.append(on_change)
        self._check()

    """To highlight the error field(s)"""
    def highlight_when_invalid(self, component, errcolour, okcolour):
        def on_change(is_valid):
            component.background = errcolour if not is_valid else okcolour
        self._colours.append(on_change)
        self._check()
        
    def is_valid(self):
        """Return True if this form is valid, False if it's not"""
        return all(self._validity.values())
    
    def show_all_errors(self):
        """Show all error labels, even if the """
        for check_component in self._component_checks:
            check_component()
        
    def _check(self):
        v = self.is_valid()
        for f in self._actions:
            f(v)
        for f in self._colours:
            f(v)