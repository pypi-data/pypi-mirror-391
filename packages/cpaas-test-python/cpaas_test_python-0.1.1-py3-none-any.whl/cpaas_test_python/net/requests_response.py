from __future__ import absolute_import, division, annotations, unicode_literals

import requests
from cpaas_test_python.exception.karaden_exception import KaradenException
from cpaas_test_python.exception.unexpected_value_exception import UnexpectedValueException
from cpaas_test_python.exception.unknown_error_exception import UnknownErrorException
from cpaas_test_python.request_options import RequestOptions
from cpaas_test_python.utility import Utility
from cpaas_test_python.model.karaden_object import KaradenObject
from cpaas_test_python.model.error import Error
from cpaas_test_python.net.response_interface import ResponseInterface


class RequestsResponse(ResponseInterface):
    errors: dict = {}

    @property
    def error(self) -> KaradenException:
        return self._error

    @property
    def object(self) -> KaradenObject:
        return self._object

    @property
    def is_error(self) -> bool:
        return self._error is not None

    @property
    def status_code(self) -> int:
        raise NotImplementedError()

    @property
    def headers(self) -> dict:
        raise NotImplementedError()

    def __init__(self, response: requests.Response, request_options: RequestOptions) -> None:
        self._error = None
        self._object = None
        self._interpret(response, request_options)

    def _interpret(self, response: requests.Response, request_options: RequestOptions) -> None:
        status_code = response.status_code
        body = response.text
        try:
            contents = response.json()
        except requests.JSONDecodeError:
            headers = response.headers
            self._error = UnexpectedValueException(status_code, headers, body)
            return

        obj = Utility.convert_to_karaden_object(contents, request_options)
        if status_code < 200 or status_code >= 400:
            headers = response.headers
            if obj.object == 'error':
                self._error = self.handle_error(status_code, headers, body, obj)
            else:
                self._error = UnexpectedValueException(status_code, headers, body)
            return

        self._object = obj

    def handle_error(self, status_code: int, headers: dict, body: str, error: Error) -> KaradenException:
        if status_code in self.errors:
            cls = self.errors[status_code]
            return cls(headers, body, error)
        else:
            return UnknownErrorException(status_code, headers, body, error)
