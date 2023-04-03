from ._anvil_designer import LabelMaintFormTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from ... import Routing

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
        self.dropdown_lbl_list.items = anvil.server.call('generate_labels_dropdown')
        self.dropdown_lbl_list.selected_value = None

    def dropdown_moveto_show(self, **event_args):
        """This method is called when the DropDown is shown on the screen"""
        self.dropdown_moveto.items = anvil.server.call('generate_labels_dropdown')
        self.dropdown_moveto.selected_value = None
        # TODO - Enable after Move to logic is implemented
        self.dropdown_moveto.enabled = False

    def dropdown_lbl_list_change(self, **event_args):
        """This method is called when an item is selected"""
        self.hidden_lbl_id.text, \
        self.text_lbl_name.text, \
        self.text_keywords.text, \
        self.dropdown_status.selected_value = anvil.server.call('get_selected_label_attr', self.dropdown_lbl_list.selected_value[0])

    def dropdown_status_show(self, **event_args):
        """This method is called when the DropDown is shown on the screen"""
        self.dropdown_status.items = [('Active', True), ('Inactive', False)]
        self.dropdown_status.selected_value = True

    def button_labels_create_click(self, **event_args):
        """This method is called when the button is clicked"""
        lbl_id = anvil.server.call('create_label',
                                    name=self.text_lbl_name.text,
                                    keywords=self.text_keywords.text,
                                    status=True
                                )

        if lbl_id is None or lbl_id <= 0:
            n = Notification("ERROR: Fail to create label {lbl_name}.".format(lbl_name=self.text_lbl_name.text))
        else:
            """ Reflect the change in labels dropdown """
            self.dropdown_lbl_list.items = anvil.server.call('generate_labels_dropdown')
            self.dropdown_lbl_list.selected_value = [lbl_id, self.text_lbl_name.text]
            self.dropdown_moveto.items = self.dropdown_lbl_list.items
            n = Notification("Label {lbl_name} has been created successfully.".format(lbl_name=self.text_lbl_name.text))
        n.show()
        return

    def button_labels_update_click(self, **event_args):
        """This method is called when the button is clicked"""
        result = anvil.server.call('update_label',
                                   id=self.hidden_lbl_id.text,
                                   name=self.text_lbl_name.text,
                                   keywords=self.text_keywords.text,
                                   status=self.dropdown_status.selected_value
                                )

        if result is None or result <= 0:
            n = Notification("ERROR: Fail to update label {lbl_name}.".format(lbl_name=self.text_lbl_name.text))
        else:
            """ Reflect the change in labels dropdown """
            self.dropdown_lbl_list.items = anvil.server.call('generate_labels_dropdown')
            self.dropdown_lbl_list.selected_value = self.hidden_lbl_id.text
            n = Notification("Label {lbl_name} has been updated successfully.".format(lbl_name=self.text_lbl_name.text))
        n.show()
        return

    def button_labels_move_click(self, **event_args):
        """This method is called when the button is clicked"""
        pass

    def button_labels_delete_click(self, **event_args):
        """This method is called when the button is clicked"""
        # TODO
        selected_lbl_id, selected_lbl_name = self.dropdown_lbl_list.selected_value
        msg = Label(text="Proceed label <{lbl_name}> ({lbl_id}) deletion by clicking DELETE.".format(lbl_name=selected_lbl_name, lbl_id=selected_lbl_id))
        userconf = alert(content=msg,
                        title=f"Alert - Label Deletion",
                        buttons=[
                        ("DELETE", "Y"),
                        ("CANCEL", "N")
                        ])

        if userconf == "Y":
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
