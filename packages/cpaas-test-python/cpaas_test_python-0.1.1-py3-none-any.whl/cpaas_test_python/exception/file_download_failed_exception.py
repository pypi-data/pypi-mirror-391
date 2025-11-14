from __future__ import absolute_import, division, annotations, unicode_literals

from cpaas_test_python.exception.karaden_exception import KaradenException


class FileDownloadFailedException(KaradenException):
    def __init__(self):
        super().__init__(None, None)
