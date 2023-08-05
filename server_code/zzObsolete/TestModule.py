import anvil.secrets
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
import camelot
from io import BytesIO
import datetime
from ..SysProcess import SystemModule as sysmod

# This is a server module. It runs on the Anvil server,
# rather than in the user's browser.
#
# To allow anvil.server.call() to call functions here, we mark
# them with @anvil.server.callable.
# Here is an example - you can replace it with your own:
#
# @anvil.server.callable
# def say_hello(name):
#   print("Hello, " + name + "!")
#   return 42
#

@anvil.server.callable
def zz_test_session():
    print(anvil.server.session)
    if anvil.server.session is None:
        print("It's none")
    else:
        print("It's not none")
    if not anvil.server.session:
        print("It's empty")
    else:
        print("It's not empty")

class NewLog:
    def __init__(self):
        print("NewLog=", anvil.server.session)

@anvil.server.callable
def test_camelot(file, url):
    MAX_IMAGES_STORED = 1
    userid = int(sysmod.get_current_userid())
    print("userid=", userid)
    if file.content_type != "application/pdf":
        raise Exception(f"File type not allowed, file upload aborted.")
    
    all_rows = app_tables.upload_files.search(tables.order_by('last_upload', ascending=False), userid=userid)
    if len(all_rows) > MAX_IMAGES_STORED:
        rows_to_delete = all_rows[MAX_IMAGES_STORED:]
        print("rows_to_delete=", rows_to_delete)
        for row_del in rows_to_delete:
            row_del.delete()
            
    row = app_tables.upload_files.add_row(userid=userid, fileobj=file, last_upload=datetime.datetime.now())
    fileurl = row[2][1].url[:-3]
    print("fileurl=", fileurl)
    print("tempurl=", url)
    for r in row:
        print(r)

    # try:
    df = camelot.read_pdf(fileurl)
    print(df)
    # except (Exception) as err:
        # print(f"Error: {err}")