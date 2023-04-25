import datetime
from typing import Tuple, Optional

from datetime_periods import period

from models.sellerboard import Period, EntriesData
from services import BaseService
from utils.headers import SELLER_BOARD_ENTRIES_HEADERS
from utils.urls import SELLER_BOARD_ENTRIES_URL, SELLER_BOARD_PERIODS_URL


def get_last_week_date_range() -> Tuple[int, int]:
    now = datetime.datetime.utcnow()
    last_week_period = period(now - datetime.timedelta(days=7), 'week')

    start_last_week_timestamp = int(
        datetime.datetime.timestamp(last_week_period[0].replace(tzinfo=datetime.timezone.utc))
    )
    end_last_week_timestamp = int(
        datetime.datetime.timestamp(last_week_period[1].replace(tzinfo=datetime.timezone.utc))
    )

    return start_last_week_timestamp, end_last_week_timestamp


def get_last_moth_date_range() -> Tuple[int, int]:
    now = datetime.datetime.utcnow()
    first_day = now.replace(day=1)

    last_month = first_day - datetime.timedelta(days=1)
    last_month_period = period(last_month, 'month')

    datetime.datetime.timestamp(last_month_period[0].replace(tzinfo=datetime.timezone.utc))

    start_last_month_timestamp = int(
        datetime.datetime.timestamp(last_month_period[0].replace(tzinfo=datetime.timezone.utc))
    )
    end_last_month_timestamp = int(
        datetime.datetime.timestamp(last_month_period[1].replace(tzinfo=datetime.timezone.utc))
    )

    return start_last_month_timestamp, end_last_month_timestamp


PERIODS = {
    'last_week': ('Прошлая неделя', get_last_week_date_range),
    'last_month': ('Прошлый месяц', get_last_moth_date_range)
}


class SellerBoardService(BaseService):
    def get_periods(self, asin: str, period_: str):
        period_start, period_end = PERIODS[period_][1]()
        return self.__get_periods(asin=asin, period_start=period_start, period_end=period_end)

    def get_cost(self, asin: str, period_: str) -> Optional[float]:
        period_start, period_end = PERIODS[period_][1]()

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
