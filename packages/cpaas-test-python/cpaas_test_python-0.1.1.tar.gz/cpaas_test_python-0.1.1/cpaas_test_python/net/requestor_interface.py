from __future__ import absolute_import, division, annotations, unicode_literals

import abc
from cpaas_test_python.request_options import RequestOptions
from cpaas_test_python.net.response_interface import ResponseInterface


class RequestorInterface(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def send(self, method: str, path: str, params: dict, data: dict, request_options: RequestOptions = None, is_no_contents: bool = False, allow_redirects: bool = True) -> ResponseInterface:
        raise NotImplementedError()
