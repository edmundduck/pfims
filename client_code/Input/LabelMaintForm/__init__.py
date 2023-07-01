from ._anvil_designer import LabelMaintFormTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from ...App import Routing
from ...App import Caching as cache

class LabelMaintForm(LabelMaintFormTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        # Any code you write here will run before the form opens.
        # TODO - Enable after Move to logic is implemented
        self.button_labels_move.enabled = False

    def button_exp_input_click(self, **event_args):
        """This method is called when the button is clicked"""
        Routing.open_exp_input_form(self)

    def dropdown_lbl_list_show(self, **event_args):
        """This method is called when the DropDown is shown on the screen"""
        self.dropdown_lbl_list.items = cache.get_caching_labels_dropdown()
        self.dropdown_lbl_list.selected_value = None
        self.button_labels_update.enabled = False if self.dropdown_lbl_list.selected_value in ('', None) else True
        self.button_labels_delete.enabled = False if self.dropdown_lbl_list.selected_value in ('', None) else True

    def dropdown_moveto_show(self, **event_args):
        """This method is called when the DropDown is shown on the screen"""
        self.dropdown_moveto.items = cache.get_caching_labels_dropdown()
        self.dropdown_moveto.selected_value = None
        # TODO - Enable after Move to logic is implemented
        self.dropdown_moveto.enabled = False

    def dropdown_lbl_list_change(self, **event_args):
        """This method is called when an item is selected"""
        # Case 001 - string dict key handling review
        # lbl_id, lbl_name = self.dropdown_lbl_list.selected_value.values() if self.dropdown_lbl_list.selected_value is not None else [None, None]
        lbl_id, lbl_name = eval(self.dropdown_lbl_list.selected_value).values() if self.dropdown_lbl_list.selected_value is not None else [None, None]
        self.hidden_lbl_id.text, \
        self.text_lbl_name.text, \
        self.text_keywords.text, \
        self.dropdown_status.selected_value = anvil.server.call('get_selected_label_attr', lbl_id)
        # Case 001 - string dict key handling review
        # self.button_labels_update.enabled = False if self.dropdown_lbl_list.selected_value in ('', None) else True
        # self.button_labels_delete.enabled = False if self.dropdown_lbl_list.selected_value in ('', None) else True
        self.button_labels_update.enabled = False if eval(self.dropdown_lbl_list.selected_value) in ('', None) else True
        self.button_labels_delete.enabled = False if eval(self.dropdown_lbl_list.selected_value) in ('', None) else True

    def dropdown_status_show(self, **event_args):
        """This method is called when the DropDown is shown on the screen"""
        self.dropdown_status.items = [('Active', True), ('Inactive', False)]
        self.dropdown_status.selected_value = True

    def button_labels_create_click(self, **event_args):
        """This method is called when the button is clicked"""
        lbl_name = self.text_lbl_name.text
        lbl_id = anvil.server.call('create_label', labels={'name':lbl_name, 'keywords':self.text_keywords.text, 'status':True})

        if lbl_id is None or lbl_id[0] <= 0:
            n = Notification("ERROR: Fail to create label {lbl_name}.".format(lbl_name=lbl_name))
        else:
            """ Reflect the change in labels dropdown """
            cache.reset_caching_labels()
            self.dropdown_lbl_list.items = cache.get_caching_labels_dropdown()
            # Case 001 - string dict key handling review
            # self.dropdown_lbl_list.selected_value = {"id": lbl_id, "text": lbl_name}
            self.dropdown_lbl_list.selected_value = repr({"id": lbl_id, "text": lbl_name})
            self.dropdown_moveto.items = self.dropdown_lbl_list.items
            self.button_labels_update.enabled = True
            n = Notification("Label {lbl_name} has been created successfully.".format(lbl_name=lbl_name))
        n.show()
        return

    def button_labels_update_click(self, **event_args):
        """This method is called when the button is clicked"""
        # Case 001 - string dict key handling review
        # lbl_id, lbl_name = self.dropdown_lbl_list.selected_value.values() if self.dropdown_lbl_list.selected_value is not None else [None, None]
        lbl_id, lbl_name = eval(self.dropdown_lbl_list.selected_value).values() if self.dropdown_lbl_list.selected_value is not None else [None, None]
        # lbl_name retrieved should be replaced by text field value
        lbl_name = self.text_lbl_name.text
        result = anvil.server.call('update_label',
                                   id=lbl_id,
                                   name=lbl_name,
                                   keywords=self.text_keywords.text,
                                   status=self.dropdown_status.selected_value
                                )

        if result is None or result <= 0:
            n = Notification("ERROR: Fail to update label {lbl_name}.".format(lbl_name=lbl_name))
        else:
            """ Reflect the change in labels dropdown """
            cache.reset_caching_labels()
            self.dropdown_lbl_list.items = cache.get_caching_labels_dropdown()
            # Case 001 - string dict key handling review
            # self.dropdown_lbl_list.selected_value = {"id": lbl_id, "text": lbl_name}
            self.dropdown_lbl_list.selected_value = repr({"id": lbl_id, "text": lbl_name})
            n = Notification("Label {lbl_name} has been updated successfully.".format(lbl_name=lbl_name))
        n.show()
        return

    def button_labels_move_click(self, **event_args):
        """This method is called when the button is clicked"""
        pass

    def button_labels_delete_click(self, **event_args):
        """This method is called when the button is clicked"""
        # Case 001 - string dict key handling review
        # selected_lbl_id, selected_lbl_name = self.dropdown_lbl_list.selected_value.values() if self.dropdown_lbl_list.selected_value is not None else [None, None]
        selected_lbl_id, selected_lbl_name = eval(self.dropdown_lbl_list.selected_value).values() if self.dropdown_lbl_list.selected_value is not None else [None, None]
        msg = Label(text="Proceed label <{lbl_name}> ({lbl_id}) deletion by clicking DELETE.".format(lbl_name=selected_lbl_name, lbl_id=selected_lbl_id))
        userconf = alert(content=msg,
                        title=f"Alert - Label Deletion",
                        buttons=[
                        ("DELETE", "Y"),
                        ("CANCEL", "N")
                        ])

        if userconf == "Y":
            cache.reset_caching_labels()
            result = anvil.server.call('delete_label', selected_lbl_id)
            if result is not None and result > 0:
                """ Reflect the change in label dropdown """
                self.clear()

                n = Notification("Label {lbl_name} has been deleted.".format(lbl_name=selected_lbl_name))
            else:
                n = Notification("ERROR: Fail to delete label {lbl_name}.".format(lbl_name=selected_lbl_name))
            n.show()

    def clear(self, **event_args):
        self.dropdown_lbl_list_show()
        self.dropdown_status.selected_value = True
        self.dropdown_moveto.selected_value = None
        self.text_lbl_name.text = None
        self.text_keywords.text = None
