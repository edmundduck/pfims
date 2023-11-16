import anvil.server
from datetime import date
from ..Utils.Constants import CacheKey, ExpenseReportType, SearchInterval
from ..Utils.Logger import ClientLogger

# This is a module.
# You can define variables and functions here, and use them from any form. For example, in a top-level form:

logger = ClientLogger()

def generate_search_interval_dropdown():
    """
    Access search interval dropdown from either client cache or generate from DB data returned from server side.

    Returns:
        cache.get_cache (list): Search interval dropdown formed by search interval DB table data.
    """
    from . import UserSettingController
    return UserSettingController.generate_search_interval_dropdown()

@logger.log_function
def generate_labels_dropdown(reload=False):
    """
    Access labels dropdown from either client cache or generate from DB data returned from server side.

    Parameters:
        reload (Boolean): Optional. True if clear cache is required. False by default.

    Returns:
        cache.get_cache (list): Labels dropdown formed by labels DB table data.
    """
    from . import LabelMaintController
    return LabelMaintController.generate_labels_dropdown(reload)

@logger.log_function
def generate_stock_symbols_dropdown(search_interval_dropdown_selected, from_date, to_date):
    """
    Access stock symbols dropdown generated from DB data returned from server side. No cache is stored in client side.

    Parameters:
        search_interval_dropdown_selected (list): The selected value in list from the account dropdown.
        from_date (date): Date to search from.
        to_date (date): Date to search to.

    Returns:
        result (list): Stock symbols found within from_date and to_date in list.
    """
    
    interval = search_interval_dropdown_selected
    if interval != SearchInterval.INTERVAL_SELF_DEFINED:
        from_date = _get_start_date(date.today(), interval)
        to_date = date.today()
    rows = anvil.server.call('select_journals', from_date, to_date)
    result = list(sorted(set(row['symbol'] for row in rows)))
    return result

def _get_L1M_start_date(end_date):
    """
    Internal function - Return start date of last 1 month.

    Parameters:
        end_date (date): End date of the search.

    Returns:
        date: 1 month ago from end date.
    """
    return date(end_date.year-1, end_date.month+12-1, end_date.day) if end_date.month-1 < 1 else date(end_date.year, end_date.month-1, end_date.day)

def _get_L3M_start_date(end_date):
    """
    Internal function - Return start date of last 3 months.

    Parameters:
        end_date (date): End date of the search.

    Returns:
        date: 3 months ago from end date.
    """
    return date(end_date.year-1, end_date.month+12-3, end_date.day) if end_date.month-3 < 1 else date(end_date.year, end_date.month-3, end_date.day)

def _get_L6M_start_date(end_date):
    """
    Internal function - Return start date of last 6 months.

    Parameters:
        end_date (date): End date of the search.

    Returns:
        date: 6 months ago from end date.
    """
    return date(end_date.year-1, end_date.month+12-6, end_date.day) if end_date.month-6 < 1 else date(end_date.year, end_date.month-6, end_date.day)

def _get_L1Y_start_date(end_date):
    """
    Internal function - Return start date of last 1 year.

    Parameters:
        end_date (date): End date of the search.

    Returns:
        date: 1 year ago from end date.
    """
    return date(end_date.year-1, end_date.month, end_date.day)

def _get_YTD_start_date(end_date):
    """
    Internal function - Return the 1st date of the current year.

    Parameters:
        end_date (date): End date of the search.

    Returns:
        date: The first day of the current year.
    """
    return date(end_date.year, 1, 1)

def _get_default_start_date(end_date):
    """
    Internal function - Return the default start date.

    Parameters:
        end_date (date): End date of the search.

    Returns:
        None
    """
    return date(end_date.year, 1, 1)

def _get_start_date(end_date, interval):
    """
    Get start date based on end date and time interval dropdown value.

    Parameters:
        end_date (date): End date of the search.
        interval (string): Constant of search interval.

    Returns:
        function: A function which coresponds to the interval.
    """
    switcher = {
        SearchInterval.INTERVAL_LAST_1_MTH: _get_L1M_start_date,
        SearchInterval.INTERVAL_LAST_3_MTH: _get_L3M_start_date,
        SearchInterval.INTERVAL_LAST_6_MTH: _get_L6M_start_date,
        SearchInterval.INTERVAL_LAST_1_YR: _get_L1Y_start_date,
        SearchInterval.INTERVAL_YEAR_TO_DATE: _get_YTD_start_date,
    }
    return switcher.get(interval, _get_default_start_date)(end_date)

