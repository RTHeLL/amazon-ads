from typing import List, Optional

from pydantic import BaseModel, Field


class Period(BaseModel):
    task_ids: Optional[List[str]] = None
    status: Optional[str] = None
    sales: Optional[float] = None
    units: Optional[int] = None
    units_ppc: Optional[int] = Field(None, alias='unitsPpc')
    advertising: Optional[float] = None
    net_profit: Optional[float] = Field(None, alias='netProfit')


class Entry(BaseModel):
    id: str
    type: str
    asin: str
    price: float
    cost: float


class EntriesData(BaseModel):
    entries: Optional[List[Entry]] = None
    state: Optional[str] = None
    status: Optional[str] = None
    error: Optional[str] = None


"""
units -> Total Units
sales -> Total Sales $
netProfit -> Total Profit $
unitsPpc -> PPC Units
advertising -> Spend+Tax $
"""
