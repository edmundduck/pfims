import anvil.files
from anvil.files import data_files
import anvil.secrets
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
import psycopg2
import psycopg2.extras
from ..SysProcess import SystemModule as sysmod
from ..SysProcess import LoggingModule
from ..Utils.Constants import Database

# This is a server module. It runs on the Anvil server,
# rather than in the user's browser.
logger = LoggingModule.ServerLogger()

# For callable decorator to be used with other decorator, refer to following,
# https://anvil.works/forum/t/fixed-multiple-decorators-in-forms/3582/5
@anvil.server.callable("generate_accounts_dropdown")
@logger.log_function
def generate_accounts_dropdown():
    """
    Select accounts data from a DB table which stores accounts' detail to generate a dropdown list.

    Returns:
        list: A dropdown list of accounts names and IDs as description, and account names and IDs as ID.
    """
    userid = sysmod.get_current_userid()
    conn = sysmod.db_connect()
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute(f"SELECT * FROM {Database.SCHEMA_FIN}.accounts WHERE userid = {userid} ORDER BY status ASC, valid_from DESC, valid_to DESC, id DESC")
        rows = cur.fetchall()
        logger.trace("rows=", rows)
        cur.close()
    return list((row['name'] + " (" + str(row['id']) + ")", [row['id'], row['name']]) for row in rows)

@anvil.server.callable("generate_ccy_dropdown")
@logger.log_function
def generate_ccy_dropdown():
    """
    Select CCY data from a DB table which stores currencies' detail to generate a dropdown list.

    Not all currencies have symbols, so they can be empty.
    
    Returns:
        list: A dropdown list of currency abbreviations, names and symbols as description, and currency abbreviations as ID.
    """
    conn = sysmod.db_connect()
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute(f"SELECT * FROM {Database.SCHEMA_REFDATA}.ccy ORDER BY common_seq ASC, abbv ASC")
        rows = cur.fetchall()
        logger.trace("rows=", rows)
        cur.close()
    content = list((row['abbv'] + " " + row['name'] + " (" + row['symbol'] + ")" if row['symbol'] else row['abbv'] + " " + row['name'], row['abbv']) for row in rows)
    return content

@anvil.server.callable("get_selected_account_attr")
@logger.log_function
def get_selected_account_attr(selected_acct):
    """
    Select one particular account attributes from a DB table which stores accounts' detail.

    Parameters:
        selected_acct (int): The ID of a selected account.

    Returns:
        list: A row of accounts attributes including ID, name, base currency, date valid from, date valid to and status.
    """
    if selected_acct in (None, ''):
        return [None, None, None, None, None, True]
    else:
        conn = sysmod.db_connect()
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            sql = "SELECT * FROM {schema}.accounts WHERE id=%s".format(schema=Database.SCHEMA_FIN)  
            stmt = cur.mogrify(sql, (selected_acct, ))
            cur.execute(stmt)
            row = cur.fetchone()
            logger.trace("row=", row)
            cur.close()
        return [row['id'], row['name'], row['ccy'], row['valid_from'], row['valid_to'], row['status']]

@anvil.server.callable("create_account")
@logger.log_function
def create_account(name, ccy, valid_from, valid_to, status):
    """
    Create an account from account form to a DB table which stores accounts' detail.

    In a successful update, a newly created account with new ID will be returned.
    
    Parameters:
        name (str): The name of the account.
        ccy (str): The base currency of the account.
        valid_from (date): The date when account becomes valid.
        valid_to (date): The date when account is no longer valid.
        status (boolean): Current status of the account.

    Returns:
        id['id'] (int): The ID of the newly created or existing account, otherwise None
    """
    try:
        userid = sysmod.get_current_userid()
        conn = sysmod.db_connect()
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            sql = "INSERT INTO {schema}.accounts (userid, name, ccy, valid_from, valid_to, status) \
            VALUES (%s,%s,%s,%s,%s,%s) RETURNING id".format(schema=Database.SCHEMA_FIN)
            stmt = cur.mogrify(sql, (userid, name, ccy, valid_from, valid_to, status))
            cur.execute(stmt)
            conn.commit()
            logger.debug(f"cur.query (rowcount)={cur.query} ({cur.rowcount})")
            id = cur.fetchone()
            if id['id'] < 0: raise psycopg2.OperationalError("Account ({0}) creation fail.".format(name))
            return id['id']
    except (Exception, psycopg2.OperationalError) as err:
        logger.error(err)
        conn.rollback()
    finally:
        if cur is not None: cur.close()
        if conn is not None: conn.close()
    return None

