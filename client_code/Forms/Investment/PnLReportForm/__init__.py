from ._anvil_designer import PnLReportFormTemplate
from anvil import *
import anvil.server
from ....Utils.Logger import ClientLogger

logger = ClientLogger()

class PnLReportForm(PnLReportFormTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)
    
        # Any code you write here will run when the form opens.
        self.data_grid.rows_per_page = self.dropdown_displayrow.selected_value
        self.rpt_panel.add_event_handler('x-update', self.update_pnl_list)

    def dropdown_displayrow_change(self, **event_args):
        """This method is called when an item is selected"""
        self.data_grid.rows_per_page = self.dropdown_displayrow.selected_value

    @logger.log_function
    def update_pnl_list(self, date, mode, action, **event_args):
        self.rpt_panel.items = anvil.server.call('update_pnl_list', 
                                                 start_date=self.hidden_time_datefrom.date, 
                                                 end_date=self.hidden_time_dateto.date,  
                                                 symbols=list(self.hidden_symbol.text), 
                                                 pnl_list=self.rpt_panel.items, 
                                                 date_value=date, 
                                                 mode=mode, 
                                                 action=action)