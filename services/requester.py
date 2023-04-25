import logging
import time
from typing import Any, Callable, Dict, Optional

import requests

from exceptions import DataNotFoundException
from settings import API_CALL_TRIES, TIMEOUT, TIME_TO_SLEEP


logger = logging.getLogger(__name__)


class Requester:
    def __init__(self) -> None:
        self.session = requests.Session()

    def make_request(  # type: ignore
            self,
            method: Callable[..., requests.Response],
            url: str,
            headers: Dict[str, Any],
            cookies: Optional[Dict[str, Any]] = None,
            json_response: bool = False,
            raise_exceptions: bool = False,
            *args,
            **kwargs
    ) -> requests.Response:
        try:
            logger.info(f'start request: {method.__name__} - {url}')
            response = method(url, headers=headers, timeout=TIMEOUT, cookies=cookies, *args, **kwargs)
            if response.status_code == 401:
                if not cookies:
                    logger.error(f'no cookies for {url}')
                else:
                    logger.warning(f'Company with {cookies.get("x-supplier-id-external")} '
                                   f'x-supplier-id returned 401 - {url} [{method.__name__}]')
            if response.status_code == 429:
                time.sleep(TIME_TO_SLEEP)
                return self.make_request(method=method, url=url, headers=headers, cookies=cookies,
                                         json_response=json_response,
                                         raise_exceptions=raise_exceptions,
                                         *args, **kwargs)  # type: ignore
            if json_response:
                return response.json()

            logger.info(f'end request: {method.__name__} - {response.status_code} ({url})')

            if response.status_code != 200:
                logger.error(f'Error status code: {response.status_code}')

            return response
        except requests.exceptions.ReadTimeout:
            time.sleep(TIME_TO_SLEEP)

    def make_get_request(
            self,
            url: str,
            headers: Dict[str, Any],
            cookies: Dict[str, Any],
            params: Any = None,
            call_tries: int = API_CALL_TRIES,
            json_response: bool = True,
            raise_exceptions: bool = False
    ) -> requests.Response:
        for _ in range(call_tries):
            response = self.make_request(
                method=self.session.get,
                url=url,
                params=params,
                cookies=cookies,
                headers=headers,
                json_response=json_response,
                raise_exceptions=raise_exceptions
            )

            if response is None:
                continue

            return response

        raise DataNotFoundException('Data not found')

    def make_post_request(
            self,
            url: str,
            headers: Dict[str, Any],
            cookies: Dict[str, Any],
            params: Any = None,
            data=None,
            json=None,
            call_tries: int = API_CALL_TRIES,
            json_response: bool = True,
            raise_exceptions: bool = False
    ) -> requests.Response:
        for _ in range(call_tries):
            response = self.make_request(
                method=self.session.post,
                url=url,
                params=params,
                data=data,
                json=json,
                cookies=cookies,
                headers=headers,
                json_response=json_response,
                raise_exceptions=raise_exceptions)

            if response is None:
                continue

            return response

        raise DataNotFoundException('Data not found')
