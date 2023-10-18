import anvil.server
import psycopg2
import psycopg2.extras
from fuzzywuzzy import fuzz
from ..Entities.Label import Label
from ..ServerUtils import HelperModule as helper
from ..SysProcess import SystemModule as sysmod
from ..SysProcess import LoggingModule
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
    return rows

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

@anvil.server.callable("select_label")
@logger.log_function
def select_label(selected_lbl):
    """
    Select one particular label attributes from a DB table which stores labels' detail based on a selected label.

    Parameters:
        selected_lbl (int): The selected label ID.

    Returns:
        lbl (Label): Label object corresponding to the selected label ID.
    """
    userid = sysmod.get_current_userid()
    conn = sysmod.db_connect()
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        sql = "SELECT * FROM {schema}.labels WHERE userid = {userid} AND id=%s".format(
            schema=Database.SCHEMA_FIN,
            userid=userid
        )
        stmt = cur.mogrify(sql, (selected_lbl, ))
        cur.execute(stmt)
        row = cur.fetchone()
        logger.trace("row=", row)
        cur.close()
        lbl = Label(row).set_user_id(userid)
        return lbl
        
@anvil.server.callable("create_label")
@logger.log_function
def create_label(labels):
    """
    Create a new label into the label DB table.

    Parameters:
        labels (list of Label): The to-be-created label objects.

    Returns:
        rows (list of int): A list of successful created label IDs, otherwise None.
    """
    try:
        cur, conn = [None]*2
        if isinstance(labels, Label):
            list_lbl = [labels]
        elif isinstance(labels, (list, tuple)):
            list_lbl = labels
        else:
            raise TypeError(f'The parameter is neither Label object or a list of Label objects.')
        userid = sysmod.get_current_userid()
        conn = sysmod.db_connect()
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            if len(list_lbl) > 0:
                mogstr = ', '.join(cur.mogrify("(%s, %s, %s, %s)", (userid, label.get_name(), label.get_keywords(), label.get_status())).decode('utf-8') for label in list_lbl)
                stmt = f"INSERT INTO {Database.SCHEMA_FIN}.labels (userid, name, keywords, status) VALUES %s RETURNING id"
                cur.execute(stmt % mogstr)
                conn.commit()
                rows = cur.fetchall()
                logger.debug(f"cur.query (rowcount)={cur.query} ({cur.rowcount})")
                if not rows: raise psycopg2.OperationalError("Label [{0}] create fail.".format(label.get_name()))
                return [r['id'] for r in rows]
            else:
                return []
    except psycopg2.OperationalError as err:
        logger.error(err)
        conn.rollback()
    finally:
        if cur is not None: cur.close()
        if conn is not None: conn.close()
    return None

@anvil.server.callable("update_label")
@logger.log_function
def update_label(label):
    """
    Update existing label into the DB table which stores labels' detail.

    Parameters:
        label (Label): The to-be-updated label object.

    Returns:
        cur.rowcount (int): Successful update row count, otherwise None.
    """
    try:
        cur, conn = [None]*2
        if isinstance(label, Label):
            conn = sysmod.db_connect()
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                sql = "UPDATE {schema}.labels SET name=%s, keywords=%s, status=%s WHERE id=%s".format(
                    schema=Database.SCHEMA_FIN
                )
                stmt = cur.mogrify(sql, (label.get_name(), label.get_keywords(), label.get_status(), label.get_id()))
                cur.execute(stmt)
                conn.commit()
                logger.debug(f"cur.query (rowcount)={cur.query} ({cur.rowcount})")
                if cur.rowcount <= 0: raise psycopg2.OperationalError("Label [{0}] update fail.".format(label.get_name()))
                return cur.rowcount
        raise TypeError(f'The parameter is not a Label object.')
    except psycopg2.OperationalError as err:
        logger.error(err)
        conn.rollback()
    finally:
        if cur is not None: cur.close()
        if conn is not None: conn.close()
    return None

@anvil.server.callable("delete_label")
@logger.log_function
def delete_label(label):
    """
    Delete a label from the label DB table.

    Parameters:
        label (Label): The to-be-deleted label object.

    Returns:
        cur.rowcount (int): Successful delete row count, otherwise None.
    """
    try:
        cur, conn = [None]*2
        if isinstance(label, Label):
            conn = sysmod.db_connect()
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                sql = "DELETE FROM {schema}.labels WHERE id=%s".format(
                    schema=Database.SCHEMA_FIN
                )
                stmt = cur.mogrify(sql, (label.get_id(), ))
                cur.execute(stmt)
                conn.commit()
                logger.debug(f"cur.query (rowcount)={cur.query} ({cur.rowcount})")
                if cur.rowcount <= 0: raise psycopg2.OperationalError("Label [{0}] deletion fail.".format(label.get_name()))
                return cur.rowcount
        raise TypeError(f'The parameter is not a Label object.')
    except psycopg2.OperationalError as err:
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