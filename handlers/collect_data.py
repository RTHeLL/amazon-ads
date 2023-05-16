import datetime
from typing import Any, Dict, Optional

from exceptions import InvalidSellerCentralAuth, NoCSRFToken
from handlers import BaseHandler
from services.amazon.adverting import AdvertingService
from services.amazon.sellerboard import SellerBoardService
from services.amazon.sellercentral import SellerCentralService


class CollectDataHandler(BaseHandler):
    @property
    def actions(self):
        return {
            'all': ('Собрать все данные', self.collect_all_data),
            'adverting': ('Собрать данные из рекламного кабинета', self.collect_adverting_data),
            'sellerboard': ('Собрать данные из SellerBoard', self.collect_seller_board_data),
            'sellercentral': ('Собрать данные из SellerCentral', self.collect_seller_central_data),
            'back': ('Назад', self.app.show_main_menu)
        }

    def handle(self, action: str):
        if not self.app.selected_account:
            print('У вас не выбран аккаунт')
            return

        self.__set_parameters()

        return self.actions[action][1]()

    def collect_all_data(self) -> Optional[Dict[str, Any]]:
        while True:
            try:
                adverting = self._collect_adverting_data()
                break
            except NoCSRFToken:
                print('У вас устарели данные от Adverting')
                self.app.selected_account.at_main = input('Введите at_main для Adverting аккаунта: ')
                self.app.selected_account.sst_main = input('Введите sst_main для Adverting аккаунта: ')
                self.app.selected_account.session_id = input('Введите session_id для Adverting аккаунта: ')
                self.app.selected_account.ubid_main = input('Введите ubid_main для Adverting аккаунта: ')
                self.app.selected_account.save()

        periods, cost = self._collect_seller_board_data()

        while True:
            try:
                sessions = self._collect_seller_central_data()
                break
            except InvalidSellerCentralAuth:
                print('У вас устарели данные от SellerCentral')
                self.app.selected_account.at_main = input('Введите at_main для SellerCentral аккаунта: ')
                self.app.selected_account.host_mselc = input('Введите host_mselc для SellerCentral аккаунта: ')
                self.app.selected_account.save()

        return {
            'ASIN': self.asin,
            'Cost': cost,
            'Total Units': periods[0].units,
            'Sessions': sessions,
            'Total Sales $': periods[0].sales,
            'Profit Total': periods[0].net_profit,
            'PPC Units': periods[0].units_ppc,
            'Impressions': adverting.summary.impressions,
            'Clicks': adverting.summary.clicks,
            'Orders': adverting.summary.orders,
            'Sales $': adverting.summary.sales.dollars,
            'Spend $': adverting.summary.spend.dollars,
            'Spend+Tax $': periods[0].advertising,
        }

    def collect_adverting_data(self):
        adverting = self._collect_adverting_data()

        return {
            'ASIN': self.asin,
            'Cost': '-',
            'Total Units': '-',
            'Sessions': '-',
            'Total Sales $': '-',
            'Profit Total': '-',
            'PPC Units': '-',
            'Impressions': adverting.summary.impressions,
            'Clicks': adverting.summary.clicks,
            'Orders': adverting.summary.orders,
            'Sales $': adverting.summary.sales.dollars,
            'Spend $': adverting.summary.spend.dollars,
            'Spend+Tax $': '-',
        }

    def _collect_adverting_data(self):
        adverting_service = AdvertingService(account=self.app.selected_account)

        return adverting_service.get_campaigns_data(
            campaigns_name=self.campaigns_name,
            start_date=self.start_date,
            end_date=self.end_date
        )

    def collect_seller_board_data(self):
        periods, cost = self._collect_seller_board_data()

        return {
            'ASIN': self.asin,
            'Cost': cost,
            'Total Units': periods[0].units,
            'Sessions': '-',
            'Total Sales $': periods[0].sales,
            'Profit Total': periods[0].net_profit,
            'PPC Units': periods[0].units_ppc,
            'Impressions': '-',
            'Clicks': '-',
            'Orders': '-',
            'Sales $': '-',
            'Spend $': '-',
            'Spend+Tax $': periods[0].advertising,
        }

    def _collect_seller_board_data(self):
        self.app.selected_account.auth()
        self.app.selected_account.save()

        seller_board_service = SellerBoardService(account=self.app.selected_account)

        end_date = self.end_date.replace(hour=23, minute=59, second=59)

        periods = seller_board_service.get_periods(
            asin=self.asin,
            period_start=self.__convert_datetime_to_timestamp(self.start_date),
            period_end=self.__convert_datetime_to_timestamp(end_date)
        )
        cost = seller_board_service.get_cost(
            asin=self.asin,
            period_start=self.__convert_datetime_to_timestamp(self.start_date),
            period_end=self.__convert_datetime_to_timestamp(end_date)
        )

        return periods, cost

    def collect_seller_central_data(self):
        try:
            sessions = self._collect_seller_central_data()
        except InvalidSellerCentralAuth:
            print('У вас устарели данные от SellerCentral')
            self.app.selected_account.at_main = input('Введите at_main для SellerCentral аккаунта: ')
            self.app.selected_account.host_mselc = input('Введите host_mselc для SellerCentral аккаунта: ')
            self.app.selected_account.save()
            print('Данные успешно обновлены, запустите сбор данных еще раз!')
            return

        return {
            'ASIN': self.asin,
            'Cost': '-',
            'Total Units': '-',
            'Sessions': sessions,
            'Total Sales $': '-',
            'Profit Total': '-',
            'PPC Units': '-',
            'Impressions': '-',
            'Clicks': '-',
            'Orders': '-',
            'Sales $': '-',
            'Spend $': '-',
            'Spend+Tax $': '-',
        }

    def _collect_seller_central_data(self):
        seller_central_service = SellerCentralService(account=self.app.selected_account)

        return seller_central_service.get_sessions(
            asin=self.asin,
            start_date=self.start_date,
            end_date=self.end_date
        )

    @staticmethod
    def __convert_datetime_to_timestamp(date: datetime.datetime) -> int:
        return int(date.timestamp())

    def __set_parameters(self):
        while True:
            try:
                self.start_date, self.end_date = (
                    datetime.datetime.strptime(
                        input('Введите дату в формате YYYY-MM-DD: '),
                        '%Y-%m-%d'
                    ).replace(tzinfo=datetime.timezone.utc) for _ in range(2)
                )
                break
            except ValueError:
                print('Ошибка ввода даты! \n. Убедитесь, что дата имеет формат YYYY-MM-DD')

        self.campaigns_name = input('Введите название рекламных кампаний: ')
        self.asin = input('Введите ASIN: ')
