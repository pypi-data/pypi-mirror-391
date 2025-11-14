from typing import Any, Callable, List, Dict, Text, Optional, Tuple, Union, Awaitable, TypeVar, Type
from datetime import date, datetime, timedelta
import uvicorn
import os
import uvloop
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from ewoxcore.constants.server_env import ServerEnv
from ewoxcore.service.interfaces.istartup import IStartup
from ewoxcore.service.interfaces.iservice import IService
from ewoxcore.service.service_app_base import ServiceAppBase
from ewoxcore.service.class_registry import ClassRegistry
from ewoxcore.utils.task_util import TaskUtil
from ewoxcore.message.message_args import MessageArgs
from ewoxservicefastapi.models.request_model import RequestModel
from ewoxservicefastapi.models.response_model import ResponseModel
from ewoxservicefastapi.routers import keepalive
from ewoxservicefastapi.middleware.jwt_auth import JWTAuthMiddleware

T = TypeVar('T')


class ServiceApp(ServiceAppBase):
    def __init__(self, service_name:str="", startup:IStartup=None, service:IService=None) -> None:
        """ Initializes the ServiceApp with a FastAPI instance. """
        super().__init__(service_name, startup, service)
        self._app:FastAPI = FastAPI()


    def _on_start_event(self):
        TaskUtil.create_task(self._start_async())


    def _setup_routes(self) -> None:
        ClassRegistry.add(RequestModel)
        ClassRegistry.add(ResponseModel)
        ClassRegistry.add(MessageArgs)

        self._app.include_router(keepalive.router)


    def addCors(self, origins:List[str], include_localhost:bool=False) -> None:
        """ Adds CORS middleware to the FastAPI app."""
        if isinstance(origins, str):
            raise TypeError("origins must be a list of strings.")
        
        # if include_localhost:
        #     origins.append(r"|^https?:\/\/localhost(:[0-9]+)?$")
        origin_regex: Optional[str] = None
        if include_localhost:
            # Match http://localhost, http://localhost:3000, https://localhost:5173, etc.
            origin_regex = r"^https?://localhost(?::\d+)?$"
            # Optional: also cover 127.0.0.1 (common with Vite)
            # origin_regex = r"^https?://(localhost|127\.0\.0\.1)(?::\d+)?$"

        self._app.add_middleware(
            CORSMiddleware,
            allow_origins=origins,
            allow_origin_regex=origin_regex,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )


    def addJWTAuth(self, exclude_urls:list[str]=["/login", "/register", "/signup"]) -> None:
        """ Adds JWT authentication middleware to the FastAPI app.
            Args:
                exclude_urls (list[str], optional): List of URL paths to exclude from JWT authentication. Defaults to ["/login", "/register", "/signup"]. """
        self._app.add_middleware(JWTAuthMiddleware, exclude_urls=exclude_urls)


    def addSessionAuth(self, env_session_secret_key:str=os.getenv("SESSION_SECRET")) -> None:
        """ Adds session authentication middleware to the FastAPI app."""
        self._app.add_middleware(SessionMiddleware, secret_key=env_session_secret_key)


    def start(self, server_port:int = 80, debug_server_port:int=0) -> None:
        """ Starts the FastAPI server with the specified port. """
        uvloop.install()
        server_env:str = os.getenv(ServerEnv.ENVIRONMENT)
        if ((server_env == ServerEnv.DEVELOPMENT) & (debug_server_port != 0)):
            server_port = debug_server_port

        self._app.add_event_handler("startup", lambda: self._on_start_event())
        self._setup_routes()

#        uvicorn.run(self._app, host="127.0.0.1", port=server_port)
        uvicorn.run(self._app, host="0.0.0.0", port=server_port)
