from typing import Tuple

import pygsheets

from services.google import BaseService


class PyGSheetsWorksheetService(BaseService):
    def __init__(self, spreadsheet: pygsheets.Spreadsheet) -> None:
        super().__init__()

        self.spreadsheet = spreadsheet

    def get(self, name: str) -> pygsheets.Worksheet:
        return self.spreadsheet.worksheet_by_title(name)

    def create(self, name: str) -> pygsheets.Worksheet:
        return self.spreadsheet.add_worksheet(name)

    def get_or_create(self, name: str) -> Tuple[pygsheets.Worksheet, bool]:
        try:
            return self.get(name=name), False
        except pygsheets.WorksheetNotFound:
            return self.create(name=name), True
