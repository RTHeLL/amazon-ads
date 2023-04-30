from typing import Optional

from models.sellerboard import Period, EntriesData
from services import BaseService
from utils.headers import SELLER_BOARD_ENTRIES_HEADERS
from utils.urls import SELLER_BOARD_ENTRIES_URL, SELLER_BOARD_PERIODS_URL


class SellerBoardService(BaseService):
    def get_periods(self, asin: str, period_start: int, period_end: int):
        return self.__get_periods(asin=asin, period_start=period_start, period_end=period_end)

    def get_cost(self, asin: str, period_start: int, period_end: int) -> Optional[float]:
        entries_response = self.__get_entries_with_retry(asin=asin, period_start=period_start, period_end=period_end)

        if not entries_response or not entries_response.entries:
            return None

        return entries_response.entries[0].cost

    def __get_entries_with_retry(self, asin: str, period_start: int, period_end: int) -> EntriesData:
        entries_response = self.__get_entries(asin=asin, period_start=period_start, period_end=period_end)

        if not entries_response or entries_response.state in ('preparing', 'cache_empty'):
            self.__get_periods(asin=asin, period_start=period_start, period_end=period_end)
            entries_response = self.__get_entries(asin=asin, period_start=period_start, period_end=period_end)

        return entries_response

    def __get_entries(self, asin: str, period_start: int, period_end: int) -> EntriesData:
        data = {
            'viewType': 'panels',
            'entryType': 'product',
            'periodStart': period_start,
            'periodEnd': period_end,
            'periodicity': 'period',
            'sortField': 'sales',
            'sortDirection': 'desc',
            'page': '1',
            'groupByAsin': '',
            'groupBy': '',
            'trendsParameter': 'sales',
            'productsSelectAll': 'true',
            'productsSearchQuery': asin,
        }

        response = self.requester.make_post_request(
            SELLER_BOARD_ENTRIES_URL,
            cookies=self.account.get_seller_board_cookies(),
            headers=SELLER_BOARD_ENTRIES_HEADERS,
            data=data
        )

        return EntriesData(**response)

    def __get_periods(self, asin: str, period_start: int, period_end: int, task_id: Optional[str] = None):
        data = {
            'viewType': 'panels',
            'compare': '',
            'groupByAsin': '',
            'groupBy': '',
            'loadBy': 'periods',
            'periods[0][start]': period_start,
            'periods[0][end]': period_end,
            'periods[0][forecast]': '0',
            'periods[0][standard]': '0',
            'periods[0][key]': 'last_week',
            'productsSelectAll': 'true',
            'productsSearchQuery': asin,
        }

        if task_id:
            data['preparingPeriodsTasksIds[]'] = task_id

        response = self.requester.make_post_request(
            SELLER_BOARD_PERIODS_URL,
            cookies=self.account.get_seller_board_cookies(),
            headers=SELLER_BOARD_ENTRIES_HEADERS,
            data=data
        )

        if isinstance(response, bool):
            return self.__get_periods(
                asin=asin,
                period_start=period_start,
                period_end=period_end
            )

        periods = [Period(**i) for i in response]

        if periods[0].task_ids:
            return self.__get_periods(
                asin=asin,
                period_start=period_start,
                period_end=period_end,
                task_id=periods[0].task_ids[0]
            )

        return periods
