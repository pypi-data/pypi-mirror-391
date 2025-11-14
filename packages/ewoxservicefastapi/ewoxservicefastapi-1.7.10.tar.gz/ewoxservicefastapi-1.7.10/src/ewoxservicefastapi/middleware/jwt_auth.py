from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.responses import JSONResponse
from fastapi import HTTPException, Request, status, Response
from ewoxcore.client.status_code import StatusCode
from ewoxcore.service.interfaces.iauthorizer import IAuthorizer
from ewoxcore.service.service import get_service
from ewoxservicefastapi.api_factory import APIFactory

class JWTAuthMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, exclude_urls:list[str]=[]) -> None:
        super().__init__(app)
        self._exclude_urls = exclude_urls


    async def dispatch(self, request: Request, call_next):
        try:
            if request.method == "OPTIONS":
                return Response(status_code=204)

            # Skip auth for public routes if needed
            # if request.url.path in ["/login", "/register", "/signup"]:
            if request.url.path in self._exclude_urls:
                return await call_next(request)

            auth_header = request.headers.get("Authorization")
            if auth_header is None or not auth_header.startswith("Bearer "):
                return APIFactory.create_empty_response(StatusCode.Unauthorized, "Authorization header missing or invalid")

            token = auth_header.split(" ")[1]

            authorizer:IAuthorizer = get_service(IAuthorizer)
            res:bool = authorizer.is_authorized(token)
            if (res == False):
                return APIFactory.create_empty_response(StatusCode.Forbidden, "Not authorized")

            payload = authorizer.get_payload(token)
            if (payload is not None):
                request.state.payload = payload
        except HTTPException as e:
            return APIFactory.create_empty_response(e.status_code, e.detail)

        return await call_next(request)
