import anvil.server
import psycopg2
import psycopg2.extras
from .. import SystemProcess as sys
from ..Entities.Account import Account
from ..ServerUtils.LoggingModule import ServerLogger
from ..Utils.Constants import Database

# This is a server module. It runs on the Anvil server,
# rather than in the user's browser.
logger = ServerLogger()

# For callable decorator to be used with other decorator, refer to following,
# https://anvil.works/forum/t/fixed-multiple-decorators-in-forms/3582/5
@anvil.server.callable("generate_accounts_list")
@logger.log_function
def generate_accounts_list():
    """
    Select accounts detail from the accounts DB table.

    Returns:
        rows (list of RealDictRow): A list of accounts detail.
    """
    userid = sys.get_current_userid()
    conn = sys.db_connect()
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        sql = "SELECT * FROM {schema}.accounts WHERE userid = {userid} ORDER BY status ASC, valid_from DESC, valid_to DESC, id DESC".format(
            schema=Database.SCHEMA_FIN,
            userid=userid
        )
        cur.execute(sql)
        rows = cur.fetchall()
        logger.trace("rows=", rows)
        cur.close()
    return rows

@anvil.server.callable("select_account")
@logger.log_function
def select_account(selected_acct):
    """
    Select one particular account attributes from a DB table which stores accounts' detail.

    Parameters:
        selected_acct (int): The ID of a selected account.

    Returns:
        acct (Account): Account object corresponding to the selected account ID.
    """
    userid = sys.get_current_userid()
    conn = sys.db_connect()
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        sql = "SELECT * FROM {schema}.accounts WHERE id=%s".format(
            schema=Database.SCHEMA_FIN
        )
        stmt = cur.mogrify(sql, (selected_acct, ))
        cur.execute(stmt)
        row = cur.fetchone()
        logger.trace("row=", row)
        cur.close()
        acct = Account(row).set_user_id(userid) if row else None
        return acct

@anvil.server.callable("create_account")
@logger.log_function
def create_account(account):
    """
    Create a new account into the account DB table.

    In a successful update, a newly created account with new ID will be returned.
    
    Parameters:
        account (Account): The to-be-created account object.

    Returns:
        row['id'] (int): The newly created account's ID, otherwise None.
    """
    try:
        cur, conn = [None]*2
        if isinstance(account, Account):
            userid = sys.get_current_userid()
            conn = sys.db_connect()
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                sql = "INSERT INTO {schema}.accounts (userid, name, ccy, valid_from, valid_to, status) VALUES (%s,%s,%s,%s,%s,%s) RETURNING id".format(
                    schema=Database.SCHEMA_FIN
                )
                stmt = cur.mogrify(sql, (userid, account.get_name(), account.get_base_currency(), account.get_valid_datefrom(), account.get_valid_dateto(), account.get_status()))
                cur.execute(stmt)
                conn.commit()
                logger.debug(f"cur.query (rowcount)={cur.query} ({cur.rowcount})")
                row = cur.fetchone()
                if row['id'] < 0: raise psycopg2.OperationalError("Account [{0}] creation fail.".format(account.get_name()))
                return row['id']
        raise TypeError(f'The parameter is not an Account object.')
    except psycopg2.OperationalError as err:
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
        rows (list of int): A list of successful created accounts IDs, otherwise None.
    """
    userid = sys.get_current_userid()
    try:
        conn = sys.db_connect()
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
    except psycopg2.OperationalError as err:
        logger.error(err)
        conn.rollback()
    finally:
        if cur is not None: cur.close()
        if conn is not None: conn.close()
    return None

@anvil.server.callable("update_account")
@logger.log_function
def update_account(account):
    """
    Update an existing account change into the account DB table.

    Row count returned larger than 0 is considered as a successful update. 
    
    Parameters:
        account (Account): The to-be-updated account object.

    Returns:
        cur.rowcount (int): Successful update row count, otherwise None.
    """
    try:
        cur, conn = [None]*2
        if isinstance(account, Account):
            conn = sys.db_connect()
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                sql = "UPDATE {schema}.accounts SET name=%s, ccy=%s, valid_from=%s, valid_to=%s, status=%s WHERE id=%s".format(
                    schema=Database.SCHEMA_FIN
                )
                stmt = cur.mogrify(sql, (account.get_name(), account.get_base_currency(), account.get_valid_datefrom(), account.get_valid_dateto(), account.get_status(), account.get_id()))
                cur.execute(stmt)
                conn.commit()
                logger.debug(f"cur.query (rowcount)={cur.query} ({cur.rowcount})")
                if cur.rowcount <= 0: raise psycopg2.OperationalError("Account [{0}] update fail.".format(account.get_name()))
                return cur.rowcount
        raise TypeError(f'The parameter is not an Account object.')
    except psycopg2.OperationalError as err:
        logger.error(err)
        conn.rollback()
    finally:
        if cur is not None: cur.close()
        if conn is not None: conn.close()
    return None

@anvil.server.callable("delete_account")
@logger.log_function
def delete_account(account):
    """
    Delete an account from the account DB table.

    Row count returned larger than 0 is considered as a successful update.
    
    Parameters:
        account (Account): The to-be-deleted account object.

    Returns:
        cur.rowcount (int): Successful update row count, otherwise None
    """
    try:
        cur, conn = [None]*2
        if isinstance(account, Account):
            conn = sys.db_connect()
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                sql = "DELETE FROM {schema}.accounts WHERE id=%s".format(
                    schema=Database.SCHEMA_FIN
                )
                stmt = cur.mogrify(sql, (account.get_id(), ))
                cur.execute(stmt)
                conn.commit()
                logger.debug(f"cur.query (rowcount)={cur.query} ({cur.rowcount})")
                if cur.rowcount <= 0: raise psycopg2.OperationalError("Account [{0}] deletion fail.".format(account.get_name()))
                return cur.rowcount
        raise TypeError(f'The parameter is not an Account object.')
    except psycopg2.OperationalError as err:
        logger.error(err)
        conn.rollback()
    finally:
        if cur is not None: cur.close()
        if conn is not None: conn.close()
    return None
