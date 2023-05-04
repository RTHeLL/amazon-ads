from typing import Tuple

from handlers import BaseHandler
from models import Account
from settings import YES_CHOICES, NO_CHOICES


class AccountHandler(BaseHandler):
    @property
    def actions(self):
        return {
            'add': ('Добавить аккаунт', self._create),
            'update': ('Изменить аккаунт', self._update),
            'delete': ('Удалить аккаунт', self._delete),
            'back': ('Назад', self.app.show_main_menu)
        }

    def handle(self, action: str):
        return self.actions[action][1]()

    @staticmethod
    def _create():
        Account(
            name=input('Введите название аккаунта: '),
            session_id=input('Введите ssesion_id: '),
            ubid_main=input('Введите ubid_main: '),
            at_main=input('Введите at_main: '),
            sst_main=input('Введите sst_main: '),
            host_mselc=input('Введите host_mselc: '),
            seller_board_name=input('Введите название аккаунт в SellerBoard: '),
            seller_board_username=input('Введите логин от SellerBoard: '),
            seller_board_password=input('Введите пароль от SellerBoard: ')
        ).create()
        print('Аккаунт успешно добавлен!')

    def _update(self):
        if not self.app.selected_account:
            print('У вас не выбран аккаунт')
            return

        for key in self.app.selected_account.__dict__.keys():
            print(f'{key}')

        while True:
            field_name = input('Выберите поле, которое нужно изменить: ')

            if not hasattr(self.app.selected_account, field_name):
                print('У аккаунта нет такого поля. Попробуйте еще раз')
            elif field_name == 'id':
                print('ID нельзя изменить')
            else:
                setattr(self.app.selected_account, field_name, input('Введите новое значение: '))
                break

        self.app.selected_account.save()
        print('Аккаунт успешно обновлен!')

    def _delete(self):
        if not self.app.selected_account:
            print('У вас не выбран аккаунт')
            return

        self.app.selected_account.delete()
        print('Аккаунт успешно удален!')

    def show_accounts(self):
        self.app.update_accounts_list()

        if not self.app.accounts:
            user_input = input('У вас нет добавленных аккаунтов. Хотите добавить? [Y/N]').lower()

            while True:
                if user_input in YES_CHOICES:
                    print('test add account')
                    break
                elif user_input in NO_CHOICES:
                    self.app.show_main_menu()
                else:
                    print('Неизвестная команда')
        else:
            self.select_account()

    def select_account(self):
        for index, account in enumerate(self.app.accounts):
            print(f'{index + 1}. {account}')

        while True:
            try:
                self.app.selected_account = self.app.accounts[int(
                    input('Выберите аккаунт (введите его номер из списка): ')
                ) - 1]
                break
            except ValueError:
                print('Нужно ввести число! \n')
            except IndexError:
                print('Такого аккаунта нет! \n')
