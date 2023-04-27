import anvil.secrets
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server

# This is a server module. It runs on the Anvil server,
# rather than in the user's browser.

@anvil.server.callable
# Save the filter and rules
# Filter and rules ID are not generated in application side, it's handled by DB function instead, hence running SQL scripts in DB is required beforehand
def save_filter_rules(uid, fid, filter_obj):
    conn = None
    count = None
    try:
        conn = sysmod.psqldb_connect()
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            if len(filter_obj) > 0:
                # First insert/update filter group
                if fid is None: fid = "DEFAULT".strip('''''')
                name = filter_obj.get('name', None)
                type = filter_obj.get('type', None)
                rules = filter_obj.get('rules', [])
                currenttime = datetime.now()
                sql = "INSERT INTO {schema}.filtergrp (userid, fid, fname, flastsave) \
                VALUES (%s,%s,%s,%s) RETURNING fid".format(schema=sysmod.schemafin())
                stmt = cur.mogrify(sql, (uid, fid, name, currenttime))
                cur.execute(stmt)
                conn.commit()
                fid = cur.fetchone()
                if fid['fid'] < 0:
                    raise psycopg2.OperationalError("Fail to save the filter ({0}).".format(name))
            
                mogstr = []
                for rule in rules:
                    tj = fobj.CashTransaction()
                    tj.assignFromDict({'tab_id': tid}).assignFromDict(row)
                    if tj.isValidRecord(): mogstr.append(tj.getDatabaseRecord())
                if len(mogstr) > 0:
                    cur.executemany("INSERT INTO {schema}.exp_transactions (iid, tab_id, trandate, account_id, amount, labels, \
                    remarks, stmt_dtl) VALUES (%s, %s, %s, %s, %s, %s, %s, %s) ON CONFLICT (iid, tab_id) DO UPDATE SET \
                    trandate=EXCLUDED.trandate, \
                    account_id=EXCLUDED.account_id, \
                    amount=EXCLUDED.amount, \
                    labels=EXCLUDED.labels, \
                    remarks=EXCLUDED.remarks, \
                    stmt_dtl=EXCLUDED.stmt_dtl \
                    WHERE exp_transactions.iid=EXCLUDED.iid AND exp_transactions.tab_id=EXCLUDED.tab_id".format(schema=sysmod.schemafin()), mogstr)
                    conn.commit()
                    count = cur.rowcount
                    if count <= 0: raise psycopg2.OperationalError("Transactions (tab id:{0}) creation or update fail.".format(tid))
                    cur.close()
                else:
                    count = 0
            else:
                count = 0
    except (Exception, psycopg2.OperationalError) as err:
        sysmod.print_data_debug("OperationalError in " + upsert_transactions.__name__, err)
        conn.rollback()
    finally:
        if conn is not None: conn.close()        
    return count
    
