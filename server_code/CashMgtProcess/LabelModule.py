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
from ..ServerUtils import HelperModule as helper
from ..SysProcess import SystemModule as sysmod
from ..SysProcess import LoggingModule
from fuzzywuzzy import fuzz
from ..Utils.Constants import Database

# This is a server module. It runs on the Anvil server,
# rather than in the user's browser.
logger = LoggingModule.ServerLogger()

@anvil.server.callable("generate_labels_list")
@logger.log_function
def generate_labels_list():
    """
    Select labels detail from the labels DB table.

    Returns:
        rows (list of RealDictRow): A list of labels detail.
    """
    userid = sysmod.get_current_userid()
    conn = sysmod.db_connect()
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute(f"SELECT * FROM {Database.SCHEMA_FIN}.labels WHERE userid = {userid} ORDER BY name ASC")
        rows = cur.fetchall()
        cur.close()
    content = list((row['name'] + " (" + str(row['id']) + ")", (row['id'], row['name'])) for row in rows)
    return content

@anvil.server.callable("generate_labels_dict_of_list")
@logger.log_function
def generate_labels_dict_of_list():
    """
    Select data from a DB table which stores labels' detail as transformed dictionary of list.

    Returns:
        dict: A dictionary of each column as key, where value is the list of the data belonging to that particular column.
    """
    userid = sysmod.get_current_userid()
    conn = sysmod.db_connect()
    with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
        cur.execute(f"SELECT * FROM {Database.SCHEMA_FIN}.labels WHERE userid = {userid} ORDER BY name ASC")
        rows = cur.fetchall()
        cur.close()
    return helper.to_dict_of_list(rows)

@anvil.server.callable("get_selected_label_attr")
@logger.log_function
def get_selected_label_attr(selected_lbl):
    """
    Select corresponding data from a DB table which stores labels' detail based on a selected label.

    Parameters:
        selected_lbl (int): The selected label ID.

    Returns:
        list: A list of label ID, name, keywords and status based on a selected label.
    """
    userid = sysmod.get_current_userid()
    if selected_lbl is None or selected_lbl == '':
        return [None, None, None, True]
    else:
        conn = sysmod.db_connect()
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            sql = f"SELECT * FROM {Database.SCHEMA_FIN}.labels WHERE userid = {userid} AND id=%s"  
            stmt = cur.mogrify(sql, (selected_lbl, ))
            cur.execute(stmt)
            row = cur.fetchone()
            cur.close()
        return [row['id'], row['name'], row['keywords'], row['status']]

@anvil.server.callable("generate_labels_mapping_action_dropdown")
@logger.log_function
def generate_labels_mapping_action_dropdown():
    """
    Select data from the DB table which stores label mapping actions' detail to generate a dropdown list.

    Returns:
        content (list): A list of label mapping action name as description, and ID and name as ID.
    """
    conn = sysmod.db_connect()
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute(f"SELECT * FROM {Database.SCHEMA_REFDATA}.label_mapping_action ORDER BY seq ASC")
        rows = cur.fetchall()
        cur.close()
    content = list((row['action'], [row['id'], row['action']]) for row in rows)
    return content

@anvil.server.callable("create_label")
@logger.log_function
def create_label(labels):
    """
    Create new label into the DB table which stores labels' detail.

    Parameters:
        labels (list of dict): Contains label name, its keywords and status.

    Returns:
        list: A list of successful created label IDs, otherwise None.
    """
    userid = sysmod.get_current_userid()
    try:
        conn = sysmod.db_connect()
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            if len(labels) > 0:
                mogstr = ', '.join(cur.mogrify("(%s, %s, %s, %s)", (userid, label['name'], label['keywords'], label['status'])).decode('utf-8') for label in labels)
                stmt = f"INSERT INTO {Database.SCHEMA_FIN}.labels (userid, name, keywords, status) VALUES %s RETURNING id"
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

@anvil.server.callable("update_label")
@logger.log_function
def update_label(id, name, keywords, status):
    """
    Update existing label into the DB table which stores labels' detail.

    Parameters:
        id (int): The label ID to be updated.
        name (string): The label name to be updated.
        keywords (list): The keywords relevant to the label.
        status (boolean): The active status of the label.

    Returns:
        cur.rowcount (int): Successful update row count, otherwise None.
    """
    try:
        conn = sysmod.db_connect()
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            sql = f"UPDATE {Database.SCHEMA_FIN}.labels SET name=%s, keywords=%s, status=%s WHERE id=%s"
            stmt = cur.mogrify(sql, (name, keywords, status, id))
            cur.execute(stmt)
            conn.commit()
            logger.debug(f"cur.query (rowcount)={cur.query} ({cur.rowcount})")
            if cur.rowcount <= 0: raise psycopg2.OperationalError("Label ({0}) update fail.".format(name))
            return cur.rowcount
    except (Exception, psycopg2.OperationalError) as err:
        logger.error(err)
        conn.rollback()
    finally:
        if cur is not None: cur.close()
        if conn is not None: conn.close()
    return None

@anvil.server.callable("delete_label")
@logger.log_function
def delete_label(id):
    """
    Delete a label from the DB table which stores labels' detail.

    Parameters:
        id (int): The label ID to be deleted.

    Returns:
        cur.rowcount (int): Successful delete row count, otherwise None.
    """
    try:
        conn = sysmod.db_connect()
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            sql = f"DELETE FROM {Database.SCHEMA_FIN}.labels WHERE id=%s"
            stmt = cur.mogrify(sql, (id, ))
            cur.execute(stmt)
            conn.commit()
            logger.debug(f"cur.query (rowcount)={cur.query} ({cur.rowcount})")
            if cur.rowcount <= 0: raise psycopg2.OperationalError("Label ({0}) deletion fail.".format(name))
            return cur.rowcount
    except (Exception, psycopg2.OperationalError) as err:
        logger.error(err)
        conn.rollback()
    finally:
        if cur is not None: cur.close()
        if conn is not None: conn.close()
    return None

@anvil.server.callable("predict_relevant_labels")
@logger.log_function
def predict_relevant_labels(srclbl, curlbl):
    """
    Return a label which has the highest proximity (a.k.a. the most matched) from the DB from the source label.

    Parameters:
        srclbl (list): The labels extracted from Excel to be compared.
        curlbl (list): The label dropdown from the DB labels table.

    Returns:
        score (list): Proximity score of each label, its order follows the order of the srclbl.
    """
    # Max 100, min 0
    min_proximity = 40
    score = []
    for s in srclbl:
        highscore = [0, None]
        for lbl in curlbl:
            similarity = fuzz.ratio(s, lbl[1][1])
            logger.trace(f"lbl={lbl[1][1]}, similarity={similarity}, highscore[0]={highscore[0]}")
            if similarity > highscore[0]:
                highscore = [similarity, [lbl[1][0], lbl[1][1]]]
        score.append(highscore[1] if highscore[0] > min_proximity else None)
    return score