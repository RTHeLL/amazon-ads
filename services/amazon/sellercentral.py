import datetime

from requests import JSONDecodeError

from exceptions import NoASINInSellerCentral, InvalidSellerCentralAuth
from models.sellercentral import BusinessReports
from services import BaseService
from utils.headers import SELLER_CENTRAL_HEADERS
from utils.urls import SELLER_CENTRAL_BUSINESS_REPORTS_URL


class SellerCentralService(BaseService):
    def get_sessions(self, asin: str, start_date: datetime.datetime, end_date: datetime.datetime):
        data = {
            'operationName': 'reportDataQuery',
            'variables': {
                'input': {
                    'legacyReportId': '102:DetailSalesTrafficBySKU',
                    'startDate': start_date.strftime("%Y-%m-%d"),
                    'endDate': end_date.strftime("%Y-%m-%d"),
                },
            },
            'query': 'query reportDataQuery($input: GetReportDataInput) {\n  '
                     'getReportData(input: $input) {\n    '
                     'granularity\n    '
                     'hadPrevious\n    '
                     'hasNext\n    '
                     'size\n    '
                     'startDate\n    '
                     'endDate\n    '
                     'page\n    '
                     'columns {\n      '
                     'label\n      '
                     'valueFormat\n      '
                     'isGraphable\n      '
                     'translationKey\n      '
                     'isDefaultSortAscending\n      '
                     'isDefaultGraphed\n      '
                     'isDefaultSelected\n      '
                     'isDefaultSortColumn\n      '
                     '__typename\n    }\n    '
                     'rows\n    __typename\n  '
                     '}\n}\n',
        }

        try:
            response = self.requester.make_post_request(
                SELLER_CENTRAL_BUSINESS_REPORTS_URL,
                cookies=self.account.get_seller_central_cookies(),
                headers=SELLER_CENTRAL_HEADERS,
                json=data
            )
        except JSONDecodeError:
            raise InvalidSellerCentralAuth

        business_reports = BusinessReports(**response)

        for i in business_reports.data.get_report_data.rows:
            if i[1] == asin:
                return i[8]
            else:
                continue

        raise NoASINInSellerCentral
