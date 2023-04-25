from typing import List

from pydantic import BaseModel, Field


class GetReportData(BaseModel):
    rows: List[List[str]]


class Data(BaseModel):
    get_report_data: GetReportData = Field(..., alias='getReportData')


class BusinessReports(BaseModel):
    data: Data
