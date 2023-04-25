import pysondb
import logging

logging.basicConfig(
    level=logging.INFO,
    filename="logs.log",
    filemode="a",
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger('WBStat')
logger.addHandler(logging.StreamHandler())

YES_CHOICES = ['yes', 'y']
NO_CHOICES = ['no', 'n']

DATABASE = pysondb.getDb('db.json', id_fieldname='id_', log=True)

API_CALL_TRIES = 3
TIMEOUT = 30
TIME_TO_SLEEP = 5

GOOGLE_CREDENTIALS_FILE_NAME = 'amazon-ads-384815-6de7d1580482.json'
GOOGLE_ADMIN_EMAIL = 'mr.trex2014@gmail.com'
GOOGLE_FILE_NAME = 'MOONRIN, C&B, DACOTTON, EPSY'
