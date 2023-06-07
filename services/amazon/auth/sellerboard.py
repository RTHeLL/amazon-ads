import requests
from bs4 import BeautifulSoup

from exceptions import UnauthorizedException, NoAccountInSellerBoard
from models import Account
from utils.headers import SELLER_BOARD_LOGIN_PAGE_HEADERS, SELLER_BOARD_LOGIN_AUTH_HEADERS, \
    SELLER_BOARD_SWITCH_ACCOUNT_HEADERS, SELLER_BOARD_DASHBOARD_HEADERS
from utils.urls import SELLER_BOARD_LOGIN_URL, SELLER_BOARD_SWITCH_ACCOUNT_URL


class SellerBoardAuthService:
    def __init__(self, account: Account) -> None:
        self.account = account
        self.session = requests.Session()

    def auth(self) -> tuple:
        hidden_fields = self._get_hidden_fields_on_login_page()

        data = {
            'login': self.account.seller_board_username,
            'password': self.account.seller_board_password,
            'keeploggedin': '1'
        }
        data.update(hidden_fields)

        response = self.session.post(
            SELLER_BOARD_LOGIN_URL,
            headers=SELLER_BOARD_LOGIN_AUTH_HEADERS,
            data=data
        )

        if response.status_code != 200:
            raise ValueError(
                f'Response: {response.text}\n'
                f'Ошибка авторизации в SellerBoard. Проверьте правильность введенных данных.'
            )

        self._switch_account()

        cookies = self.session.cookies.get_dict()
        phpsesid = cookies.get('PHPSESSID')
        rmbrm = cookies.get('RMBRM')
        sid = cookies.get('sid')

        if all([phpsesid, rmbrm, sid]):
            raise ValueError(f'Bad auth in SellerBoard. No PHPSESID, RMBRM or sid in cookeis {cookies}')

        return phpsesid, rmbrm, sid

    def _get_hidden_fields_on_login_page(self):
        response = self.session.get(SELLER_BOARD_LOGIN_URL, headers=SELLER_BOARD_LOGIN_PAGE_HEADERS)

        soup = BeautifulSoup(response.text)
        hidden_tags = soup.find_all("input", type="hidden")
        soup_dict = dict()

        for tag in hidden_tags:
            attrs = tag.attrs
            name = attrs.get('name')
            value = attrs.get('value')
            if name is not None and value is not None:
                soup_dict[name] = value

        return soup_dict

    def _switch_account(self):
        dashboard_page = self._get_dashboard_page()

        csrf_key, csrf_value = self._get_csrf_from_dashboard_page(dashboard_page)
        account_id = self._get_account_id(dashboard_page)

        data = {
            'account': account_id,
            csrf_key: csrf_value,
        }

        self.session.post(
            SELLER_BOARD_SWITCH_ACCOUNT_URL,
            headers=SELLER_BOARD_SWITCH_ACCOUNT_HEADERS,
            data=data
        )

    @staticmethod
    def _get_csrf_from_dashboard_page(source):
        soup = BeautifulSoup(source)
        tag = soup.select_one("input[data-csrfkey]", type="hidden")

        try:
            csrf_key = tag.attrs.get('data-csrfkey')
            csrf_value = tag.attrs.get('data-csrfvalue')
        except AttributeError:
            raise UnauthorizedException

        return csrf_key, csrf_value

    def _get_account_id(self, source):
        soup = BeautifulSoup(source)

        try:
            account_element = soup.find('span', title=self.account.seller_board_name).parent
        except AttributeError:
            raise NoAccountInSellerBoard()

        data_account_value = account_element.get('data-account')

        return data_account_value

    def _get_dashboard_page(self):
        response = self.session.get(
            'https://app.sellerboard.com/ru/dashboard/',
            headers=SELLER_BOARD_DASHBOARD_HEADERS
        )

        return response.text