@anvil.server.callable("create_multiple_accounts")
@logger.log_function
def create_multiple_accounts(accounts):
    """
    Create new multiple accounts into the DB table which stores accounts' detail.

    Parameters:
        accounts (list of dict): Contains list of account names and their attributes.

    Returns:
        list: A list of successful created account IDs, otherwise None.
    """
    userid = sysmod.get_current_userid()
    try:
        conn = sysmod.db_connect()
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            if len(accounts) > 0:
                mogstr = ', '.join(cur.mogrify("(%s, %s, %s, %s, %s, %s)", (userid, account['name'], account['ccy'], account['valid_from'], account['valid_to'], account['status'])).decode('utf-8') for account in accounts)
                stmt = f"INSERT INTO {Database.SCHEMA_FIN}.accounts (userid, name, ccy, valid_from, valid_to, status) VALUES %s RETURNING id"
                cur.execute(stmt % mogstr)
                conn.commit()
                logger.debug(f"cur.query (rowcount)={cur.query} ({cur.rowcount})")
                return [r['id'] for r in cur.fetchall()]
            else:
                return []
    except (Exception, psycopg2.OperationalError) as err:
        logger.error(err)
        conn.rollback()
    finally:
        if cur is not None: cur.close()
        if conn is not None: conn.close()
    return None

@anvil.server.callable("update_account")
@logger.log_function
def update_account(id, name, ccy, valid_from, valid_to, status):
    """
    Update an existing account from account form to a DB table which stores accounts' detail.

    Row count returned larger than 0 is considered as a successful update. 
    
    Parameters:
        id (int): The ID of the account.
        name (str): The name of the account.
        ccy (str): The base currency of the account.
        valid_from (date): The date when account becomes valid.
        valid_to (date): The date when account is no longer valid.
        status (boolean): Current status of the account.

    Returns:
        cur.rowcount (int): Successful update row count, otherwise None
    """
    try:
        conn = sysmod.db_connect()
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            sql = "UPDATE {schema}.accounts SET name=%s, ccy=%s, valid_from=%s, valid_to=%s, status=%s WHERE id=%s".format(schema=Database.SCHEMA_FIN)
            stmt = cur.mogrify(sql, (name, ccy, valid_from, valid_to, status, id))
            cur.execute(stmt)
            conn.commit()
            logger.debug(f"cur.query (rowcount)={cur.query} ({cur.rowcount})")
            if cur.rowcount <= 0: raise psycopg2.OperationalError("Account ({0}) update fail.".format(name))
            return cur.rowcount
    except (Exception, psycopg2.OperationalError) as err:
        logger.error(err)
        conn.rollback()
    finally:
        if cur is not None: cur.close()
        if conn is not None: conn.close()
    return None

@anvil.server.callable("delete_account")
@logger.log_function
def delete_account(id):
    """
    Delete an account from a DB table which stores accounts' detail.

    Row count returned larger than 0 is considered as a successful update.
    
    Parameters:
        id (int): The ID of the account.

    Returns:
        cur.rowcount (int): Successful update row count, otherwise None
    """
    try:
        conn = sysmod.db_connect()
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            sql = "DELETE FROM {schema}.accounts WHERE id=%s".format(schema=Database.SCHEMA_FIN)
            stmt = cur.mogrify(sql, (id, ))
            cur.execute(stmt)
            conn.commit()
            logger.debug(f"cur.query (rowcount)={cur.query} ({cur.rowcount})")
            if cur.rowcount <= 0: raise psycopg2.OperationalError("Account ({0}) deletion fail.".format(name))
            return cur.rowcount
    except (Exception, psycopg2.OperationalError) as err:
        logger.error(err)
        conn.rollback()
    finally:
        if cur is not None: cur.close()
        if conn is not None: conn.close()
    return None
