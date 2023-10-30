import anvil.server
import psycopg2
import psycopg2.extras
from ..SysProcess import SystemModule as sysmod
from ..SysProcess import LoggingModule
from ..Utils import Helper
from ..Utils.Constants import Database

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
