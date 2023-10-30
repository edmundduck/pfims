import anvil.server
import psycopg2
import psycopg2.extras
from datetime import date, datetime, timedelta
from ..SysProcess import SystemModule as sysmod
from ..SysProcess import LoggingModule
from ..Utils import Helper
from ..Utils.Constants import Database, Icons, PNLDrillMode

# This is a server module. It runs on the Anvil server,
# rather than in the user's browser.
logger = LoggingModule.ServerLogger()

@anvil.server.callable("select_journals")
@logger.log_function
def select_journals(start_date, end_date, symbols=[]):
    """
    Return journals for repeating panel to display based on sell and buy date criteria.

    Parameters:
        start_date (date): Start date of the search.
        end_date (date): End date of the search.
        symbols (list): List of selected symbols.

    Returns:
        rows (list): Stock journals in list.
    """
    userid = sysmod.get_current_userid()
    conn = sysmod.db_connect()
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        sell_sql = "j.sell_date <= '{0}'".format(end_date) if end_date is not None else ""
        buy_sql = "j.buy_date >= '{0}'".format(start_date) if start_date is not None else ""
        symbol_sql = "j.symbol IN ({0})".format(",".join("'" + i + "'" for i in symbols)) if len(symbols) > 0 else ""
        conn_sql1 = " AND " if sell_sql or buy_sql or symbol_sql else ""
        conn_sql2 = " AND " if sell_sql and (buy_sql or symbol_sql) else ""
        conn_sql3 = " AND " if (sell_sql or buy_sql) and symbol_sql else ""
        sql = f"SELECT j.iid, j.template_id, j.sell_date, j.buy_date, j.symbol, j.qty, j.sales, j.cost, j.fee, \
        j.sell_price, j.buy_price, j.pnl FROM {Database.SCHEMA_FIN}.templ_journals j, {Database.SCHEMA_FIN}.templates t \
        WHERE t.userid = {userid} AND t.template_id = j.template_id {conn_sql1} {sell_sql} {conn_sql2} \
        {buy_sql} {conn_sql3} {symbol_sql} ORDER BY sell_date DESC, symbol ASC"
        cur.execute(sql)
        rows = cur.fetchall()
        logger.trace("rows=", rows)
        cur.close()
    return list(rows)

