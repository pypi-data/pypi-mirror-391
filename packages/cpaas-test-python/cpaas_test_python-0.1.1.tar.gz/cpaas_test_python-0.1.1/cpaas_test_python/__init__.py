from __future__ import absolute_import, division, annotations, unicode_literals

from cpaas_test_python.config import Config
from cpaas_test_python.request_options import RequestOptions
from cpaas_test_python.model.karaden_object import KaradenObject
from cpaas_test_python.model.message import Message
from cpaas_test_python.model.bulk_file import BulkFile
from cpaas_test_python.model.bulk_message import BulkMessage
from cpaas_test_python.model.error import Error
from cpaas_test_python.model.collection import Collection
from cpaas_test_python.exception.bad_request_exception import BadRequestException
from cpaas_test_python.exception.forbidden_exception import ForbiddenException
from cpaas_test_python.exception.not_found_exception import NotFoundException
from cpaas_test_python.exception.too_many_requests_exception import TooManyRequestsException
from cpaas_test_python.exception.unauthorized_exception import UnauthorizedException
from cpaas_test_python.exception.unprocessable_entity_exception import UnprocessableEntityException
from cpaas_test_python.exception.invalid_request_options_exception import InvalidRequestOptionsException
from cpaas_test_python.net.requests_requestor import RequestsRequestor
from cpaas_test_python.net.requests_response import RequestsResponse
from cpaas_test_python.utility import Utility

from .__version__ import (
    __version__,
)

Config.VERSION = __version__
Config.api_base = Config.DEFAULT_API_BASE
Config.api_version = Config.DEFALUT_API_VERSION

Utility.DEFAULT_OBJECT_NAME = Message.OBJECT_NAME
Utility.object_types = {
    KaradenObject.OBJECT_NAME: KaradenObject,
    Collection.OBJECT_NAME: Collection,
    Message.OBJECT_NAME: Message,
    Error.OBJECT_NAME: Error,
    BulkFile.OBJECT_NAME: BulkFile,
    BulkMessage.OBJECT_NAME: BulkMessage,
}

Message.requestor = RequestsRequestor()
BulkFile.requestor = RequestsRequestor()
BulkMessage.requestor = RequestsRequestor()

RequestsResponse.errors = {
    BadRequestException.STATUS_CODE: BadRequestException,
    UnauthorizedException.STATUS_CODE: UnauthorizedException,
    ForbiddenException.STATUS_CODE: ForbiddenException,
    NotFoundException.STATUS_CODE: NotFoundException,
    UnprocessableEntityException.STATUS_CODE: UnprocessableEntityException,
    TooManyRequestsException.STATUS_CODE: TooManyRequestsException,
}

RequestOptions.errors = KaradenObject
RequestOptions.error = Error
RequestOptions.validation_exception = InvalidRequestOptionsException
