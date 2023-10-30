import anvil.server
from ..DataAccess import ReportingDAModule
from ..Entities.StockJournal import StockJournal
from ..SysProcess import SystemModule as sysmod
from ..SysProcess import LoggingModule
from ..Utils import Helper
from ..Utils.Constants import Icons, PNLDrillMode

# This is a server module. It runs on the Anvil server,
# rather than in the user's browser.

logger = LoggingModule.ServerLogger()

def format_pnl_dict(rowitem, dictupdate, key, mode):
    """
    Internal function - Format P&L dictionary. Directly onto dictupdate parameter.
    
    Parameters:
        rowitem (dict): Items in rows returned from DB table (which stores template journals) search result.
        dictupdate (dict of list): The row structure for P&L data.
        key (string): Key of date.
        mode (string): Period mode - y/m/d (Year/Month/Day)
    """
    numtrade, numdaytrade, sales, cost, fee, pnl, mod = dictupdate.get(key, [0, 0, 0, 0, 0, 0, ''])
    if (rowitem[StockJournal.field_sell_date()] - rowitem[StockJournal.field_buy_date()]).days == 0:
        numdaytrade += 1
    numtrade += 1
    sales += rowitem[StockJournal.field_total_sold()]
    cost += rowitem[StockJournal.field_total_cost()]
    fee += rowitem[StockJournal.field_fee()]
    pnl += rowitem[StockJournal.field_pnl()]
    mod = mode
    dictupdate.update({key: [numtrade, numdaytrade, sales, cost, fee, pnl, mode]})

def format_pnl_child(dictupdate, parent, child):
    """
    Internal function - Format a parent: child mapping into dictionary.

    Parameters:
        dictupdate (dict of list): The row structure for P&L data.
        parent (string): Key of parent.
        child (string): Key of child.
    """
    childset = dictupdate.get(parent, set())
    childset.add(child)
    dictupdate.update({parent: childset})
  
@logger.log_function
def build_pnl_data(start_date, end_date, symbols):
    """
    Internal function - Load DB table which stores template journals data to build 3 P&L data dictionaries - day, month, year.

    Parameters:
        start_date (date): Start date of the search.
        end_date (date): End date of the search.
        symbols (list): List of selected symbols.

    Returns:
        dictstruct_day (dict of list): The row structure for P&L data in day.
        dictstruct_mth (dict of list): The row structure for P&L data in month.
        dictstruct_yr (dict of list): The row structure for P&L data in year.
        dictstruct_child (dict of list): The row structure for P&L data as child.
        dictstruct_gchild (dict of list): The row structure for P&L data as grandchild.
    """
    userid = sysmod.get_current_userid()
    rows = ReportingDAModule.select_journals(start_date, end_date, symbols)
    
    # Prepare the data in dictionary structure
    dictstruct_day = {}
    dictstruct_mth = {}
    dictstruct_yr = {}
    dictstruct_child = {}
    dictstruct_gchild = {}
    for i in rows:
        # Key has to be in string instead of datetime obj
        sell_date_str = i[StockJournal.field_sell_date()].strftime("%Y-%m-%d")
        sell_mth_str = i[StockJournal.field_sell_date()].strftime("%Y-%m")
        sell_yr_str = i[StockJournal.field_sell_date()].strftime("%Y")
        logger.debug(f"sell={i[StockJournal.field_sell_date()]} / buy={i[StockJournal.field_buy_date()]} / diff={(i[StockJournal.field_sell_date()]-i[StockJournal.field_buy_date()]).days}")

        # Handling of Day
        format_pnl_dict(i, dictstruct_day, sell_date_str, PNLDrillMode.DAY)
        # Handling of Month
        format_pnl_dict(i, dictstruct_mth, sell_mth_str, PNLDrillMode.MONTH)
        # Handling of Year
        format_pnl_dict(i, dictstruct_yr, sell_yr_str, PNLDrillMode.YEAR)
        # Handling parent:child relationship dict
        format_pnl_child(dictstruct_child, sell_mth_str, sell_date_str)
        format_pnl_child(dictstruct_child, sell_yr_str, sell_mth_str)
        format_pnl_child(dictstruct_gchild, sell_yr_str, sell_date_str)

    logger.trace('dictstruct_day=', dictstruct_day)
    logger.trace('dictstruct_mth=', dictstruct_mth)
    logger.trace('dictstruct_yr=', dictstruct_yr)
    logger.trace('dictstruct_child=', dictstruct_child)
    logger.trace('dictstruct_gchild=', dictstruct_gchild)
    return dictstruct_day, dictstruct_mth, dictstruct_yr, dictstruct_child, dictstruct_gchild

@anvil.server.callable("generate_init_pnl_list")
@logger.log_function
def generate_init_pnl_list(start_date, end_date, symbols):
    """
    Generate initial P&L list (year only).

    Parameters:
        start_date (date): Start date of the search.
        end_date (date): End date of the search.
        symbols (list): List of selected symbols.

    Returns:
        rowstruct (list of dict): The row structure for P&L data.
    """
    userid = sysmod.get_current_userid()
    rowstruct = []
    
    dictstruct_day, dictstruct_mth, dictstruct_yr, dictstruct_child, dictstruct_gchild = build_pnl_data(start_date, end_date, symbols)
    
    for j in dictstruct_yr.keys():
        numtrade, numdaytrade, sales, cost, fee, pnl, mode = dictstruct_yr.get(j)
        dictitem = {
            StockJournal.field_sell_date(): j,
            'num_trade': numtrade,
            'num_daytrade': numdaytrade,
            StockJournal.field_total_sold(): sales,
            StockJournal.field_total_cost(): cost,
            StockJournal.field_fee(): fee,
            StockJournal.field_pnl(): pnl,
            'mode': mode, 
            'action': Icons.DATA_DRILLDOWN
        }
        rowstruct += [dictitem]
    
    return sorted(rowstruct, key=lambda x: x.get(StockJournal.field_sell_date()))

