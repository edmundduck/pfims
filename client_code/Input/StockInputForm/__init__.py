from ._anvil_designer import StockInputFormTemplate
from anvil import *
import anvil.users
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from datetime import date
from ... import glo
from ... import Global as glo
from ... import validation

class StockInputForm(StockInputFormTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)
    
        # Any code you write here will run when the form opens.
        self.input_repeating_panel.add_event_handler('x-save-change', self.save_row_change)
        self.input_repeating_panel.add_event_handler('x-disable-submit-button', self.disable_submit_button)

        # Initiate repeating panel items to an empty list otherwise will throw NoneType error
        self.input_repeating_panel.items = []
        self.input_selldate.date = date.today()
        self.templ_name.text, self.dropdown_broker.selected_value = anvil.server.call('get_selected_template_attr', self.dropdown_templ.selected_value)

        # Reset on screen change status
        glo.reset_input_stock_change()
        self.disable_submit_button()
        
    def save_row_change(self, **event_args):
        """ 
        *** ESSENTIAL ***
        Update child items from repeating panel to parent form items
        Refer to the following reference links for detail
        https://anvil.works/forum/t/is-it-possible-to-access-a-repeating-panels-methods-from-the-parent-form/3028/2
        https://anvil.works/forum/t/refresh-data-bindings-when-any-key-in-self-items-changes/1141/3
        https://anvil.works/forum/t/repeating-panel-to-collect-new-information/356/3
        """
        # TODO - Improve the update change logic so that don't have to go through whole list everytime
        self.input_repeating_panel.items = [c.input_data_panel_readonly.item \
                                            for c in self.input_repeating_panel.get_components()]
    
    def button_plus_click(self, **event_args):
        """This method is called when the button is clicked"""
        v = validation.Validator()
        v.display_when_invalid(self.valerror_title)
        v.require_date_field(self.input_selldate, self.valerror_1, True)
        v.require_date_field(self.input_buydate, self.valerror_2, True)
        v.require_text_field(self.input_symbol, self.valerror_3, True)
        v.require_text_field(self.input_qty, self.valerror_4, True)
        v.require_text_field(self.input_sales, self.valerror_5, True)
        v.require_text_field(self.input_cost, self.valerror_6, True)
        v.require_text_field(self.input_fee, self.valerror_7, True)

        # IID generation logic is moved to database function
        # When a new row is created, IID is default to be None
        # if v.is_valid():
        #     last_iid = 0
        #     if len(self.input_repeating_panel.items) > 0:
        #         last_iid = self.input_repeating_panel.items[len(self.input_repeating_panel.items)-1]['iid']
      
        new_data = {"sell_date": self.input_selldate.date,
                    "buy_date": self.input_buydate.date,
                    "symbol": self.input_symbol.text,
                    "qty": self.input_qty.text,
                    "sales": self.input_sales.text,
                    "cost": self.input_cost.text,
                    "fee": self.input_fee.text,
                    "sell_price": anvil.server.call('cal_price', self.input_sales.text, self.input_qty.text),
                    "buy_price": anvil.server.call('cal_price', self.input_cost.text, self.input_qty.text),
                    "pnl": anvil.server.call('cal_profit', self.input_sales.text, self.input_cost.text, self.input_fee.text), 
                    #"iid": int(last_iid)+1}
                    "iid": None}
      
        self.input_repeating_panel.items = self.input_repeating_panel.items + [new_data]
        glo.track_input_stock_journals_change()
        self.disable_submit_button()
      
    def dropdown_templ_change(self, **event_args):
        """This method is called when an item is selected"""
        self.templ_name.text, self.dropdown_broker.selected_value = anvil.server.call('get_selected_template_attr', self.dropdown_templ.selected_value)
        self.input_repeating_panel.items = anvil.server.call('select_template_journals', self.dropdown_templ.selected_value)
        # Reset on screen change status
        glo.reset_input_stock_change()
        if self.dropdown_templ.selected_value != glo.input_stock_default_templ_dropdown():
            self.button_submit.enabled = True

    def dropdown_templ_show(self, **event_args):
        """This method is called when the DropDown is shown on the screen"""
        self.dropdown_templ.items = anvil.server.call('generate_template_dropdown')
    
    def dropdown_broker_show(self, **event_args):
        """This method is called when the DropDown is shown on the screen"""
        self.dropdown_broker.items = [''] + anvil.server.call('select_brokers')

    def button_save_templ_click(self, **event_args):
        """This method is called when the button is clicked"""
        templ_id = anvil.server.call('get_template_id', self.dropdown_templ.selected_value)
        templ_name = self.templ_name.text
        broker_id = self.dropdown_broker.selected_value
        templ_id = anvil.server.call('save_templates',
                                     template_id=templ_id,
                                     template_name=templ_name, 
                                     broker_id=broker_id,
                                     del_iid=glo.del_iid
                                    )

        if templ_id is None or templ_id <= 0:
            n = Notification("ERROR: Fail to save template {templ_name}.".format(templ_name=templ_name))
            n.show()
            return
        
        """ Trigger save_row_change if del_iid is not empty """
        if len(glo.del_iid) > 0:
            self.save_row_change()
            glo.reset_deleted_row()
        
        """ Add/Update """
        result = anvil.server.call('upsert_journals', templ_id, self.input_repeating_panel.items)

        if result is not None and result > 0:
            """ Reflect the change in template dropdown """
            self.dropdown_templ.items = anvil.server.call('generate_template_dropdown')
            self.dropdown_templ.selected_value = anvil.server.call('generate_template_dropdown_item', templ_id, templ_name)
            self.input_repeating_panel.items = anvil.server.call('select_template_journals', self.dropdown_templ.selected_value)
            self.button_submit.enabled = True
            n = Notification("Template {templ_name} has been saved successfully.".format(templ_name=templ_name))
        else:
            n = Notification("ERROR: Fail to save template {templ_name}.".format(templ_name=templ_name))
        n.show()
            
    def button_erase_click(self, **event_args):
        """This method is called when the button is clicked"""
        self.input_selldate.date = ""
        self.input_buydate.date = ""
        self.input_symbol.text = ""
        self.input_qty.text = ""
        self.input_sales.text = ""
        self.input_cost.text = ""
        self.input_fee.text = 0
        self.input_sell_price.text = ""
        self.input_buy_price.text = ""
        self.input_pnl.text = ""
        """ Reset row delete flag """
        glo.reset_deleted_row()
    
    def button_delete_templ_click(self, **event_args):
        """This method is called when the button is clicked"""
        to_be_del_templ_name = self.dropdown_templ.selected_value
        msg = Label(text="Proceed template <{templ_name}> deletion by clicking DELETE.".format(templ_name=to_be_del_templ_name))
        userconf = alert(content=msg, 
                        title=f"Alert - Template Deletion",
                        buttons=[
                        ("DELETE", "Y"),
                        ("CANCEL", "N")
                        ])
    
        if userconf == "Y":
            templ_id = anvil.server.call('get_template_id', to_be_del_templ_name)
            result = anvil.server.call('delete_templates', template_id=templ_id)
            if result is not None and result > 0:
                """ Reset row delete flag """
                glo.reset_deleted_row()
            
                """ Reflect the change in template dropdown """
                self.dropdown_templ_show()
                self.dropdown_broker_show()
                self.input_repeating_panel.items = []
                
                n = Notification("Template {templ_name} has been deleted.".format(templ_name=to_be_del_templ_name))
                n.show()
            else:
                n = Notification("ERROR: Fail to delete template {templ_name}.".format(templ_name=to_be_del_templ_name))
                n.show()                

    def button_submit_click(self, **event_args):
        """This method is called when the button is clicked"""
        to_be_submitted_templ_name = self.dropdown_templ.selected_value
        templ_id = anvil.server.call('get_template_id', to_be_submitted_templ_name)
        templ_name = self.templ_name.text
        broker_id = self.dropdown_broker.selected_value
        result = anvil.server.call('submit_templates', templ_id, True)

        if result is not None and result > 0:
            """ Reflect the change in template dropdown """
            self.dropdown_templ.items = anvil.server.call('generate_template_dropdown')
            self.dropdown_templ.raise_event('change')
        
            n = Notification("Template {templ_name} has been submitted.\n It can be viewed in the transaction list report only.".format(templ_name=to_be_submitted_templ_name))
            n.show()
        else:
            n = Notification("ERROR: Fail to submit template {templ_name}.".format(templ_name=to_be_submitted_templ_name))
            n.show()

    def templ_name_change(self, **event_args):
        """This method is called when the text in this text box is edited"""
        glo.track_input_stock_template_change()
        self.disable_submit_button()

    def dropdown_broker_change(self, **event_args):
        """This method is called when an item is selected"""
        glo.track_input_stock_template_change()
        self.disable_submit_button()

    def disable_submit_button(self, **event_args):
        self.button_submit.enabled = False    