def populate_repeating_panel_stock_transactions(search_interval_dropdown_selected, from_date, to_date, symbols=[]):
    """
    Populate repeating panel items with stock trading transactions.

    Parameters:
        search_interval_dropdown_selected (list): The selected value in list from the search interval dropdown.
        from_date (date): Date to search from.
        to_date (date): Date to search to.
        symbols (list): List of stock symbols.

    Returns:
        result (list of dict): A list of stock trading transactions for repeating panel.
    """
    interval = search_interval_dropdown_selected
    if interval != SearchInterval.INTERVAL_SELF_DEFINED:
        from_date = _get_start_date(date.today(), interval)
        to_date = date.today()
    result = anvil.server.call('select_journals', from_date, to_date, symbols)
    return result

def generate_repeating_panel_stock_transactions_file(search_interval_dropdown_selected, from_date, to_date, symbols=[]):
    """
    Generate repeating panel items with stock trading transactions in file

    Parameters:
        search_interval_dropdown_selected (list): The selected value in list from the search interval dropdown.
        from_date (date): Date to search from.
        to_date (date): Date to search to.
        symbols (list): List of stock symbols.

    Returns:
        csv: Result in CSV file.
    """
    interval = search_interval_dropdown_selected
    if interval != SearchInterval.INTERVAL_SELF_DEFINED:
        from_date = _get_start_date(date.today(), interval)
        to_date = date.today()
    result = anvil.server.call('generate_csv', from_date, to_date, symbols)
    return result

def populate_repeating_panel_stock_profit_n_loss(search_interval_dropdown_selected, from_date, to_date, symbols=[]):
    """
    Populate repeating panel items with stock profit and loss.

    Parameters:
        search_interval_dropdown_selected (list): The selected value in list from the search interval dropdown.
        from_date (date): Date to search from.
        to_date (date): Date to search to.
        symbols (list): List of stock symbols.

    Returns:
        result (list of dict): A list of stock profit and loss calculations for repeating panel.
    """
    interval = search_interval_dropdown_selected
    if interval != SearchInterval.INTERVAL_SELF_DEFINED:
        from_date = _get_start_date(date.today(), interval)
        to_date = date.today()
    result = anvil.server.call('generate_init_pnl_list', from_date, to_date, symbols)
    return result

def populate_repeating_panel_expense_transactions(search_interval_dropdown_selected, from_date, to_date, labels=[]):
    """
    Populate repeating panel items with expense transactions.

    Parameters:
        search_interval_dropdown_selected (list): The selected value in list from the search interval dropdown.
        from_date (date): Date to search from.
        to_date (date): Date to search to.
        labels (list): List of labels.

    Returns:
        result (list of dict): A list of expense transactions for repeating panel.
    """
    interval = search_interval_dropdown_selected
    if interval != SearchInterval.INTERVAL_SELF_DEFINED:
        from_date = _get_start_date(date.today(), interval)
        to_date = date.today()
    result = anvil.server.call('proc_search_expense_list', from_date, to_date, labels)
    return result

def drill_pnl_data(start_date, end_date, symbols, pnl_list, date_value, mode, action):
    """
    Drill up or drill down profit and loss data into year, month or day detail.

    Parameters:
        start_date (date): Start date of the search.
        end_date (date): End date of the search.
        symbols (list): List of selected symbols.
        pnl_list (list of dict): List of P&L data.
        date_value (string): Date value in string of the expanded/shrinked section.
        mode (string): Period mode - y/m/d (Year/Month/Day)
        action (string): Expand or shrink in the name of the clicked icon

    Returns:
        result (list of dict): The row structure for P&L data.
    """
    result = anvil.server.call('update_pnl_list', start_date, end_date, symbols, pnl_list, date_value, mode, action)
    return result

def populate_expense_analysis_data(report_type_dropdown_selected, search_interval_dropdown_selected, from_date, to_date, labels=[]):
    """
    Populate expense analysis data as repeating panel items and charts.

    Parameters:
        report_type_dropdown_selected (list): The selected value in list from the report type dropdown.
        search_interval_dropdown_selected (list): The selected value in list from the search interval dropdown.
        from_date (date): Date to search from.
        to_date (date): Date to search to.
        labels (list): List of labels.

    Returns:
        result_rp (?): ?
        result_balance (?): ?
        result_chart1 (?): ?
        result_chart2 (?): ?
    """
    interval = search_interval_dropdown_selected
    result_rp, result_chart1, result_chart2 = [None]*3
    if interval != SearchInterval.INTERVAL_SELF_DEFINED:
        from_date = _get_start_date(date.today(), interval)
        to_date = date.today()
    if report_type_dropdown_selected:
        if report_type_dropdown_selected == ExpenseReportType.EXP_PER_LABEL:
            result_rp, result_chart1, result_chart2 = anvil.server.call('proc_search_expense_analysis', from_date, to_date, labels)
        elif report_type_dropdown_selected == ExpenseReportType.BAL_ACCT:
            result_rp, result_chart1, result_chart2 = anvil.server.call('XXX', from_date, to_date, labels)
    return result_rp, result_balanace, result_chart1, result_chart2