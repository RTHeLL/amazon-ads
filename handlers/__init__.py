from abc import ABC, abstractmethod


class BaseHandler(ABC):
    def __init__(self, app) -> None:
        super().__init__()

        self.app = app

    @property
    @abstractmethod
    def actions(self):
        pass

    @abstractmethod
    def handle(self, action: str):
        pass
