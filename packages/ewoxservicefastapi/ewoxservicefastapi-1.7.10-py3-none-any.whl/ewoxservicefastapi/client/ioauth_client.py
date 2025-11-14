from typing import Any, Callable, List, Dict, Text, Optional, Tuple, Union, Awaitable, TypeVar, Type
from abc import ABC, abstractmethod

from ewoxservicefastapi.models.user_oauth_model import UserOAuthModel


class IOAuthClient(ABC):
    @abstractmethod
    def register(self, name:str, client_id:str, client_secret:str, server_metadata_url:str, config:dict[str, str]) -> None:
        """ Registers an OAuth provider with the FastAPI app.
            Args:
                name (str): The name of the OAuth provider.
                client_id (str): The client ID for the OAuth provider.
                client_secret (str): The client secret for the OAuth provider.
                server_metadata_url (str): The URL for the OAuth provider's server metadata.
                config (dict[str, str]): Additional configuration parameters for the OAuth provider."""
        raise NotImplementedError("Implement inherited method")


    @abstractmethod
    def is_registered(self, name:str) -> bool:
        raise NotImplementedError("Implement inherited method")


    @abstractmethod
    async def authorize_redirect(self, request, name:str, redirect_url:str) -> Any:
        """ Initiates the OAuth authorization flow by redirecting to the provider's authorization URL.
            Args:
                name (str): The name of the OAuth provider.
                redirect_url (str): The URI to redirect to after authorization.
            Returns:
                A RedirectResponse to the provider's authorization URL."""
        raise NotImplementedError("Implement inherited method")


    @abstractmethod
    async def authorize_access_token(self, request, name:str) -> UserOAuthModel:
        """ Handles the OAuth callback and retrieves the access token.
            Args:
                request (Request): The incoming FastAPI request.
                name (str): The name of the OAuth provider.
                redirect_url (str): The URL to redirect to after obtaining the access token.
            Returns:
                A RedirectResponse to the specified redirect URL."""
        raise NotImplementedError("Implement inherited method")
