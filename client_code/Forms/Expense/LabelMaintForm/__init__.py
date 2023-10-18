from ._anvil_designer import LabelMaintFormTemplate
from anvil import *
import anvil.server
from ....Controllers import LabelMaintController
from ....Utils.ButtonModerator import ButtonModerator
from ....Utils.ClientCache import ClientCache
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
        lbl_id, _ = self.dropdown_lbl_list.selected_value if self.dropdown_lbl_list.selected_value is not None else [None, None]
        self.text_lbl_name.text = LabelMaintController.get_label_name(self.dropdown_lbl_list.selected_value)
        self.text_keywords.text = LabelMaintController.get_label_keywords(self.dropdown_lbl_list.selected_value)
        self.dropdown_status.selected_value = LabelMaintController.get_label_status(self.dropdown_lbl_list.selected_value)
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
        try:
            label = LabelMaintController.create_label(
                self.text_lbl_name.text,
                self.text_keywords.text,
                self.dropdown_status.selected_value
            )
            logger.debug("lbl_id=", label.get_id())
            """ Reflect the change in labels dropdown """
            self.dropdown_lbl_list.items = LabelMaintController.generate_labels_dropdown(reload=True)
            self.dropdown_lbl_list.selected_value = LabelMaintController.get_label_dropdown_selected_item(label.get_id())
            self.dropdown_moveto.items = self.dropdown_lbl_list.items
            self.button_labels_update.enabled = LabelMaintController.enable_label_update_button(self.dropdown_lbl_list.selected_value)
            self.button_labels_delete.enabled = LabelMaintController.enable_label_delete_button(self.dropdown_lbl_list.selected_value)
            msg = f"Label {label.get_name()} ({label.get_id()}) has been created successfully."
            logger.info(msg)
        except Exception as err:
            logger.error(err)
            msg = f"ERROR occurs when creating label {self.text_lbl_name.text}."
        Notification(msg).show()

    @btnmod.one_click_only
    @logger.log_function
    def button_labels_update_click(self, **event_args):
        """This method is called when the button is clicked"""
        try:
            label = LabelMaintController.create_label(
                self.dropdown_lbl_list.selected_value,
                self.text_lbl_name.text,
                self.text_keywords.text,
                self.dropdown_status.selected_value
            )
            """ Reflect the change in labels dropdown """
            self.dropdown_lbl_list.items = LabelMaintController.generate_labels_dropdown(reload=True)
            self.dropdown_lbl_list.selected_value = [label.get_id(), label.get_name()]
            msg = f"Label {label.get_name()} ({label.get_id()}) has been updated successfully."
            logger.info(msg)
        except Exception as err:
            logger.error(err)
            msg = f"ERROR occurs when updating account {self.text_lbl_name.text}."
        Notification(msg).show()

    @btnmod.one_click_only
    @logger.log_function
    def button_labels_move_click(self, **event_args):
        """This method is called when the button is clicked"""
        pass

    @btnmod.one_click_only
    @logger.log_function
    def button_labels_delete_click(self, **event_args):
        """This method is called when the button is clicked"""
        from ....Utils.Constants import Alerts
        lbl_id, lbl_name = self.dropdown_lbl_list.selected_value if self.dropdown_lbl_list.selected_value is not None else [None, None]
        confirm = Label(text="Proceed label [{lbl_name}] deletion by clicking PROCEED.".format(lbl_name=lbl_name))
        userconf = alert(content=confirm, title='Alert - Confirm to delete label', buttons=[('PROCEED', Alerts.CONFIRM), ('CANCEL', Alerts.CANCEL)])

        if userconf == const.Alerts.CONFIRM:
            try:
                result = AccountMaintController.delete_account(self.dropdown_lbl_list.selected_value)
                """ Reflect the change in label dropdown """
                self.dropdown_lbl_list.items = LabelMaintController.generate_labels_dropdown(reload=True)
                self.clear()
                msg = f"Label {lbl_name} ({lbl_id}) has been deleted."
                logger.info(msg)
                Notification(msg).show()
                return btnmod.override_end_state(False)
            except Exception as err:
                logger.error(err)
                msg = f"ERROR: Fail to delete label {lbl_name}."
                Notification(msg).show()

    def clear(self, **event_args):
        self.dropdown_lbl_list.selected_value = None
        self.dropdown_status.selected_value = True
        self.dropdown_moveto.selected_value = None
        self.button_labels_update.enabled = None
        self.button_labels_delete.enabled = None
        self.text_lbl_name.text = None
        self.text_keywords.text = None
