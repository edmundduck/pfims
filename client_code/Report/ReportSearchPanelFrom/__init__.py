from ._anvil_designer import ReportSearchPanelFromTemplate
from anvil import *
import anvil.server
from datetime import date
from ...Controllers import ReportSearchPanelController
from ...Utils.ButtonModerator import ButtonModerator
from ...Utils.Constants import ColorSchemes, Icons, SearchInterval
from ...Utils.Logger import ClientLogger

logger = ClientLogger()
btnmod = ButtonModerator()

class ReportSearchPanelFrom(ReportSearchPanelFromTemplate):
    subform = None

    def __init__(self, subform, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)
    
        # Any code you write here will run when the form opens.
        from ... import Global
        from ..TransactionReportForm import TransactionReportForm
        from ..PnLReportForm import PnLReportForm
        from ..ExpenseReportForm import ExpenseReportForm
        self.dropdown_interval.items = ReportSearchPanelController.generate_search_interval_dropdown()
        self.dropdown_interval.selected_value = Global.settings.get_search_interval()
        self.time_datefrom.date = Global.settings.get_search_datefrom()
        self.time_dateto.date = Global.settings.get_search_dateto()

        if "Transaction" in subform.report_name.text:
            self.subform = TransactionReportForm()
            self.colpanel_list.add_component(self.subform)
            self.panel_symbol.visible = True
            self.panel_label.visible = False
            self.panel_tranx_list.visible = True
            self.panel_pnl_report.visible = False
            self.panel_exp_list.visible = False
            # Prevent from adding default value "[Symbol]" by registering to the dictionary
            self.tag = {'added_symbols': {None: 1}}
            self._update_stock_enablement()
        elif "P&L" in subform.report_name.text:
            self.subform = PnLReportForm()
            self.colpanel_list.add_component(self.subform)
            self.panel_symbol.visible = True
            self.panel_label.visible = False
            self.panel_tranx_list.visible = False
            self.panel_pnl_report.visible = True
            self.panel_exp_list.visible = False
            # Prevent from adding default value "[Symbol]" by registering to the dictionary
            self.tag = {'added_symbols': {None: 1}}
            self._update_stock_enablement()
        elif "Expense" in subform.report_name.text:
            self.subform = ExpenseReportForm()
            self.colpanel_list.add_component(self.subform)
            self.panel_symbol.visible = False
            self.panel_label.visible = True
            self.panel_tranx_list.visible = False
            self.panel_pnl_report.visible = False
            self.panel_exp_list.visible = True
            # Prevent from adding default value "[Symbol]" by registering to the dictionary
            self.tag = {'added_labels': {None: 1}}
            self._update_expense_enablement()
        else:
            # If error, show no buttons
            self.panel_symbol.visible = False
            self.panel_tranx_list.visible = False
            self.panel_pnl_report.visible = False
            self.panel_exp_list.visible = False
         
    # NOTE - If use self.tag['added_symbols'] approach, need to consider the registered default value "[Symbol]"
    # Return selected symbols which appear in blue buttons 
    @logger.log_function
    def _getall_selected_symbols(self):
        symbol_list = []
        for i in self.panel_symbol.get_components():
            if isinstance(i, Button):
                if i.icon == Icons.REMOVE:
                    symbol_list += [i.text]
        return symbol_list

    # Remove all symbols selected as blue buttons from dictionary
    @logger.log_function
    def _rmvall_selected_symbols(self):
        for i in self.panel_symbol.get_components():
            if isinstance(i, Button):
                if i.icon == Icons.REMOVE:
                    # Deregister the added symbol from the dictionary in self.tag
                    self.tag['added_symbols'].pop(i.text)
                    i.remove_from_parent()

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
                    self.tag['added_labels'].pop(i.tag)
                    i.remove_from_parent()

    @logger.log_function
    def _update_stock_enablement(self):
        interval = self.dropdown_interval.selected_value[0] if isinstance(self.dropdown_interval.selected_value, list) else self.dropdown_interval.selected_value
        if not interval:
            self._reset_search()
        else:
            self.dropdown_symbol.items = ReportSearchPanelController.generate_stock_symbols_dropdown(self.dropdown_interval.selected_value, self.time_datefrom.date, self.time_dateto.date)
            if interval != SearchInterval.INTERVAL_SELF_DEFINED:
                self.time_datefrom.enabled = False
                self.time_dateto.enabled = False
                self.label_timetotime.enabled = False
            else:
                self.time_datefrom.enabled = True
                self.time_dateto.enabled = True
                self.label_timetotime.enabled = True
            self.button_tranx_gen_csv.enabled = True
            self.button_tranx_search.enabled = True
            self.button_pnl_search.enabled = True
  
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
        from ... import Global
        self.time_datefrom.date = Global.settings.get_search_datefrom()
        self.time_dateto.date = Global.settings.get_search_dateto()
        self.dropdown_interval.selected_value = Global.settings.get_search_interval()
        self.dropdown_symbol.items = []
        self._rmvall_selected_symbols()
        self._rmvall_selected_labels()
        self.subform.rpt_panel.items = []
        self.button_tranx_gen_csv.enabled = False
        self.button_tranx_search.enabled = False
        self.button_pnl_search.enabled = False
        self.button_exp_search.enabled = False
    
    def _find_enddate(self):
        interval = self.dropdown_interval.selected_value[0] if isinstance(self.dropdown_interval.selected_value, list) else self.dropdown_interval.selected_value
        if interval != SearchInterval.INTERVAL_SELF_DEFINED or self.time_dateto.date is None:
            return date.today()
        else:
            return self.time_dateto.date
  
    def _find_startdate(self):
        interval = self.dropdown_interval.selected_value[0] if isinstance(self.dropdown_interval.selected_value, list) else self.dropdown_interval.selected_value
        if interval != SearchInterval.INTERVAL_SELF_DEFINED or self.time_datefrom.date is None:
            return anvil.server.call('get_start_date', date.today(), interval)      
        else:
            return self.time_datefrom.date 
  
    def dropdown_interval_change(self, **event_args):
        """This method is called when an item is selected"""
        if ("Transaction" or "P&L") in self.subform.report_name.text:
            self._rmvall_selected_symbols()
            self._update_stock_enablement()

    def time_datefrom_change(self, **event_args):
        """This method is called when the selected date changes"""
        if ("Transaction" or "P&L") in self.subform.report_name.text:
            self.dropdown_symbol.items = ReportSearchPanelController.generate_stock_symbols_dropdown(self.dropdown_interval.selected_value, self.time_datefrom.date, self.time_dateto.date)

    def time_dateto_change(self, **event_args):
        """This method is called when the selected date changes"""
        if ("Transaction" or "P&L") in subform.report_name.text:
            self.dropdown_symbol.items = ReportSearchPanelController.generate_stock_symbols_dropdown(self.dropdown_interval.selected_value, self.time_datefrom.date, self.time_dateto.date)

    @logger.log_function
    def tranx_rpt_button_plus_click(self, **event_args):
        """This method is called when the button is clicked"""
        if self.tag['added_symbols'].get(self.dropdown_symbol.selected_value, None) is None:
            b = Button(text=self.dropdown_symbol.selected_value,
                    icon=Icons.REMOVE,
                    foreground=ColorSchemes.BUTTON_FG,
                    background=ColorSchemes.BUTTON_BG)
            self.panel_symbol.add_component(b, name=self.dropdown_symbol.selected_value)
            b.set_event_handler('click', self.tranx_rpt_button_minus_click)
            # Register the added symbol to the dictionary in self.tag to avoid duplication
            self.tag['added_symbols'].update({self.dropdown_symbol.selected_value: 1})

    @logger.log_function
    def tranx_rpt_button_minus_click(self, **event_args):
        b = event_args['sender']
        # Deregister the added symbol from the dictionary in self.tag
        self.tag['added_symbols'].pop(b.text)
        b.remove_from_parent()

    @btnmod.one_click_only
    @logger.log_function
    def button_tranx_search_click(self, **event_args):
        """This method is called when the button is clicked"""
        symbol_list = self._getall_selected_symbols()
        self.subform.rpt_panel.items = ReportSearchPanelController.populate_repeating_panel_stock_transactions(self.dropdown_interval.selected_value, self.time_datefrom.date, self.time_dateto.date, symbol_list)

    @btnmod.one_click_only
    def button_tranx_gen_csv_click(self, **event_args):
        """This method is called when the button is clicked"""
        symbol_list = self._getall_selected_symbols()
        csv_file = ReportSearchPanelController.generate_repeating_panel_stock_transactions_file(self.dropdown_interval.selected_value, self.time_datefrom.date, self.time_dateto.date, symbol_list)
        anvil.media.download(csv_file)

    def button_tranx_reset_click(self, **event_args):
        """This method is called when the button is clicked"""
        self._reset_search()
    
    @btnmod.one_click_only
    @logger.log_function
    def button_pnl_search_click(self, **event_args):
        """This method is called when the button is clicked"""
        symbol_list = self._getall_selected_symbols()
        self.subform.hidden_time_datefrom.date = startdate
        self.subform.hidden_symbol.text = symbol_list
        self.subform.rpt_panel.items = ReportSearchPanelController.populate_repeating_panel_stock_profit_n_loss(self.dropdown_interval.selected_value, self.time_datefrom.date, self.time_dateto.date, symbol_list)

    def button_pnl_reset_click(self, **event_args):
        """This method is called when the button is clicked"""
        self._reset_search()

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
        if self.tag['added_labels'].get(lbl_id, None) is None:
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
            self.tag['added_labels'].update({lbl_id: 1})

    @logger.log_function
    def exp_rpt_button_minus_click(self, **event_args):
        b = event_args['sender']
        # Deregister the added label from the dictionary in self.tag
        self.tag['added_labels'].pop(b.tag)
        b.remove_from_parent()
