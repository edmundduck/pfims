import anvil.secrets
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
import psycopg2
import psycopg2.extras
from datetime import date, datetime, timedelta
from ..Utils import Constants as const
from ..System import SystemModule as sysmod

# This is a server module. It runs on the Anvil server,
# rather than in the user's browser.

# Static variables

# Internal function - Return start date of last 1 month
def get_L1M_start_date(end_date):
    return date(end_date.year-1, end_date.month+12-1, end_date.day) if end_date.month-1 < 1 else date(end_date.year, end_date.month-1, end_date.day)

# Internal function - Return start date of last 3 months
def get_L3M_start_date(end_date):
    return date(end_date.year-1, end_date.month+12-3, end_date.day) if end_date.month-3 < 1 else date(end_date.year, end_date.month-3, end_date.day)

# Internal function - Return start date of last 6 months
def get_L6M_start_date(end_date):
    return date(end_date.year-1, end_date.month+12-6, end_date.day) if end_date.month-6 < 1 else date(end_date.year, end_date.month-6, end_date.day)

# Internal function - Return start date of last 1 year
def get_L1Y_start_date(end_date):
    return date(end_date.year-1, end_date.month, end_date.day)

# Internal function - Return the 1st date of the current year
def get_YTD_start_date(end_date):
    return date(end_date.year, 1, 1)

# Internal function - Return None if it's not date
def interval_default(end_date):
    return None

@anvil.server.callable
# Get all symbols which were transacted between start and end date into the dropdown
def get_symbol_dropdown_items(start_date, end_date=date.today()):
    return list(sorted(set(row['symbol'] for row in select_journals(start_date, end_date))))

@anvil.server.callable
# Get start date based on end date and time interval dropdown value
def get_start_date(end_date, interval):
    switcher = {
        const.SearchInterval.INTERVAL_LAST_1_MTH: get_L1M_start_date,
        const.SearchInterval.INTERVAL_LAST_3_MTH: get_L3M_start_date,
        const.SearchInterval.INTERVAL_LAST_6_MTH: get_L6M_start_date,
        const.SearchInterval.INTERVAL_LAST_1_YR: get_L1Y_start_date,
        const.SearchInterval.INTERVAL_YEAR_TO_DATE: get_YTD_start_date,
    }
    return switcher.get(interval, interval_default)(end_date)

@anvil.server.callable
# Return journals for repeating panel to display based on sell and buy date criteria
def select_journals(start_date, end_date, symbols=[]):
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
        j.sell_price, j.buy_price, j.pnl FROM {sysmod.schemafin()}.templ_journals j, {sysmod.schemafin()}.templates t \
        WHERE t.userid = {userid} AND t.template_id = j.template_id {conn_sql1} {sell_sql} {conn_sql2} \
        {buy_sql} {conn_sql3} {symbol_sql} ORDER BY sell_date DESC, symbol ASC"
        cur.execute(sql)
        rows = cur.fetchall()
        cur.close()
    return list(rows)

@anvil.server.callable
# Return template journals for csv generation
def generate_csv(start_date, end_date, symbols):
    return select_journals(start_date, end_date, symbols).to_csv()

# Internal function - Format P&L dictionary
# rowitem = Items in rows returned from DB table 'templ_journals' search result
def format_pnl_dict(rowitem, dictupdate, key, mode):
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

# Internal function - Format a parent: child mapping into dictionary
def format_pnl_child(dictupdate, parent, child):
    childset = dictupdate.get(parent, set())
    childset.add(child)
    dictupdate.update({parent: childset})
  
