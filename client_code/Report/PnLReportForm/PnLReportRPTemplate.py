from ._anvil_designer import PnLReportRPTemplateTemplate
from anvil import *
import anvil.users
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from ...Utils import Constants as const
from ...Utils.Logging import trace, debug, info, warning, error, critical

# About amount formatting in design page's data binding field
# Refer to https://anvil.works/forum/t/formatting-float-fields-in-a-datagrid/6796

class PnLReportRPTemplate(PnLReportRPTemplateTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)
    
        # Any code you write here will run when the form opens.
        if self.item['pnl'] < 0:
            self.foreground = const.ColorSchemes.AMT_NEG
        else:
            self.foreground = const.ColorSchemes.AMT_POS
      
        if self.item['mode'] == const.PNLDrillMode.YEAR:
            self.button_exp.visible = True
        elif self.item['mode'] == const.PNLDrillMode.MONTH:
            self.button_exp.visible = True
        elif self.item['mode'] == const.PNLDrillMode.DAY:
            self.button_exp.visible = False
      
        if self.item['action'] == const.Icons.DATA_DRILLDOWN:
            self.button_exp.icon = const.Icons.DATA_DRILLDOWN
        elif self.item['action'] == const.Icons.DATA_SUMMARIZE:
            self.button_exp.icon = const.Icons.DATA_SUMMARIZE

    @debug.log_function
    def button_exp_click(self, **event_args):
        """This method is called when the button is clicked"""
        action = self.button_exp.icon
        self.parent.raise_event('x-update', date=self.item['sell_date'], mode=self.item['mode'], action=action)
    
