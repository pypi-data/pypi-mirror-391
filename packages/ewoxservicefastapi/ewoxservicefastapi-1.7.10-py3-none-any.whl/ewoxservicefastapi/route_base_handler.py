from typing import Any, Callable, List, Dict, Text, Optional, Tuple, Union, Awaitable, TypeVar, Type
from datetime import date, datetime, timedelta
from fastapi import APIRouter
from ewoxcore.monitoring.ilogger import ILogger
from ewoxcore.utils.json_util import JsonUtil
from ewoxservicefastapi.models.request_model import RequestModel
from ewoxservicefastapi.request_serializer import RequestSerializer
from ewoxservicefastapi.api_factory import APIFactory
from ewoxcore.service.service import get_service

T = TypeVar("T")

class RouteBaseHandler():
    def __init__(self) -> None:
        self._router: APIRouter = APIRouter()
        self._logger: ILogger | None = None


    @property
    def logger(self) -> ILogger:
        """ Get the logger for this handler. """
        if self._logger is None:
            self._logger = get_service(ILogger)
        return self._logger


    def parse_params(
        self,
        class_type:T,
        params: Optional[str]
    ) -> Optional[T]:
        """ Parse query parameters from the request. """
        args: Optional[T] = self.parse_data(class_type, params)

        return args
    

    def parse_data(
        self,
        class_type:T,
        data: Optional[str]
    ) -> Optional[T]:
        """ Parse data from the request. """
        if (data is None):
            return None

        args: Optional[T] = JsonUtil.deserialize_json64(class_type, data)

        return args


    def parse_body(
        self,
        body: Optional[str]
    ) -> Optional[T]:
        """ Parse the body of the request. """
        if (body is None):
            return None

        request:RequestModel = JsonUtil.deserialize_gen_object(RequestModel, body)
        model: Optional[T] = RequestSerializer.deserialize(request)

        return model


    def parse_request(
        self,
        request: RequestModel
    ) -> Optional[T]:
        """ Parse the body of the request. """
        if (request is None):
            return None

        model: Optional[T] = RequestSerializer.deserialize(request)

        return model


    def parse_request_model(
        self,
        request: Dict[str, Any],
        class_type:T
    ) -> Optional[T]:
        """ Parse the body of the request. """
        if (request is None):
            return None

        request_model:RequestModel = APIFactory.convert_to_request_model(request)
        model: Optional[T] = RequestSerializer.deserialize(request_model)
        if (model is not None):
            if (isinstance(model, class_type) == False):
                return None

        return model


    def log_error(
            self,
            error: Any,
            message: str = "",
            args: Optional[Any] = None,
        ) -> None:
            """ Log an error message. """
            self.logger.error({
                "error": error,
                "message": message,
                "args": args,
            })
