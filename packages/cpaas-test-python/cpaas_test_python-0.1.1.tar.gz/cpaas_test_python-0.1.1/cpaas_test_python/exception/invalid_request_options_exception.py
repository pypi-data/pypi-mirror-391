from __future__ import absolute_import, division, annotations, unicode_literals

from cpaas_test_python.exception.karaden_exception import KaradenException
from cpaas_test_python.model.error_interface import ErrorInterface


class InvalidRequestOptionsException(KaradenException):
    def __init__(self, error: ErrorInterface = None):
        super().__init__(None, None, error)
