import anvil.secrets
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
import psycopg2
import psycopg2.extras
from ..System import SystemModule as sysmod
from ..System.LoggingModule import trace, debug, info, warning, error, critical
from fuzzywuzzy import fuzz

# This is a server module. It runs on the Anvil server,
# rather than in the user's browser.

# Generate labels dropdown items
@anvil.server.callable("generate_labels_dropdown")
@debug.log_function
def generate_labels_dropdown():
    userid = sysmod.get_current_userid()
    conn = sysmod.db_connect()
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute(f"SELECT * FROM {sysmod.schemafin()}.labels WHERE userid = {userid} ORDER BY name ASC")
        rows = cur.fetchall()
        cur.close()
    # Case 001 - string dict key handling review
    content = list((row['name'] + " (" + str(row['id']) + ")", repr({"id": row['id'], "text": row['name']})) for row in rows)
    return content

# Generate labels into list
@anvil.server.callable("generate_labels_list")
@debug.log_function
def generate_labels_list():
    userid = sysmod.get_current_userid()
    conn = sysmod.db_connect()
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute(f"SELECT * FROM {sysmod.schemafin()}.labels WHERE userid = {userid} ORDER BY name ASC")
        rows = cur.fetchall()
        cur.close()
    return list({"id": row['id'], "name": row['name'], "status": row['status']} for row in rows)

# Get selected label attributes
@anvil.server.callable("get_selected_label_attr")
@debug.log_function
def get_selected_label_attr(selected_lbl):
    userid = sysmod.get_current_userid()
    if selected_lbl is None or selected_lbl == '':
        return [None, None, None, True]
    else:
        conn = sysmod.db_connect()
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            sql = f"SELECT * FROM {sysmod.schemafin()}.labels WHERE userid = {userid} AND id=%s"  
            stmt = cur.mogrify(sql, (selected_lbl, ))
            cur.execute(stmt)
            row = cur.fetchone()
            cur.close()
        return [row['id'], row['name'], row['keywords'], row['status']]

# Generate labels dropdown items
@anvil.server.callable("generate_labels_mapping_action_dropdown")
@debug.log_function
def generate_labels_mapping_action_dropdown():
    conn = sysmod.db_connect()
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute(f"SELECT * FROM {sysmod.schemarefd()}.label_mapping_action ORDER BY seq ASC")
        rows = cur.fetchall()
        cur.close()
    content = list((row['action'], [row['id'], row['action']]) for row in rows)
    return content

# Create label
@anvil.server.callable("create_label")
@debug.log_function
def create_label(labels):
    userid = sysmod.get_current_userid()
    try:
        conn = sysmod.db_connect()
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            if len(labels) > 0:
                mogstr = ', '.join(cur.mogrify("(%s, %s, %s, %s)", (userid, label['name'], label['keywords'], label['status'])).decode('utf-8') for label in labels)
                stmt = f"INSERT INTO {sysmod.schemafin()}.labels (userid, name, keywords, status) VALUES %s RETURNING id"
                cur.execute(stmt % mogstr)
                conn.commit()
                debug.log(f"cur.query (rowcount)={cur.query} ({cur.rowcount})")
                return [r['id'] for r in cur.fetchall()]
            else:
                return []
    except (Exception, psycopg2.OperationalError) as err:
        error.log(f"{__name__}.{type(err).__name__}: {err}")
        conn.rollback()
    finally:
        if cur is not None: cur.close()
        if conn is not None: conn.close()
    return None

# Update label
@anvil.server.callable("update_label")
@debug.log_function
def update_label(id, name, keywords, status):
    try:
        conn = sysmod.db_connect()
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            sql = f"UPDATE {sysmod.schemafin()}.labels SET name=%s, keywords=%s, status=%s WHERE id=%s"
            stmt = cur.mogrify(sql, (name, keywords, status, id))
            cur.execute(stmt)
            conn.commit()
            debug.log(f"cur.query (rowcount)={cur.query} ({cur.rowcount})")
            if cur.rowcount <= 0: raise psycopg2.OperationalError("Label ({0}) update fail.".format(name))
            return cur.rowcount
    except (Exception, psycopg2.OperationalError) as err:
        error.log(f"{__name__}.{type(err).__name__}: {err}")
        conn.rollback()
    finally:
        if cur is not None: cur.close()
        if conn is not None: conn.close()
    return None

# Delete label
@anvil.server.callable("delete_label")
@debug.log_function
def delete_label(id):
    try:
        conn = sysmod.db_connect()
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            sql = f"DELETE FROM {sysmod.schemafin()}.labels WHERE id=%s"
            stmt = cur.mogrify(sql, (id, ))
            cur.execute(stmt)
            conn.commit()
            debug.log(f"cur.query (rowcount)={cur.query} ({cur.rowcount})")
            if cur.rowcount <= 0: raise psycopg2.OperationalError("Label ({0}) deletion fail.".format(name))
            return cur.rowcount
    except (Exception, psycopg2.OperationalError) as err:
        error.log(f"{__name__}.{type(err).__name__}: {err}")
        conn.rollback()
    finally:
        if cur is not None: cur.close()
        if conn is not None: conn.close()
    return None

@anvil.server.callable("predict_relevant_labels")
@debug.log_function
def predict_relevant_labels(srclbl, curlbl):
    # Max 100, min 0
    min_proximity = 40
    score = []
    for s in srclbl:
        highscore = [0, None]
        for lbl in curlbl:
            similarity = fuzz.ratio(s, curlbl[lbl])
            debug.log(f"lbl={lbl}, similarity={similarity}, highscore[0]={highscore[0]}")
            if similarity > highscore[0]:
                highscore = [similarity, {'id': int(lbl), 'text': curlbl[lbl]}]
        score.append(highscore[1] if highscore[0] > min_proximity else None)
    return score