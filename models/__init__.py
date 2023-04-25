from typing import Dict, Any, Optional

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
            rmbrm: str,
            phpsesid: str,
            id_: Optional[int] = None,
    ) -> None:
        self.id = id_

        self.name = name
        self.session_id = session_id
        self.ubid_main = ubid_main
        self.at_main = at_main
        self.sst_main = sst_main
        self.host_mselc = host_mselc
        self.rmbrm = rmbrm
        self.phpsesid = phpsesid

    def get_seller_board_cookies(self) -> Dict[str, str]:
        return {
            'RMBRM': self.rmbrm,
            'PHPSESSID': self.phpsesid
        }

    def get_seller_central_cookies(self) -> Dict[str, str]:
        return {
            'ubid-main': self.ubid_main,
            '__Host-mselc': self.host_mselc,
            'at-main': self.at_main,
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
        DATABASE.add(self._get_data_dict())

    def delete(self):
        DATABASE.deleteById(self.id)

    @staticmethod
    def all():
        return [Account(**i) for i in DATABASE.getAll()]

    def _get_data_dict(self) -> Dict[str, Any]:
        return {
            'id_': self.id,
            'name': self.name,
            'session_id': self.session_id,
            'ubid_main': self.ubid_main,
            'at_main': self.at_main,
            'sst_main': self.sst_main,
            'host_mselc': self.host_mselc,
            'rmbrm': self.rmbrm,
            'phpsesid': self.phpsesid
        }

    def __str__(self):
        return f'{self.name} ({self.id})'

    def __repr__(self):
        return f'{self.name} ({self.id})'
