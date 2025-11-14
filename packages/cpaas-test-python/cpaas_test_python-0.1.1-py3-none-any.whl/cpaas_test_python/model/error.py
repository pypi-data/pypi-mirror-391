from __future__ import absolute_import, division, annotations, unicode_literals

from cpaas_test_python.model.karaden_object import KaradenObject
from cpaas_test_python.model.karaden_object_interface import KaradenObjectInterface
from cpaas_test_python.model.error_interface import ErrorInterface


class Error(ErrorInterface, KaradenObject):
    OBJECT_NAME = 'error'

    @property
    def code(self) -> str:
        return self.get_property('code')

    @property
    def message(self) -> str:
        return self.get_property('message')

    @property
    def errors(self) -> KaradenObjectInterface:
        return self.get_property('errors')
