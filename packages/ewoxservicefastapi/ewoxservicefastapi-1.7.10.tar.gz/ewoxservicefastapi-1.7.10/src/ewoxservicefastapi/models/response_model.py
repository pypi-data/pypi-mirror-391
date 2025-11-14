from typing import Any, Callable, List, Dict, Text, Optional, Tuple, Union, Awaitable, TypeVar, Type
from datetime import date, datetime, timedelta
from ewoxcore.client.status_code import StatusCode
from ewoxcore.decorators.serializable import Serializable


@Serializable
class ResponseModel:
    def __init__(self, data: str="", code: int=int(StatusCode.Ok), message: str="", iscompressed: bool=True, correlationid: str=""):
        self.data:str = data
        self.code:int = int(code)
        self.message:str = message
        self.iscompressed:bool = iscompressed
        self.correlationid:str = correlationid
