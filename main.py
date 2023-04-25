import sys
from typing import Optional

import pandas as pd

from handlers.account import AccountHandler
from handlers.collect_data import CollectDataHandler
from models import Account
from services.google.spreadsheet_service import PyGSheetsSpreadsheetService
from services.google.worksheet_service import PyGSheetsWorksheetService
from settings import logger, GOOGLE_FILE_NAME


def push_stats_to_google_sheet(df: pd.DataFrame):
    # Spreadsheet
    sh_service = PyGSheetsSpreadsheetService()
    sh, sh_is_created = sh_service.get_or_create(name=GOOGLE_FILE_NAME)
    print(sh.url)

    # Worksheet
    wh_service = PyGSheetsWorksheetService(spreadsheet=sh)
    ws, ws_is_created = wh_service.get_or_create('Auto collect')

    try:
        df_from_sh = ws.get_as_df(index_column=1)
    except ValueError:
        df_from_sh = ws.get_as_df()

    concatenated_df = pd.concat([df_from_sh, df], axis=1)
    ws.set_dataframe(concatenated_df, start='A1', copy_index=True)

    if sh_is_created:
        first_wks = sh[0]
        sh.del_worksheet(first_wks)

    logger.info('Successfully for all')


class App:
    def __init__(self) -> None:
        self.accounts = Account.all()
        self.selected_account: Optional[Account] = None

        self.accounts_handler = AccountHandler(self)
        self.collect_data_handler = CollectDataHandler(self)

        self.MAIN_MENU = {
            1: ('Аккаунты', self.show_accounts_menu),
            2: ('Выбрать аккаунт', self.accounts_handler.show_accounts),
            3: ('Сбор данных', self.show_collect_data_menu),
            0: ('Выйти', self.exit_program)
        }

    def show_main_menu(self):
        for key, value in self.MAIN_MENU.items():
            print(f'{key} - {value[0]}')

        while True:
            try:
                action = int(input('Выберите действие: '))
                self.MAIN_MENU[action][1]()
            except (ValueError, KeyError):
                print("Неизвестная команда. Попробуйте еще раз")
                continue

    @staticmethod
    def show_handler_menu(handler):
        for key, value in handler.actions.items():
            print(f'{key} - {value[0]}')

        while True:
            action = input('Выберите действие: ')

            if action in handler.actions:
                return handler.handle(action)
            else:
                print("Неизвестная команда. Попробуйте еще раз")

    def show_accounts_menu(self):
        self.show_handler_menu(self.accounts_handler)

    def show_collect_data_menu(self):
        result = self.show_handler_menu(self.collect_data_handler)
        df = pd.DataFrame.from_dict(
            result,
            orient='index',
            columns=[
                f'{self.collect_data_handler.start_date.strftime("%d.%m")}'
                f'-'
                f'{self.collect_data_handler.end_date.strftime("%d.%m")}'
            ]
        )
        push_stats_to_google_sheet(df)

    @staticmethod
    def exit_program():
        print("Выход из программы")
        sys.exit()

    def update_accounts_list(self):
        self.accounts = Account.all()

    def run(self):
        print('Добро пожаловать!')

        self.show_main_menu()


if __name__ == '__main__':
    app = App()
    app.run()
