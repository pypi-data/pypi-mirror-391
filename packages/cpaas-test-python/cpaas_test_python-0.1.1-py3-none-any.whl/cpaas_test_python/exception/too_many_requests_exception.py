from __future__ import absolute_import, division, annotations, unicode_literals

from cpaas_test_python.exception.karaden_exception import KaradenException


class TooManyRequestsException(KaradenException):
    STATUS_CODE = 429
