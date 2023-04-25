from _decimal import Decimal
from pydantic import BaseModel


class Converter:
    @staticmethod
    def millicents_to_dollars(millicents):
        return Decimal(millicents / 100000).quantize(Decimal('0.00'))


class Spend(BaseModel):
    millicents: int

    @property
    def dollars(self):
        return Converter.millicents_to_dollars(self.millicents)


class Sales(BaseModel):
    millicents: int

    @property
    def dollars(self):
        return Converter.millicents_to_dollars(self.millicents)


class Summary(BaseModel):
    impressions: int
    clicks: int
    orders: int
    sales: Sales
    spend: Spend


class CampaignsData(BaseModel):
    summary: Summary
