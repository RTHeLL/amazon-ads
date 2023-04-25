from typing import Dict, Any

import requests

from models import Account
from services.requester import Requester


class BaseService:
    def __init__(self, account: Account):
        self.account = account
        self.requester = Requester()
