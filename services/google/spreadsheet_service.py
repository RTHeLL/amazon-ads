from typing import Tuple

import pygsheets

from services.google import BaseService
from settings import GOOGLE_ADMIN_EMAIL


class PyGSheetsSpreadsheetService(BaseService):
    def get_or_create(self, name: str) -> Tuple[pygsheets.Spreadsheet, bool]:
        try:
            _result = self.pygsheets_gc.open(name), False
        except pygsheets.SpreadsheetNotFound:
            _result = self.pygsheets_gc.create(name), True

        _result[0].share(GOOGLE_ADMIN_EMAIL, type='user', role='writer', sendNotificationEmail=False)

        return _result
