from typing import List, Optional

from pydantic import BaseModel, Field


class GetReportData(BaseModel):
    rows: List[List[Optional[str]]]


class Data(BaseModel):
    get_report_data: GetReportData = Field(..., alias='getReportData')


class BusinessReports(BaseModel):
    data: Data
