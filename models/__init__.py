from typing import Dict, Any, Optional

from exceptions import UnauthorizedException, NoAccountInSellerBoard
from settings import DATABASE


class Account:
    def __init__(
            self,
            name: str,
            session_id: str,
            ubid_main: str,
            at_main: str,
            sst_main: str,
            host_mselc: str,
            seller_board_name: str,
            seller_board_username: str,
            seller_board_password: str,
            phpsesid: Optional[str] = None,
            rmbrm: Optional[str] = None,
            sid: Optional[str] = None,
            id_: Optional[int] = None,
    ) -> None:
        self.id = id_

        self.name = name
        self.session_id = session_id
        self.ubid_main = ubid_main
        self.at_main = at_main
        self.sst_main = sst_main
        self.host_mselc = host_mselc
        self.phpsesid = phpsesid
        self.rmbrm = rmbrm
        self.sid = sid
        self.seller_board_name = seller_board_name
        self.seller_board_username = seller_board_username
        self.seller_board_password = seller_board_password

    def get_seller_board_cookies(self) -> Dict[str, str]:
        return {
            'PHPSESSID': self.phpsesid,
            'RMBRM': self.rmbrm,
            'sid': self.sid
        }

    def get_seller_central_cookies(self) -> Dict[str, str]:
        return {
            'ubid-main': self.ubid_main,
            '__Host-mselc': self.host_mselc,
            'at-main': self.at_main,
            'session-id': self.session_id
        }

    def get_adverting_cookies(self) -> Dict[str, str]:
        return {
            'session-id': self.session_id,
            'ubid-main': self.ubid_main,
            'at-main': self.at_main,
            'sst-main': self.sst_main
        }

    def save(self):
        DATABASE.updateById(self.id, self._get_data_dict())

    def create(self):
        self.auth()
        DATABASE.add(self._get_data_dict())

    def delete(self):
        DATABASE.deleteById(self.id)

    @staticmethod
    def all():
        return [Account(**i) for i in DATABASE.getAll()]

    def auth(self):
        from services.amazon.auth.sellerboard import SellerBoardAuthService

        auth_service = SellerBoardAuthService(self)

        while True:
            try:
                self.phpsesid, self.rmbrm, self.sid = auth_service.auth()
                break
            except UnauthorizedException:
                print('Ошибка авторизации в SellerBoard. Введите корректные данные!')
                self.seller_board_username = input('Введите логин от SellerBoard: ')
                self.seller_board_password = input('Введите пароль от SellerBoard: ')
            except NoAccountInSellerBoard:
                print(f'Аккаунт с названмем <{self.seller_board_name}> не найден в введнном аккаунте SellerBoard')
                self.seller_board_name = input('Введите название аккаунт в SellerBoard: ')

    def _get_data_dict(self) -> Dict[str, Any]:
        return {
            'id_': self.id,
            'name': self.name,
            'session_id': self.session_id,
            'ubid_main': self.ubid_main,
            'at_main': self.at_main,
            'sst_main': self.sst_main,
            'host_mselc': self.host_mselc,
            'seller_board_name': self.seller_board_name,
            'seller_board_username': self.seller_board_username,
            'seller_board_password': self.seller_board_password,
            'phpsesid': self.phpsesid,
            'rmbrm': self.rmbrm,
            'sid': self.sid
        }

    def __str__(self):
        return f'{self.name} ({self.id})'

    def __repr__(self):
        return f'{self.name} ({self.id})'
