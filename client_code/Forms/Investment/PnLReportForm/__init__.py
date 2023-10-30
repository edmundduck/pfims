from ._anvil_designer import PnLReportFormTemplate
from anvil import *
from ....Controllers import ReportSearchPanelController
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
        self.rpt_panel.items = ReportSearchPanelController.drill_pnl_data(self.hidden_time_datefrom.date, self.hidden_time_dateto.date, list(self.hidden_symbol.text), self.rpt_panel.items, date, mode, action)
