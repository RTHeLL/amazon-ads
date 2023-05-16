import datetime
import re

from exceptions import NoCSRFToken
from models.adverting import CampaignsData
from services import BaseService
from utils.headers import ADVERTING_API_HEADERS, ADVERTING_HEADERS
from utils.urls import CAMPAIGNS_PAGE_URL, CAMPAIGNS_API_URL


class AdvertingService(BaseService):
    def get_campaigns_data(
            self,
            campaigns_name: str,
            start_date: datetime.datetime,
            end_date: datetime.datetime
    ) -> CampaignsData:
        headers = ADVERTING_API_HEADERS.copy()
        headers['x-csrf-token'] = self.__get_csrf_token()

        data = {
            'startDateUTC': self.__convert_datetime_to_timestamp(start_date),
            'endDateUTC': self.__convert_datetime_to_timestamp(end_date),
            'period': 'CUSTOM',
            'fields': [
                'CAMPAIGN_NAME',
                'CAMPAIGN_ELIGIBILITY_STATUS',
                'CAMPAIGN_SMART_BIDDING_STRATEGY',
                'BID_ADJUSTMENT_PERCENTAGE',
                'CAMPAIGN_STATE',
                'CAMPAIGN_START_DATE',
                'CAMPAIGN_END_DATE',
                'CAMPAIGN_BUDGET',
                'CAMPAIGN_BUDGET_CURRENCY',
                'CAMPAIGN_BUDGET_TYPE',
                'CAMPAIGN_TYPE',
                'IMPRESSIONS',
                'CLICKS',
                'SPEND',
                'ORDERS',
                'SALES'
            ],
            'filters': [
                {
                    'field': 'CAMPAIGN_NAME',
                    'not': False,
                    'operator': 'BROAD_MATCH',
                    'values': [
                        campaigns_name,
                    ],
                    'programType': None,
                }
            ],
            'programType': 'SP',
            'pageOffset': 0,
            'pageSize': 300,
            'sort': {
                'order': 'DESC',
                'field': 'SPEND',
            },
            'queries': [],
            'timeSeriesInterval': 'DAY',
            'version': 'V2',
        }

        response = self.requester.make_post_request(
            CAMPAIGNS_API_URL,
            cookies=self.account.get_adverting_cookies(),
            headers=headers,
            json=data
        )

        return CampaignsData(**response)

    def __get_csrf_token(self) -> str:
        response = self.requester.make_get_request(
            CAMPAIGNS_PAGE_URL,
            cookies=self.account.get_adverting_cookies(),
            headers=ADVERTING_HEADERS,
            json_response=False
        )
        csrf_token_re = re.findall(r'csrfToken: .*', response.text)

        if not csrf_token_re:
            raise NoCSRFToken('no csrf token in response')

        return csrf_token_re[0].replace('"', '').replace(',', '').split(' ')[1]

    @staticmethod
    def __convert_datetime_to_timestamp(date: datetime.datetime) -> int:
        return int(date.timestamp() * 1000)
