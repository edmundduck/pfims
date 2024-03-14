from ._anvil_designer import PnLReportRPTemplateTemplate
from anvil import *
from ....Utils.Constants import Icons, PNLDrillMode, Roles
from ....Utils.Logger import ClientLogger

logger = ClientLogger()

# About amount formatting in design page's data binding field
# Refer to https://anvil.works/forum/t/formatting-float-fields-in-a-datagrid/6796

class PnLReportRPTemplate(PnLReportRPTemplateTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)
    
        # Any code you write here will run when the form opens.
        self.row_label_pnl.role = Roles.AMT_NEGATIVE if self.item['pnl'] < 0 else Roles.AMT_POSITIVE
      
        if self.item['mode'] == PNLDrillMode.YEAR:
            self.button_exp.visible = True
        elif self.item['mode'] == PNLDrillMode.MONTH:
            self.button_exp.visible = True
        elif self.item['mode'] == PNLDrillMode.DAY:
            self.button_exp.visible = False
      
        if self.item['action'] == Icons.DATA_DRILLDOWN:
            self.button_exp.icon = Icons.DATA_DRILLDOWN
        elif self.item['action'] == Icons.DATA_SUMMARIZE:
            self.button_exp.icon = Icons.DATA_SUMMARIZE

    @logger.log_function
    def button_exp_click(self, **event_args):
        """This method is called when the button is clicked"""
        action = self.button_exp.icon
        self.parent.raise_event('x-update', date=self.item['sell_date'], mode=self.item['mode'], action=action)
    
