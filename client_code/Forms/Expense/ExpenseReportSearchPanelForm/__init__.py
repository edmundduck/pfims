from ._anvil_designer import ExpenseReportSearchPanelFormTemplate
from anvil import *
import plotly.graph_objects as go
from .... import Global
from ....Controllers import ReportSearchPanelController
from ....Utils.ButtonModerator import ButtonModerator
from ....Utils.Constants import ColorSchemes, Icons, ReportFormTag, SearchInterval
from ....Utils.Logger import ClientLogger

logger = ClientLogger()
btnmod = ButtonModerator()

class ExpenseReportSearchPanelForm(ExpenseReportSearchPanelFormTemplate):
    subform = None
    label_key = 'added_labels'

    def __init__(self, subform, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)
    
        # Any code you write here will run when the form opens.
        from ..ExpenseReportForm import ExpenseReportForm
        self.dropdown_interval.items = ReportSearchPanelController.generate_search_interval_dropdown()
        self.dropdown_interval.selected_value = Global.settings.get_search_interval()
        self.time_datefrom.date = Global.settings.get_search_datefrom()
        self.time_dateto.date = Global.settings.get_search_dateto()
        self.subform = subform
        self.colpanel_list.add_component(self.subform)
        if self.subform.tag[ReportFormTag.REPORT_TAG] == ReportFormTag.EXP_LIST_RPT:
            self.button_exp_search.visible = True
            self.button_exp_analysis_search.visible = False
        elif self.subform.tag[ReportFormTag.REPORT_TAG] == ReportFormTag.EXP_ANALYSIS_RPT:
            self.button_exp_search.visible = False
            self.button_exp_analysis_search.visible = True
        self.tag = {self.label_key: {None: 1}}
        self._update_expense_enablement()
         
    # NOTE - If use self.tag['added_symbols'] approach, need to consider the registered default value "[Symbol]"
    # Return selected labels which appear in blue buttons 
    @logger.log_function
    def _getall_selected_labels(self):
        label_list = []
        for i in self.panel_label.get_components():
            if isinstance(i, Button):
                if i.icon == Icons.REMOVE:
                    label_list += [i.tag]
        return label_list

    # Remove all labels selected as blue buttons from dictionary
    @logger.log_function
    def _rmvall_selected_labels(self):
        for i in self.panel_label.get_components():
            if isinstance(i, Button):
                if i.icon == Icons.REMOVE:
                    # Deregister the added label from the dictionary in self.tag
                    self.tag[self.label_key].pop(i.tag)
                    i.remove_from_parent()

    @logger.log_function
    def _update_expense_enablement(self):
        interval = self.dropdown_interval.selected_value[0] if isinstance(self.dropdown_interval.selected_value, list) else self.dropdown_interval.selected_value
        if not interval:
            self._reset_search()
        else:
            self.dropdown_label.items = ReportSearchPanelController.generate_labels_dropdown()
            if interval != SearchInterval.INTERVAL_SELF_DEFINED:
                self.time_datefrom.enabled = False
                self.time_dateto.enabled = False
                self.label_timetotime.enabled = False
            else:
                self.time_datefrom.enabled = True
                self.time_dateto.enabled = True
                self.label_timetotime.enabled = True
            self.button_exp_search.enabled = True
  
    def _reset_search(self):
        self.time_datefrom.date = Global.settings.get_search_datefrom()
        self.time_dateto.date = Global.settings.get_search_dateto()
        self.dropdown_interval.selected_value = Global.settings.get_search_interval()
        self.dropdown_symbol.items = []
        self._rmvall_selected_labels()
        self.subform.rpt_panel.items = []
        self.button_exp_search.enabled = False
    
    @btnmod.one_click_only
    @logger.log_function
    def button_exp_search_click(self, **event_args):
        """This method is called when the button is clicked"""
        label_list = self._getall_selected_labels()
        self.subform.rpt_panel.items = ReportSearchPanelController.populate_repeating_panel_expense_transactions(self.dropdown_interval.selected_value, self.time_datefrom.date, self.time_dateto.date, label_list)

    def button_exp_reset_click(self, **event_args):
        """This method is called when the button is clicked"""
        self._reset_search()

    def exp_rpt_button_plus_click(self, **event_args):
        """This method is called when the button is clicked"""
        lbl_id, lbl_name = self.dropdown_label.selected_value if self.dropdown_label.selected_value is not None else [None, None]
        if self.tag[self.label_key].get(lbl_id, None) is None:
            b = Button(
                text=lbl_name,
                tag=lbl_id,
                icon=Icons.REMOVE,
                foreground=ColorSchemes.BUTTON_FG,
                background=ColorSchemes.BUTTON_BG,
                font_size=12
            )
            self.panel_label.add_component(b, name=lbl_id)
            b.set_event_handler('click', self.exp_rpt_button_minus_click)
            # Register the added label to the dictionary in self.tag to avoid duplication
            self.tag[self.label_key].update({lbl_id: 1})

    @logger.log_function
    def exp_rpt_button_minus_click(self, **event_args):
        b = event_args['sender']
        # Deregister the added label from the dictionary in self.tag
        self.tag[self.label_key].pop(b.tag)
        b.remove_from_parent()

    def button_exp_analysis_search_click(self, **event_args):
        """This method is called when the button is clicked"""
        label_list = self._getall_selected_labels()
        self.subform.rpt_panel.items, pie_chart_data, _ = ReportSearchPanelController.populate_expense_analysis_data(self.dropdown_interval.selected_value, self.time_datefrom.date, self.time_dateto.date, label_list)
        self.build_pie_chart(pie_chart_data)

    def build_pie_chart(self, data, **event_args):
        label_list, amount_list = data if data and isinstance(data, (list, tuple)) else [None, None]
        self.subform.plot_pie_chart.data = [go.Pie(labels=label_list, values=amount_list)]
        