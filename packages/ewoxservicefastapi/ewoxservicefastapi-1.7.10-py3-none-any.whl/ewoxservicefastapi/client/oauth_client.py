from typing import Any, Callable, Generic, List, Dict, Text, Optional, Tuple, Union, TypeVar, Type, cast
from datetime import date, datetime, timedelta, timezone
import time

import secrets
from jose import jwt, jwe, JWTError


import base64
import json
import os
from urllib.parse import ParseResult, urlparse, parse_qs, urlencode, urlunparse
from fastapi import Request
from fastapi.responses import RedirectResponse
from authlib.oidc.core import UserInfo
from authlib.integrations.starlette_client import OAuth
from authlib.integrations.starlette_client.apps import StarletteOAuth2App
from ewoxcore.monitoring.ilogger import ILogger
from ewoxcore.service.service import get_service
from ewoxservicefastapi.client.ioauth_client import IOAuthClient
from ewoxservicefastapi.models.user_oauth_model import UserOAuthModel


class OAuthClient(IOAuthClient):
    def __init__(self, verbose: bool=False) -> None:
        """ Initializes the OAuthClient.
            Args:
                verbose (bool): If True, enables verbose logging. """
        self._oauth:Optional[OAuth] = None
        self._logger:ILogger = get_service(ILogger)
        self._provider_names:list[str] = []
        self._verbose: bool = verbose


    def register(self, name:str, client_id:str, client_secret:str, server_metadata_url:str, config:dict[str, str]) -> None:
        """ Registers an OAuth provider with the FastAPI app.
            Args:
                name (str): The name of the OAuth provider.
                client_id (str): The client ID for the OAuth provider.
                client_secret (str): The client secret for the OAuth provider.
                server_metadata_url (str): The URL for the OAuth provider's server metadata.
                config (dict[str, str]): Additional configuration parameters for the OAuth provider."""
        if self._oauth is None:
            self._oauth = OAuth()

        self._oauth.register(
            name=name,
            client_id=client_id,
            client_secret=client_secret,
            server_metadata_url=server_metadata_url,
            client_kwargs=config
        )

        if (name not in self._provider_names):
            self._provider_names.append(name)

    
    def is_registered(self, name:str) -> bool:
        """ Checks if an OAuth provider is registered.
            Args:
                name (str): The name of the OAuth provider.
            Returns:
                True if the provider is registered, False otherwise."""
        if (name not in self._provider_names):
            return False

        return True


    def _get_client(self, name:str) -> StarletteOAuth2App:
        """ Retrieves an OAuth client by name.
            Args:
                name (str): The name of the OAuth provider.
            Returns:
                The OAuth client instance."""
        if self._oauth is None:
            raise ValueError("OAuth has not been initialized. Please register at least one OAuth provider.")

        client = self._oauth.create_client(name)
        if client is None:
            raise ValueError(f"OAuth client '{name}' not found.")

        return client
 

    async def authorize_redirect(self, request:Request, name:str, redirect_url:str) -> RedirectResponse:
        """ Initiates the OAuth authorization flow by redirecting to the provider's authorization URL.
            Args:
                name (str): The name of the OAuth provider.
                redirect_url (str): The URI to redirect to after authorization.
            Returns:
                A RedirectResponse to the provider's authorization URL."""
        client = self._get_client(name)
        state = self._generate_state(request)
        response:RedirectResponse = await client.authorize_redirect(request, redirect_url, state=state)

        return response
    

    async def authorize_access_token(self, request:Request, name:str) -> Optional[UserOAuthModel]:
        """ Handles the OAuth callback and retrieves the access token.
            Args:
                request (Request): The incoming FastAPI request.
                name (str): The name of the OAuth provider.
            Returns:
                A UserOAuthModel containing user information."""
        user:Optional[UserOAuthModel] = None

        try:
            client = self._get_client(name)
            token:dict[str, Any] = await client.authorize_access_token(request)
            if (self._verbose):
                print("TOKEN RESPONSE:", json.dumps(token, indent=2))

            user_info:dict[str, Any] = token.get("userinfo", {})
            if (self._verbose):
                print("User Info:", json.dumps(user_info, indent=2))
     
            email:str = ""
            firstname:str = ""
            lastname:str = ""

            # if (name == "microsoft") and ("email" not in user_info):
            if ("email" not in user_info):
                email = user_info.get("preferred_username", "")
                fullname:str = user_info.get("name", "")
                if (fullname):
                    firstname = fullname.split(" ")[0] if fullname else ""
                    lastname = " ".join(fullname.split(" ")[1:]) if fullname and len(fullname.split(" ")) > 1 else ""
            elif (user_info):
                email = user_info.get("email", "")
                firstname = user_info.get("given_name", "")
                lastname = user_info.get("family_name", "")

            if (self._verbose):
                print(f"User Info Email: {email}, First Name: {firstname}, Last Name: {lastname}")

            redirect_url:str = self._get_redirect_url_from_state(request)
            if (self._verbose):
                print(f"Redirect URL from state: {redirect_url}")
            # redirect_url2 = "http://localhost:8080/"

            user = UserOAuthModel(
                email=email,
                firstname=firstname,
                lastname=lastname,
                redirect_url=redirect_url
            )

            # user:UserInfo = await client.parse_id_token(request, token)
            # user:UserInfo = None
            # if "id_token" in token:
            #     user = await client.parse_id_token(request, token)
            # else:
            #     user = await client.userinfo(token=token)


            # space_id:str = "a418e91f-452a-4a0a-b905-447e2187758f" # Flextribe Development
            # space_user_id:str = "965d0542-0140-424e-ad86-f52a850822fb" # mp@flextribe.io is employee
            # user_id:str = "a97ac373-1fd0-4554-8599-28c7f0df4d51" #
            # payload:dict[str, Any] = dict()
            # payload.update({"iss": os.getenv("JWT_ISSUER")})
            # payload.update({"sub": user_id})
            # payload.update({"space": space_id})
            # payload.update({"strategy": name})

            # _algorithm:str = "HS256"
            # _token_secret:str = os.getenv("JWT_SECRET")
            # expires_delta:float = 30 * 24 * 60 * 60 * 1000

            # # expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=self._token_timeout))
            # expire_at:float = time.time() + expires_delta
            # payload.update({"exp": expire_at})
            # # expire = datetime.now(timezone.utc) + timedelta(seconds=expires_delta)
            # # payload.update({"exp": expire})

            # jwt_token:str = jwt.encode(payload, _token_secret, algorithm=_algorithm)

            # redirect_url2 = self.append_token_to_url(redirect_url2, jwt_token)
            # response = RedirectResponse(url=redirect_url2)
        except Exception as e:
            self._logger.error(f"Error during OAuth callback: {e}")
            # error_redirect_url:str = self.get_redirect_url_from_state(request, is_error=True)
            # response = RedirectResponse(url=error_redirect_url)

        return user


    # def append_token_to_url(self, url: str, token: str) -> str:
    #     parsed:ParseResult = urlparse(url)
    #     query_params:dict[str, Any] = parse_qs(parsed.query)
    #     query_params["_ft_c"] = token

    #     new_query:str = urlencode(query_params, doseq=True)
    #     new_url = urlunparse(parsed._replace(query=new_query))

    #     return new_url


    # def is_base64(self, s: str) -> bool:
    #     try:
    #         return base64.b64encode(base64.b64decode(s)).decode() == s
    #     except Exception:
    #         return False


    def _get_url_from_request(self, request: Request) -> str:
        origin:str = request.headers.get("origin") or request.headers.get("referer") or ""

        return origin.rstrip("/")


    def _get_redirect_url_from_state(self, request: Request, is_error: bool = False) -> str:
        state_param = request.query_params.get("state", "")
        state:dict[str, Any] = json.loads(base64.b64decode(state_param).decode())
        if not is_error:
            return f"{state.get('redirect', '')}{state.get('success_uri', '')}"

        return f"{state.get('redirect', '')}{state.get('error_uri', '')}"


    def _generate_state(self, request: Request) -> str:
        state:dict[str, Any] = {
            "time": int(os.times().elapsed),
            "redirect": self._get_url_from_request(request),
            "success_uri": request.query_params.get("success_uri", ""),
            "error_uri": request.query_params.get("error_uri", "")
        }

        encoded_state: str = base64.b64encode(json.dumps(state).encode()).decode()

        return encoded_state


    # def check_state(self, request: Request) -> bool:
    #     state = request.query_params.get("state", "")
    #     return bool(state and self.is_base64(state))


"""
const successRedirect = (
  req: FastifyRequest,
  reply: FastifyReply,
  data: { token: string; expires: number },
) => {
  const url = getRedirectUrlFromState(req)
  const queryStringDelimiter = url.includes("?") ? "&" : "?"
  const redirectUrl:string = `${url}${queryStringDelimiter}_ft_c=${data.token}`
    return reply.redirect(
    `${url}${queryStringDelimiter}_ft_c=${data.token}`,
  )
}

const errorRedirect = (
  req: FastifyRequest,
  reply: FastifyReply,
  error: unknown,
) => {
  const url = getRedirectUrlFromState(req)
  const queryStringDelimiter = url.includes("?") ? "&" : "?"
  return reply.redirect(
    `${getRedirectUrlFromState(req, true)}${queryStringDelimiter}error=${error}`,
  )
}
"""