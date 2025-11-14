from typing import Any, Callable, List, Dict, Text, Optional, Tuple, Union, Awaitable, TypeVar, Type
from datetime import date, datetime, timedelta
from ewoxcore.client.status_code import StatusCode
from ewoxcore.decorators.serializable import Serializable


@Serializable
class UserOAuthModel:
    def __init__(self, email: str="", firstname: str="", lastname: str="", redirect_url: str=""):
        self.email: str = email
        self.firstname: str = firstname
        self.lastname: str = lastname
        self.redirectUrl: str = redirect_url
