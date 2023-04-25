from typing import Tuple, Union

from df2gspread import gspread2df
from df2gspread import df2gspread
import gspread

from pandas import DataFrame
import pygsheets

from exceptions import NoWorksheet
from services.google import BaseService


class GSpreadWorksheetService(BaseService):
    def __init__(self, spreadsheet: gspread.Spreadsheet) -> None:
        super().__init__()

        self.spreadsheet = spreadsheet

    def get(self, name: str) -> DataFrame:
        try:
            _df: DataFrame = gspread2df.download(self.spreadsheet.id, name, credentials=self.credentials, row_names=True)
            _df.columns = _df.iloc[0]
            _df = _df[1:]
            return _df
        except RuntimeError as exc:
            if 'Trying to open non-existent or inaccessible worksheet' in exc.args:
                raise NoWorksheet

    def upload(self, name: str, df: DataFrame) -> gspread.Worksheet:
        return df2gspread.upload(df, self.spreadsheet.id, name, credentials=self.credentials, row_names=True, col_names=True)

    def get_or_create(self, name: str, df: DataFrame) -> Tuple[Union[DataFrame, gspread.Worksheet], bool]:
        try:
            return self.get(name=name), False
        except NoWorksheet:
            return self.upload(name=name, df=df), True


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
