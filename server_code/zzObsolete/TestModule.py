import anvil.files
from anvil.files import data_files
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

@anvil.server.callable
def test_camelot(file, url):
    # Ref: https://github.com/camelot-dev/camelot/issues/286
    # Ref: https://docs.streamlit.io/knowledge-base/dependencies/libgl
    # Ref: https://github.com/camelot-dev/camelot/blob/master/camelot/handlers.py
    # Camelot so far requires the following packages to work partially...
    # camelot-py 0.11.0
    # opencv-contrib-python-headless latest
    # ghostscript latest (installed but still not working)
    # tk latest (not confirmed)
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

    # test pdf
    fileurl = 'https://www.expat.hsbc.com/content/dam/hsbc/mbos/docs/important-documents/expat-gbp-rate-change-sheet.pdf'
    # try:
    t = camelot.read_pdf(fileurl)
    print("Total tables extracted:", t.n)
    # print the first table as Pandas DataFrame
    print(t[0].df)
    # except (Exception) as err:
    # print(f"Error: {err}")