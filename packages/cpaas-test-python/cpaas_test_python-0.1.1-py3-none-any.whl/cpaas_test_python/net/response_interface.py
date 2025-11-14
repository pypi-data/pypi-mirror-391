from __future__ import absolute_import, division, annotations, unicode_literals

import abc
from cpaas_test_python.exception.karaden_exception import KaradenException
from cpaas_test_python.model.karaden_object import KaradenObject


class ResponseInterface(metaclass=abc.ABCMeta):
    @abc.abstractproperty
    def error(self) -> KaradenException:
        raise NotImplementedError()

    @abc.abstractproperty
    def object(self) -> KaradenObject:
        raise NotImplementedError()

    @abc.abstractproperty
    def is_error(self) -> bool:
        raise NotImplementedError()

    @abc.abstractproperty
    def status_code(self) -> int:
        raise NotImplementedError()

    @abc.abstractproperty
    def headers(self) -> dict:
        raise NotImplementedError()
