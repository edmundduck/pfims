import anvil.files
from anvil.files import data_files
import anvil.secrets
import anvil.users
import anvil.server
# import camelot
from io import BytesIO
import datetime
from ..SysProcess import SystemModule as sysmod
from ..SysProcess import LoggingModule

# This is a server module. It runs on the Anvil server,
# rather than in the user's browser.
logger = LoggingModule.ServerLogger()

@anvil.server.callable
def zz_test_session():
    logger.debug(anvil.server.session)
    if anvil.server.session is None:
        logger.debug("It's none")
    else:
        logger.debug("It's not none")
    if not anvil.server.session:
        logger.debug("It's empty")
    else:
        logger.debug("It's not empty")

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
    logger.debug("userid=", userid)
    if file.content_type != "application/pdf":
        raise Exception(f"File type not allowed, file upload aborted.")
    
    all_rows = app_tables.upload_files.search(tables.order_by('last_upload', ascending=False), userid=userid)
    if len(all_rows) > MAX_IMAGES_STORED:
        rows_to_delete = all_rows[MAX_IMAGES_STORED:]
        logger.debug("rows_to_delete=", rows_to_delete)
        for row_del in rows_to_delete:
            row_del.delete()
            
    row = app_tables.upload_files.add_row(userid=userid, fileobj=file, last_upload=datetime.datetime.now())
    fileurl = row[2][1].url[:-3]
    logger.debug("fileurl=", fileurl)
    logger.debug("tempurl=", url)
    for r in row:
        logger.debug(r)

    # test pdf
    fileurl = 'https://www.expat.hsbc.com/content/dam/hsbc/mbos/docs/important-documents/expat-gbp-rate-change-sheet.pdf'
    # try:
    t = camelot.read_pdf(fileurl)
    logger.debug("Total tables extracted:", t.n)
    # print the first table as Pandas DataFrame
    logger.debug(t[0].df)
    # except (Exception) as err:
    # logger.debug(f"Error: {err}")

@anvil.server.callable
def test_tabula(file, url):
    import tabula

    pdf_url = 'https://www.mscbs.gob.es/profesionales/saludPublica/ccayes/alertasActual/nCov-China/documentos/Actualizacion_61_COVID-19.pdf'
    test_df = tabula.read_pdf(pdf_url)[0]
    logger.debug(test_df)

@anvil.server.callable
def test_pdfplumber(file, url):
    import pdfplumber
    
    with pdfplumber.open(BytesIO(file.get_bytes())) as pdf:
        # table = pdf.pages[1].extract_table()
        page = pdf.pages[0]
        logger.debug(page.width, ",", page.height)
        # pd.DataFrame(table[1::],columns=table[0]))