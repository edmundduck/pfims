from ._anvil_designer import LabelMaintFormTemplate
from anvil import *
import anvil.server
from ....Controllers import LabelMaintController
from ....Utils.ButtonModerator import ButtonModerator
from ....Utils.ClientCache import ClientCache
from ....Utils import Constants as const
from ....Utils.Logger import ClientLogger

logger = ClientLogger()
btnmod = ButtonModerator()

class LabelMaintForm(LabelMaintFormTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        # Any code you write here will run before the form opens.
        # TODO - Enable after Move to logic is implemented
        self.button_labels_move.enabled = False
        self.dropdown_lbl_list.items = LabelMaintController.generate_labels_dropdown()
        self.dropdown_lbl_list.selected_value = None
        self.dropdown_moveto.items = LabelMaintController.generate_labels_dropdown()
        self.dropdown_moveto.selected_value = None
        self.button_labels_update.enabled = LabelMaintController.enable_label_update_button(self.dropdown_lbl_list.selected_value)
        self.button_labels_delete.enabled = LabelMaintController.enable_label_delete_button(self.dropdown_lbl_list.selected_value)

    def button_exp_input_click(self, **event_args):
        """This method is called when the button is clicked"""
        from ....Utils import Routing
        Routing.open_exp_input_form(self)

    @logger.log_function
    def dropdown_lbl_list_change(self, **event_args):
        """This method is called when an item is selected"""
        lbl_id, lbl_name = self.dropdown_lbl_list.selected_value if self.dropdown_lbl_list.selected_value is not None else [None, None]
        self.hidden_lbl_id.text, \
        self.text_lbl_name.text, \
        self.text_keywords.text, \
        self.dropdown_status.selected_value = anvil.server.call('get_selected_label_attr', lbl_id)
        self.button_labels_update.enabled = LabelMaintController.enable_label_update_button(self.dropdown_lbl_list.selected_value)
        self.button_labels_delete.enabled = LabelMaintController.enable_label_delete_button(self.dropdown_lbl_list.selected_value)

    def dropdown_status_show(self, **event_args):
        """This method is called when the DropDown is shown on the screen"""
        self.dropdown_status.items = [('Active', True), ('Inactive', False)]
        self.dropdown_status.selected_value = True

    @btnmod.one_click_only
    @logger.log_function
    def button_labels_create_click(self, **event_args):
        """This method is called when the button is clicked"""
        lbl_name = self.text_lbl_name.text
        lbl_id = anvil.server.call('create_label', labels=[{'name':lbl_name, 'keywords':self.text_keywords.text, 'status':True}])

        if lbl_id is None:
            msg = f"ERROR: Fail to create label {lbl_name}."
            logger.error(msg)
        elif len(lbl_id) == 0:
            msg = f"INFO: No label has been created."
            logger.info(msg)
        else:
            """ Reflect the change in labels dropdown """
            self.dropdown_lbl_list.items = LabelMaintController.generate_labels_dropdown(reload=True)
            logger.debug("self.dropdown_lbl_list.items=", self.dropdown_lbl_list.items)
            logger.debug("lbl_id=", lbl_id)
            self.dropdown_lbl_list.selected_value = [lbl_id[0], lbl_name]
            self.dropdown_moveto.items = self.dropdown_lbl_list.items
            self.button_labels_update.enabled = LabelMaintController.enable_label_update_button(self.dropdown_lbl_list.selected_value)
            self.button_labels_delete.enabled = LabelMaintController.enable_label_delete_button(self.dropdown_lbl_list.selected_value)
            msg = f"Label {lbl_name} has been created successfully."
            logger.info(msg)
        Notification(msg).show()
        return

    @btnmod.one_click_only
    @logger.log_function
    def button_labels_update_click(self, **event_args):
        """This method is called when the button is clicked"""
        lbl_id, lbl_name = self.dropdown_lbl_list.selected_value if self.dropdown_lbl_list.selected_value is not None else [None, None]
        # lbl_name retrieved should be replaced by text field value
        lbl_name = self.text_lbl_name.text
        result = anvil.server.call('update_label', lbl_id, lbl_name, self.text_keywords.text, self.dropdown_status.selected_value)

        if result is None or result <= 0:
            msg = f"ERROR: Fail to update label {lbl_name}."
            logger.error(msg)
        else:
            """ Reflect the change in labels dropdown """
            self.dropdown_lbl_list.items = LabelMaintController.generate_labels_dropdown(reload=True)
            self.dropdown_lbl_list.selected_value = [lbl_id, lbl_name]
            msg = f"Label {lbl_name} has been updated successfully."
            logger.info(msg)
        Notification(msg).show()
        return

    @btnmod.one_click_only
    @logger.log_function
    def button_labels_move_click(self, **event_args):
        """This method is called when the button is clicked"""
        pass

    @btnmod.one_click_only
    @logger.log_function
    def button_labels_delete_click(self, **event_args):
        """This method is called when the button is clicked"""
        selected_lbl_id, selected_lbl_name = self.dropdown_lbl_list.selected_value if self.dropdown_lbl_list.selected_value is not None else [None, None]
        confirm = Label(text="Proceed label <{lbl_name}> ({lbl_id}) deletion by clicking DELETE.".format(lbl_name=selected_lbl_name, lbl_id=selected_lbl_id))
        userconf = alert(content=confirm,
                        title=f"Alert - Label Deletion",
                        buttons=[("DELETE", const.Alerts.CONFIRM), ("CANCEL", const.Alerts.CANCEL)])

        if userconf == const.Alerts.CONFIRM:
            result = anvil.server.call('delete_label', selected_lbl_id)
            if result is not None and result > 0:
                """ Reflect the change in label dropdown """
                self.dropdown_lbl_list.items = LabelMaintController.generate_labels_dropdown(reload=True)
                self.clear()
                msg = f"Label {selected_lbl_name} has been deleted."
                logger.info(msg)
                Notification(msg).show()
                return btnmod.override_end_state(False)
            else:
                msg = f"ERROR: Fail to delete label {selected_lbl_name}."
                logger.error(msg)
                Notification(msg).show()

    def clear(self, **event_args):
        self.dropdown_lbl_list.selected_value = None
        self.dropdown_status.selected_value = True
        self.dropdown_moveto.selected_value = None
        self.button_labels_update.enabled = None
        self.button_labels_delete.enabled = None
        self.text_lbl_name.text = None
        self.text_keywords.text = None
