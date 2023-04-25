import gspread
import pygsheets
from oauth2client.service_account import ServiceAccountCredentials

from settings import GOOGLE_CREDENTIALS_FILE_NAME


class BaseService:
    SCOPE = [
        'https://spreadsheets.google.com/feeds',
        'https://www.googleapis.com/auth/drive'
    ]

    def __init__(self) -> None:
        self.credentials = ServiceAccountCredentials.from_json_keyfile_name(
            GOOGLE_CREDENTIALS_FILE_NAME,
            self.SCOPE
        )
        self.gspread_gc = gspread.authorize(self.credentials)
        self.pygsheets_gc = pygsheets.authorize(service_file=GOOGLE_CREDENTIALS_FILE_NAME)
