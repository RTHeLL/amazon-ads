from typing import Tuple

import gspread
import pygsheets

from services.google import BaseService
from settings import GOOGLE_ADMIN_EMAIL


class GSpreadSpreadsheetService(BaseService):
    def get_or_create(self, name: str) -> Tuple[gspread.Spreadsheet, bool]:
        spreadsheet_list = self.gspread_gc.openall(name)

        if not spreadsheet_list:
            _result = self.gspread_gc.create(name), True
        else:
            _result = spreadsheet_list[0], False

        _result[0].share(GOOGLE_ADMIN_EMAIL, perm_type='user', role='writer', notify=False)

        return _result


class PyGSheetsSpreadsheetService(BaseService):
    def get_or_create(self, name: str) -> Tuple[pygsheets.Spreadsheet, bool]:
        try:
            _result = self.pygsheets_gc.open(name), False
        except pygsheets.SpreadsheetNotFound:
            _result = self.pygsheets_gc.create(name), True

        _result[0].share(GOOGLE_ADMIN_EMAIL, type='user', role='writer', sendNotificationEmail=False)

        return _result
