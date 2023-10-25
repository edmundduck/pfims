from ._anvil_designer import UserSettingFormTemplate
from anvil import *
import anvil.server
import anvil.users
from ....Controllers import UserSettingController
from ....Utils.ButtonModerator import ButtonModerator
from ....Utils.Logger import ClientLogger

logger = ClientLogger()
btnmod = ButtonModerator()

class UserSettingForm(UserSettingFormTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)
        
        # Any code you write here will run when the form opens.
        from .... import Global
        brokers, search_interval, ccy, submitted_group_list = UserSettingController.initialize_data()
        self.dropdown_default_broker.items = UserSettingController.generate_brokers_dropdown(data=brokers)
        self.dropdown_broker_list.items = UserSettingController.generate_brokers_dropdown(data=brokers)
        self.dropdown_logging_level.items = UserSettingController.generate_logging_level_dropdown()
        self.dropdown_interval.items = UserSettingController.generate_search_interval_dropdown(data=search_interval)
        self.dropdown_ccy.items = UserSettingController.generate_currency_dropdown(data=ccy)
        self.dropdown_sub_templ_list.items = UserSettingController.generate_submitted_journal_groups_dropdown(data=submitted_group_list)
        self.dropdown_default_broker.selected_value = UserSettingController.get_broker_dropdown_selected_item(Global.settings.get_broker())
        self.dropdown_interval.selected_value = Global.settings.get_search_interval()
        self.time_datefrom.date = Global.settings.get_search_datefrom()
        self.time_dateto.date = Global.settings.get_search_dateto()
        self.dropdown_logging_level.selected_value = Global.settings.get_logging_level()

        self.time_datefrom.enabled, self.time_dateto.enabled = UserSettingController.enable_search_time_datefield(self.dropdown_interval.selected_value)
        self.button_broker_create.enabled = UserSettingController.enable_broker_create_button(self.text_broker_name.text)
        self.button_broker_update.enabled, self.button_broker_delete.enabled = UserSettingController.enable_broker_update_delete_button(self.dropdown_broker_list.selected_value)
        self.column_panel_logging.visible = UserSettingController.visible_logging_panel()
    
    def dropdown_interval_change(self, **event_args):
        """This method is called when an item is selected"""
        self.time_datefrom.enabled, self.time_dateto.enabled = UserSettingController.enable_search_time_datefield(self.dropdown_interval.selected_value)
        self.time_datefrom.date, self.time_dateto.date = UserSettingController.set_search_time_datefield_value(self.dropdown_interval.selected_value, self.time_datefrom.date, self.time_dateto.date)

    @btnmod.one_click_only
    @logger.log_function
    def button_submit_click(self, **event_args):
        """This method is called when the button is clicked"""
        try:
            UserSettingController.change_settings(
                self.dropdown_default_broker.selected_value, 
                self.dropdown_interval.selected_value, 
                self.time_datefrom.date, 
                self.time_dateto.date, 
                self.dropdown_logging_level.selected_value
            )
            n = Notification(f"Setting has been updated successfully.")
        except (Exception) as err:
            logger.error(err)
            n = Notification(f"ERROR occurs during setting update.")
        n.show()

    @btnmod.one_click_only
    @logger.log_function
    def button_broker_create_click(self, **event_args):
        """This method is called when the button is clicked"""
        try:
            broker_id = UserSettingController.change_broker(None, self.text_broker_name.text, self.dropdown_ccy.selected_value)
            self.dropdown_broker_list.items = UserSettingController.generate_brokers_dropdown()
            self.dropdown_default_broker.items = UserSettingController.generate_brokers_dropdown()
            self.dropdown_broker_list.selected_value = UserSettingController.get_broker_dropdown_selected_item(broker_id)
            self.dropdown_default_broker.selected_value = default_broker
            n = Notification(f"Broker {self.text_broker_name.text} has been created successfully.")
        except Exception as err:
            logger.error(err)
            n = Notification(f"ERROR occurs when creating broker {self.text_broker_name.text}.")
        n.show()

    def text_broker_name_lost_focus(self, **event_args):
        """This method is called when the TextBox loses focus"""
        self.button_broker_create.enabled = UserSettingController.enable_broker_create_button(self.text_broker_name.text)

    @btnmod.one_click_only
    @logger.log_function
    def button_broker_update_click(self, **event_args):
        """This method is called when the button is clicked"""
        try:
            default_broker = self.dropdown_default_broker.selected_value
            broker_id = self.dropdown_broker_list.selected_value[0]
            UserSettingController.change_broker(self.dropdown_broker_list.selected_value, self.text_broker_name.text, self.dropdown_ccy.selected_value)
            self.dropdown_broker_list.items = UserSettingController.generate_brokers_dropdown()
            self.dropdown_default_broker.items = UserSettingController.generate_brokers_dropdown()
            self.dropdown_broker_list.selected_value = (broker_id, self.text_broker_name.text, self.dropdown_ccy.selected_value)
            self.dropdown_default_broker.selected_value = default_broker
            n = Notification(f"Broker {self.text_broker_name.text} has been updated successfully.")
        except Exception as err:
            logger.error(err)
            n = Notification(f"ERROR occurs when updating broker {self.text_broker_name.text}.")
        n.show()

    @btnmod.one_click_only
    @logger.log_function
    def button_broker_delete_click(self, **event_args):
        """This method is called when the button is clicked"""
        try:
            count = UserSettingController.delete_broker(self.dropdown_broker_list.selected_value)
            self.dropdown_broker_list.items = UserSettingController.generate_brokers_dropdown()
            self.dropdown_default_broker.items = UserSettingController.generate_brokers_dropdown()
            n = Notification(f"Broker {self.text_broker_name.text} has been deleted successfully.")
        except Exception as err:
            logger.error(err)
            n = Notification(f"ERROR occurs when deleting broker {self.text_broker_name.text}.")
        n.show()

    def dropdown_broker_list_change(self, **event_args):
        """This method is called when an item is selected"""
        _, self.text_broker_name.text, self.dropdown_ccy.selected_value = UserSettingController.set_selected_broker_fields(self.dropdown_broker_list.selected_value)
        self.button_broker_create.enabled = UserSettingController.enable_broker_create_button(self.text_broker_name.text)
        self.button_broker_update.enabled, self.button_broker_delete.enabled = UserSettingController.enable_broker_update_delete_button(self.dropdown_broker_list.selected_value)
  
    @btnmod.one_click_only
    @logger.log_function
    def button_jrn_grp_edit_click(self, **event_args):
        """This method is called when the button is clicked"""
        try:
            result = UserSettingController.submit_journal_group(self.dropdown_sub_templ_list.selected_value)
            self.dropdown_sub_templ_list.items = UserSettingController.generate_submitted_journal_groups_dropdown()
            n = Notification(f"Journal group has been re-enabled for modification successfully.")
        except Exception as err:
            logger.error(err)
            n = Notification(f"ERROR occurs when submitting journal group.")
        n.show()

