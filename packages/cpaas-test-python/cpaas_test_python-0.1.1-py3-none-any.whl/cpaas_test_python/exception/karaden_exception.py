from __future__ import absolute_import, division, annotations, unicode_literals

from cpaas_test_python.model.error_interface import ErrorInterface


class KaradenException(Exception):
    def __init__(self, headers: dict, body: str, error: ErrorInterface = None):
        self.headers = headers
        self.body = body
        self.error = error