@anvil.server.callable("update_pnl_list")
@logger.log_function
def update_pnl_list(start_date, end_date, symbols, pnl_list, date_value, mode, action):
    """
    Update P&L data according to expand/shrink action and reformat into repeating panel compatible data (dict in list).

    Sample data:
        start_date=2019-07-31
        end_date=None
        symbols=[]
        pnl_list=[{'fee': 0, 'sales': 3950603, 'num_daytrade': 7, 'mode': 'y', 'pnl': 14895.76, 'action': 'fa:plus-square', 'num_trade': 16, 'cost': 3935706, 'sell_date': '2020'}, {'fee': 0, 'sales': 15028798.06, 'num_daytrade': 62, 'mode': 'y', 'pnl': 96247.05000000005, 'action': 'fa:plus-square', 'num_trade': 143, 'cost': 14932552.19, 'sell_date': '2021'}, {'fee': 0, 'sales': 1530632.5000000002, 'num_daytrade': 3, 'mode': 'y', 'pnl': 6681.640000000002, 'action': 'fa:plus-square', 'num_trade': 25, 'cost': 1523950.9, 'sell_date': '2022'}]
        date_value=2021
        mode=y
        action=fa:plus-square
    
    Parameters:
        start_date (date): Start date of the search.
        end_date (date): End date of the search.
        symbols (list): List of selected symbols.
        pnl_list (list of dict): List of P&L data.
        date_value (string): Date value in string of the expanded/shrinked section.
        mode (string): Period mode - y/m/d (Year/Month/Day)
        action (string): Expand or shrink in the name of the clicked icon

    Returns:
        rowstruct (list of dict): The row structure for P&L data.
    """
    userid = sysmod.get_current_userid()
    logger.debug(f"param list={start_date} / {end_date} / {symbols} / {pnl_list} / {date_value} / {mode} / {action}")
    
    rowstruct = []
    dictstruct_day, dictstruct_mth, dictstruct_yr, dictstruct_child, dictstruct_gchild = build_pnl_data(start_date, end_date, symbols)
    logger.trace('dictstruct_day=', dictstruct_day)
    logger.trace('dictstruct_mth=', dictstruct_mth)
    logger.trace('dictstruct_yr=', dictstruct_yr)
    logger.trace('dictstruct_child=', dictstruct_child)
    logger.trace('dictstruct_gchild=', dictstruct_gchild)
    
    if action == Icons.DATA_DRILLDOWN:
        dictstruct = None
        childaction = ''
        rowstruct = pnl_list
        
        if mode == PNLDrillMode.YEAR:
            dictstruct = dictstruct_mth
            childaction = Icons.DATA_DRILLDOWN
        elif mode == PNLDrillMode.MONTH:
            dictstruct = dictstruct_day
      
        # Update action from plus to minus
        for rowitem in rowstruct:
            if rowitem[StockJournal.field_sell_date()] == date_value:
                rowstruct.remove(rowitem)
                rowitem['action'] = Icons.DATA_SUMMARIZE
                rowstruct = rowstruct + [rowitem]
      
        for j in dictstruct_child.get(date_value):
            numtrade, numdaytrade, sales, cost, fee, pnl, mod = dictstruct.get(j)
            dictitem = {
                StockJournal.field_sell_date(): j,
                'num_trade': numtrade,
                'num_daytrade': numdaytrade,
                StockJournal.field_total_sold(): sales,
                StockJournal.field_total_cost(): cost,
                StockJournal.field_fee(): fee,
                StockJournal.field_pnl(): pnl,
                'mode': mod,
                'action': childaction
            }
            rowstruct += [dictitem]
      
        #rowstruct = rowstruct + pnl_list
    elif action == Icons.DATA_SUMMARIZE:
        # Make a copy of P&L list into rowstruct
        rowstruct = list(pnl_list)
        childlist = dictstruct_child.get(date_value, {})
        gchildlist = dictstruct_gchild.get(date_value, {})
    
        for rowitem in pnl_list:
            # Remove child items from shrinked parent
            if rowitem[StockJournal.field_sell_date()] in childlist:
                rowstruct.remove(rowitem)
            if rowitem[StockJournal.field_sell_date()] in gchildlist:
                rowstruct.remove(rowitem)
            # Update action from minus to plus
            if rowitem[StockJournal.field_sell_date()] == date_value:
                rowstruct.remove(rowitem)
                rowitem['action'] = Icons.DATA_DRILLDOWN
                rowstruct = rowstruct + [rowitem]
    else:
        pass

    logger.trace("rowstruct=", rowstruct)
    return sorted(rowstruct, key=lambda x: x.get(StockJournal.field_sell_date()))

@anvil.server.callable("proc_search_expense_list")
@logger.log_function
def proc_search_expense_list(start_date, end_date, labels=[]):
    rows = ReportingDAModule.select_transactions_filter_by_labels(start_date, end_date, labels)
    return rows