# Internal function - Load DB table 'templ_journals' to build 3 P&L data dictionaries - day, month, year
def build_pnl_data(start_date, end_date, symbols):
    userid = sysmod.get_current_userid()
    # rows = None
    # if len(symbols) > 0:
    #     rows = app_tables.templ_journals.search(
    #         sell_date=q.less_than_or_equal_to(end_date), 
    #         buy_date=q.greater_than_or_equal_to(start_date),
    #         symbol=q.any_of(*symbols))
    # else:
    #     rows = app_tables.templ_journals.search(sell_date=q.between(start_date, end_date, max_inclusive=True))
    rows = select_journals(userid, start_date, end_date, symbols)
    
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
        # Debug
        #print("sell={} / buy={} / diff={}".format(i['sell_date'], i['buy_date'], (i['sell_date']-i['buy_date']).days))
        
        # Handling of Day
        format_pnl_dict(i, dictstruct_day, sell_date_str, const.PNLDrillMode.DAY)
        # Handling of Month
        format_pnl_dict(i, dictstruct_mth, sell_mth_str, const.PNLDrillMode.MONTH)
        # Handling of Year
        format_pnl_dict(i, dictstruct_yr, sell_yr_str, const.PNLDrillMode.YEAR)
        # Handling parent:child relationship dict
        format_pnl_child(dictstruct_child, sell_mth_str, sell_date_str)
        format_pnl_child(dictstruct_child, sell_yr_str, sell_mth_str)
        format_pnl_child(dictstruct_gchild, sell_yr_str, sell_date_str)

    # Debug
    #sysmod.print_data_debug('dictstruct_day', dictstruct_day)
    #sysmod.print_data_debug('dictstruct_mth', dictstruct_mth)
    #sysmod.print_data_debug('dictstruct_yr', dictstruct_yr)
    #sysmod.print_data_debug('dictstruct_child', dictstruct_child)
    #sysmod.print_data_debug('dictstruct_gchild', dictstruct_gchild)
    return dictstruct_day, dictstruct_mth, dictstruct_yr, dictstruct_child, dictstruct_gchild

@anvil.server.callable
# Generate initial P&L list (year only)
def generate_init_pnl_list(start_date, end_date, symbols):
    userid = sysmod.get_current_userid()
    rowstruct = []
    
    dictstruct_day, dictstruct_mth, dictstruct_yr, dictstruct_child, dictstruct_gchild = build_pnl_data(userid, start_date, end_date, symbols)
    
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
            'action': const.Icons.DATA_DRILLDOWN
        }
        rowstruct += [dictitem]
    
    return sorted(rowstruct, key=lambda x: x.get('sell_date'))

@anvil.server.callable
# Update P&L data according to expand/shrink action and reformat into repeatingpanel compatible data (dict in list)
def update_pnl_list(start_date, end_date, symbols, pnl_list, date_value, mode, action):
    userid = sysmod.get_current_userid()
    # Debug
    #print("param list={} / {} / {} / {} / {} / {} / {}".format(start_date, end_date, symbols, pnl_list, date_value, mode, action))
    
    rowstruct = []
    dictstruct_day, dictstruct_mth, dictstruct_yr, dictstruct_child, dictstruct_gchild = build_pnl_data(userid, start_date, end_date, symbols)
    # Debug
    #sysmod.print_data_debug('dictstruct_day', dictstruct_day)
    #sysmod.print_data_debug('dictstruct_mth', dictstruct_mth)
    #sysmod.print_data_debug('dictstruct_yr', dictstruct_yr)
    #sysmod.print_data_debug('dictstruct_child', dictstruct_child)
    #sysmod.print_data_debug('dictstruct_gchild', dictstruct_gchild)
    
    if action == const.Icons.DATA_DRILLDOWN:
        dictstruct = None
        childaction = ''
        rowstruct = pnl_list
        
        if mode == const.PNLDrillMode.YEAR:
            dictstruct = dictstruct_mth
            childaction = const.Icons.DATA_DRILLDOWN
        elif mode == const.PNLDrillMode.MONTH:
            dictstruct = dictstruct_day
      
        # Update action from plus to minus
        for rowitem in rowstruct:
            if rowitem['sell_date'] == date_value:
                rowstruct.remove(rowitem)
                rowitem['action'] = const.Icons.DATA_SUMMARIZE
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
    elif action == const.Icons.DATA_SUMMARIZE:
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
                rowitem['action'] = const.Icons.DATA_DRILLDOWN
                rowstruct = rowstruct + [rowitem]
    else:
        pass
  
    return sorted(rowstruct, key=lambda x: x.get('sell_date'))
  
