import anvil.secrets
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
import psycopg2
import psycopg2.extras
from ..System import SystemModule as sysmod
from fuzzywuzzy import fuzz

# This is a server module. It runs on the Anvil server,
# rather than in the user's browser.

@anvil.server.callable
# Generate labels dropdown items
def generate_labels_dropdown():
    conn = sysmod.psqldb_connect()
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        sql = "SELECT * FROM {schema}.labels ORDER BY name ASC".format(schema=sysmod.schemafin())
        cur.execute(sql)
        rows = cur.fetchall()
        cur.close()
    content = list((row['name'] + " (" + str(row['id']) + ")", {"id": row['id'], "text": row['name']}) for row in rows)
    return content

@anvil.server.callable
# Generate labels into list
def generate_labels_list():
    conn = sysmod.psqldb_connect()
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        sql = "SELECT * FROM {schema}.labels ORDER BY name ASC".format(schema=sysmod.schemafin())
        cur.execute(sql)
        rows = cur.fetchall()
        cur.close()
    content = list({
        "id": row['id'], 
        "name": row['name'], 
        "status": row['status']} for row in rows)
    return content

@anvil.server.callable
# Get selected label attributes
def get_selected_label_attr(selected_lbl):
    if selected_lbl is None or selected_lbl == '':
        return [None, None, None, True]
    else:
        conn = sysmod.psqldb_connect()
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            sql = "SELECT * FROM {schema}.labels WHERE id=%s".format(schema=sysmod.schemafin())   
            stmt = cur.mogrify(sql, (selected_lbl, ))
            cur.execute(stmt)
            row = cur.fetchone()
            cur.close()
        return [row['id'], row['name'], row['keywords'], row['status']]

@anvil.server.callable
# Generate labels dropdown items
def generate_labels_mapping_action_dropdown():
    conn = sysmod.psqldb_connect()
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        sql = "SELECT * FROM {schema}.label_mapping_action ORDER BY seq ASC".format(schema=sysmod.schemarefd())
        cur.execute(sql)
        rows = cur.fetchall()
        cur.close()
    content = list((row['action'], {"id": row['id'], "text": row['action']}) for row in rows)
    return content

@anvil.server.callable
# Create label
def create_label(labels):
    try:
        conn = sysmod.psqldb_connect()
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            if len(labels) > 0:
                mogstr = ', '.join(cur.mogrify("(%s, %s, %s)", (label['name'], label['keywords'], label['status'])).decode('utf-8') for label in labels)
                stmt = "INSERT INTO {schema}.labels (name, keywords, status) VALUES %s RETURNING id".format(schema=sysmod.schemafin())
                cur.execute(stmt % mogstr)
                conn.commit()
                return [r['id'] for r in cur.fetchall()]
            else:
                return []
    except (Exception, psycopg2.OperationalError) as err:
        sysmod.print_data_debug("OperationalError in " + create_label.__name__, err)
        conn.rollback()
    finally:
        if cur is not None: cur.close()
        if conn is not None: conn.close()
    return None

@anvil.server.callable
# Update label
def update_label(id, name, keywords, status):
    try:
        conn = sysmod.psqldb_connect()
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            sql = "UPDATE {schema}.labels SET name=%s, keywords=%s, status=%s WHERE id=%s".format(schema=sysmod.schemafin())
            stmt = cur.mogrify(sql, (name, keywords, status, id))
            cur.execute(stmt)
            conn.commit()
            count = cur.rowcount
            if count <= 0:
                    raise psycopg2.OperationalError("Label ({0}) update fail.".format(name))
            cur.close()
        return count
    except (Exception, psycopg2.OperationalError) as err:
        sysmod.print_data_debug("OperationalError in " + update_label.__name__, err)
        conn.rollback()
    finally:
        if conn is not None: conn.close()
    return None

@anvil.server.callable
# Delete label
def delete_label(id):
    try:
        conn = sysmod.psqldb_connect()
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            sql = "DELETE FROM {schema}.labels WHERE id=%s".format(schema=sysmod.schemafin())
            stmt = cur.mogrify(sql, (id, ))
            cur.execute(stmt)
            conn.commit()
            count = cur.rowcount
            if count <= 0:
                    raise psycopg2.OperationalError("Label ({0}) deletion fail.".format(name))
            cur.close()
        return count
    except (Exception, psycopg2.OperationalError) as err:
        sysmod.print_data_debug("OperationalError in " + delete_label.__name__, err)
        conn.rollback()
    finally:
        if conn is not None: conn.close()
    return None

@anvil.server.callable
def predict_relevant_labels(srclbl, curlbl):
    score = []
    for s in srclbl:
        highscore = [0, None]
        for lbl in curlbl:
            similarity = fuzz.ratio(s, curlbl[lbl])
            if similarity > highscore[0]:
                highscore = [similarity, lbl]
        # score.append({
        #     'src': s,
        #     'proximity': highscore[1] if highscore[0] > 50 else None,
        #     'score': highscore[0] if highscore[0] > 50 else None
        # })
        score.append(highscore[1])
    return score