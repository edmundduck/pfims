import anvil.server
import psycopg2
import psycopg2.extras
from .. import SystemProcess as sys
from ..Entities.ExpenseTransaction import ExpenseTransaction
from ..ServerUtils.LoggingModule import ServerLogger
from ..Utils import Helper
from ..Utils.Constants import Database

# This is a server module. It runs on the Anvil server,
# rather than in the user's browser.

logger = ServerLogger()

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
    userid = sys.get_current_userid()
    conn = sys.db_connect()
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        mogstr_list = []
        where_clause_list = []
        where_clause2 = ''
        if end_date:
            mogstr_list.append(end_date)
            where_clause_list.append("AND j.sell_date <= %s ")
        if start_date:
            mogstr_list.append(start_date)
            where_clause_list.append("AND j.buy_date >= %s ")
        if len(symbols) > 0:
            where_clause2 = "AND j.symbol IN ({symbol_list}) ".format(symbol_list=','.join(cur.mogrify("%s", (d, )).decode('utf-8') for d in symbols))
        logger.trace("mogstr_list=", mogstr_list)
        logger.trace("where_clause_list=", where_clause_list)
        logger.trace("where_clause2=", where_clause2)
        sql = "SELECT j.iid, j.template_id, j.sell_date, j.buy_date, j.symbol, j.qty, j.sales, j.cost, j.fee, \
        j.sell_price, j.buy_price, j.pnl FROM {schema}.templ_journals j, {schema}.templates t WHERE t.userid = {userid} \
        AND t.template_id = j.template_id {where_clause1} {where_clause2} ORDER BY sell_date DESC, symbol ASC".format(
            schema=Database.SCHEMA_FIN,
            userid=userid,
            where_clause1=' '.join(where_clause_list),
            where_clause2=where_clause2
        )
        stmt = cur.mogrify(sql, mogstr_list)
        cur.execute(stmt)
        logger.debug(f"cur.query (rowcount)={cur.query} ({cur.rowcount})")
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
    userid = sys.get_current_userid()
    conn = sys.db_connect()
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        mogstr_list = []
        where_clause_list = []
        where_clause2 = ''
        if end_date:
            mogstr_list.append(str(end_date))
            where_clause_list.append("AND j.trandate <= %s ")
        if start_date:
            mogstr_list.append(str(start_date))
            where_clause_list.append("AND j.trandate >= %s ")
        if len(labels) > 0:
            # where_clause2 = "AND j.labels ~ '^{0}' ".format("|".join("(?=.*" + str(i) + ")" for i in labels))
            # ==============================
            where_clause2 = "AND ({0}) ".format(' OR '.join(f"{i} = ANY(j.labels)" for i in labels))
        logger.trace("mogstr_list=", mogstr_list)
        logger.trace("where_clause_list=", where_clause_list)
        logger.trace("where_clause2=", where_clause2)
        sql = "SELECT j.iid, j.tab_id, j.trandate AS {trandate}, j.account_id AS {account_id}, j.amount AS {amount}, j.labels AS {labels}, \
        j.remarks AS {remarks}, j.stmt_dtl AS {stmt_dtl} FROM {schema}.exp_transactions j, {schema}.expensetab t WHERE t.userid = {userid} \
        AND t.tab_id = j.tab_id {where_clause1} {where_clause2} ORDER BY j.trandate DESC, j.iid ASC".format(
            schema=Database.SCHEMA_FIN,
            userid=userid,
            trandate=ExpenseTransaction.field_date(),
            account_id=ExpenseTransaction.field_account(),
            amount=ExpenseTransaction.field_amount(),
            labels=ExpenseTransaction.field_labels(),
            remarks=ExpenseTransaction.field_remarks(),
            stmt_dtl=ExpenseTransaction.field_statement_detail(),
            where_clause1=' '.join(where_clause_list),
            where_clause2=where_clause2
        )
        stmt = cur.mogrify(sql, mogstr_list)
        cur.execute(stmt)
        logger.debug(f"cur.query (rowcount)={cur.query} ({cur.rowcount})")
        rows = cur.fetchall()
        rows = Helper.upper_dict_keys(rows, ExpenseTransaction.get_data_transform_definition())
        cur.close()
        return list(rows)

@logger.log_function
def select_summed_total_per_labels(start_date, end_date, labels=[]):
    """
    Return summed total of each label based on transaction date criteria.

    Parameters:
        start_date (date): Start date of the search.
        end_date (date): End date of the search.
        labels (list): List of selected labels.

    Returns:
        rows (list of RealDictRow): Summed total in list.
    """
    userid = sys.get_current_userid()
    conn = sys.db_connect()
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        mogstr_list = []
        where_clause_list = []
        where_clause2 = ''
        if end_date:
            mogstr_list.append(str(end_date))
            where_clause_list.append("AND j.trandate <= %s ")
        if start_date:
            mogstr_list.append(str(start_date))
            where_clause_list.append("AND j.trandate >= %s ")
        if len(labels) > 0:
            # where_clause2 = "AND j.labels ~ '^{0}' ".format("|".join("(?=.*" + str(i) + ")" for i in labels))
            where_clause2 = "AND {labels} IN ({lbl_id}) ".format(
                labels=ExpenseTransaction.field_labels(),
                lbl_id=','.join(str(i) for i in labels)
            )
        logger.trace("mogstr_list=", mogstr_list)
        logger.trace("where_clause_list=", where_clause_list)
        logger.trace("where_clause2=", where_clause2)
        sql = "SELECT {labels}, y.name, {amount} FROM (SELECT UNNEST(j.labels) AS {labels}, SUM(j.amount) AS {amount} FROM {schema}.exp_transactions j, {schema}.expensetab t \
        WHERE t.userid = {userid} AND t.tab_id = j.tab_id {where_clause1} GROUP BY UNNEST(j.labels)) x, (SELECT id, name FROM {schema}.labels) y WHERE x.{labels} = y.id \
        {where_clause2} ORDER BY {labels} ASC".format(
            schema=Database.SCHEMA_FIN,
            userid=userid,
            labels=ExpenseTransaction.field_labels(),
            amount=ExpenseTransaction.field_amount(),
            where_clause1=' '.join(where_clause_list),
            where_clause2=where_clause2
        )
        stmt = cur.mogrify(sql, mogstr_list)
        cur.execute(stmt)
        logger.debug(f"cur.query (rowcount)={cur.query} ({cur.rowcount})")
        rows = cur.fetchall()
        rows = Helper.upper_dict_keys(rows, ExpenseTransaction.get_data_transform_definition())
        cur.close()
        return list(rows)

def select_label_names(label_id_list):
    """
    Return summed total of each label based on transaction date criteria.

    Parameters:
        label_id_list (list of int): List of selected label IDs.

    Returns:
        rows (list of RealDictRow): List of label IDs and names.
    """
    userid = sys.get_current_userid()
    conn = sys.db_connect()
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        sql = "SELECT id, name FROM {schema}.labels WHERE id in (%s) ORDER BY id ASC".format(
            schema=Database.SCHEMA_FIN,
        )
        # mogstr_list = ','.join(i for i in label_id_list)
        # stmt = cur.mogrify(sql, mogstr_list)
        cur.execute(sql, label_id_list)
        logger.debug(f"cur.query (rowcount)={cur.query} ({cur.rowcount})")
        rows = cur.fetchall()
        cur.close()
        return list(rows)