@anvil.server.callable("generate_csv")
@logger.log_function
def generate_csv(start_date, end_date, symbols):
    """
    Return template journals for csv generation.

    Parameters:
        start_date (date): Start date of the search.
        end_date (date): End date of the search.
        symbols (list): List of selected symbols.

    Returns:
        csv: Result in CSV file.
    """
    return select_journals(start_date, end_date, symbols).to_csv()

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
    if (rowitem['sell_date'] - rowitem['buy_date']).days == 0:
        numdaytrade += 1
    numtrade += 1
    sales += rowitem['sales']
    cost += rowitem['cost']
    fee += rowitem['fee']
    pnl += rowitem['pnl']
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
    rows = select_journals(start_date, end_date, symbols)
    
    # Prepare the data in dictionary structure
    dictstruct_day = {}
    dictstruct_mth = {}
    dictstruct_yr = {}
    dictstruct_child = {}
    dictstruct_gchild = {}
    for i in rows:
        # Key has to be in string instead of datetime obj
        sell_date_str = i['sell_date'].strftime("%Y-%m-%d")
        sell_mth_str = i['sell_date'].strftime("%Y-%m")
        sell_yr_str = i['sell_date'].strftime("%Y")
        logger.debug(f"sell={i['sell_date']} / buy={i['buy_date']} / diff={(i['sell_date']-i['buy_date']).days}")
        
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
            'sell_date': j,
            'num_trade': numtrade,
            'num_daytrade': numdaytrade,
            'sales': sales,
            'cost': cost,
            'fee': fee,
            'pnl': pnl,
            'mode': mode, 
            'action': Icons.DATA_DRILLDOWN
        }
        rowstruct += [dictitem]
    
    return sorted(rowstruct, key=lambda x: x.get('sell_date'))

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
            if rowitem['sell_date'] == date_value:
                rowstruct.remove(rowitem)
                rowitem['action'] = Icons.DATA_SUMMARIZE
                rowstruct = rowstruct + [rowitem]
      
        for j in dictstruct_child.get(date_value):
            numtrade, numdaytrade, sales, cost, fee, pnl, mod = dictstruct.get(j)
            dictitem = {
                'sell_date': j,
                'num_trade': numtrade,
                'num_daytrade': numdaytrade,
                'sales': sales,
                'cost': cost,
                'fee': fee,
                'pnl': pnl,
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
            if rowitem['sell_date'] in childlist:
                rowstruct.remove(rowitem)
            if rowitem['sell_date'] in gchildlist:
                rowstruct.remove(rowitem)
            # Update action from minus to plus
            if rowitem['sell_date'] == date_value:
                rowstruct.remove(rowitem)
                rowitem['action'] = Icons.DATA_DRILLDOWN
                rowstruct = rowstruct + [rowitem]
    else:
        pass

    logger.trace("rowstruct=", rowstruct)
    return sorted(rowstruct, key=lambda x: x.get('sell_date'))

@logger.log_function
def select_transactions_filter_by_labels(start_date, end_date, labels=[]):
    """
    Return transactions for repeating panel to display based on transaction date criteria.

    Parameters:
        start_date (date): Start date of the search.
        end_date (date): End date of the search.
        labels (list): List of selected labels.

    Returns:
        rows (list): Transactions in list.
    """
    from ..Entities.ExpenseTransaction import ExpenseTransaction
    userid = sysmod.get_current_userid()
    conn = sysmod.db_connect()
    logger.debug("labels=", labels)
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        enddate_sql = "j.trandate <= '{0}'".format(end_date) if end_date is not None else ""
        startdate_sql = "j.trandate >= '{0}'".format(start_date) if start_date is not None else ""
        label_sql = "j.labels ~ '^{0}'".format("|".join("(?=.*" + str(i) + ")" for i in labels)) if len(labels) > 0 else ""
        conn_sql1 = " AND " if enddate_sql or startdate_sql or label_sql else ""
        conn_sql2 = " AND " if enddate_sql and (startdate_sql or label_sql) else ""
        conn_sql3 = " AND " if (enddate_sql or startdate_sql) and label_sql else ""
        sql = f"SELECT j.iid, j.tab_id, j.trandate AS {ExpenseTransaction.field_date()}, j.account_id AS {ExpenseTransaction.field_account()}, \
        j.amount AS {ExpenseTransaction.field_amount()}, j.labels AS {ExpenseTransaction.field_labels()}, j.remarks AS {ExpenseTransaction.field_remarks()}, \
        j.stmt_dtl AS {ExpenseTransaction.field_statement_detail()} FROM {Database.SCHEMA_FIN}.exp_transactions j, {Database.SCHEMA_FIN}.expensetab t \
        WHERE t.userid = {userid} AND t.tab_id = j.tab_id {conn_sql1} {enddate_sql} {conn_sql2} \
        {startdate_sql} {conn_sql3} {label_sql} ORDER BY j.trandate DESC, j.iid ASC"
        cur.execute(sql)
        logger.debug(f"cur.query (rowcount)={cur.query} ({cur.rowcount})")
        rows = cur.fetchall()
        rows = Helper.upper_dict_keys(rows, ExpenseTransaction.get_data_transform_definition())
        logger.trace("rows=", rows)
        cur.close()
    return list(rows)

def format_accounts_labels(rows):
    DL = Helper.to_dict_of_list(rows)
    return rows

@anvil.server.callable("proc_search_expense_list")
@logger.log_function
def proc_search_expense_list(start_date, end_date, labels=[]):
    rows = select_transactions_filter_by_labels(start_date, end_date, labels)
    result = format_accounts_labels(rows)
    return result