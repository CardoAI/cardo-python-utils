import logging
from typing import Literal, Optional

from jwt.exceptions import InvalidTokenError

from django.conf import settings
from django.http import HttpRequest
from ninja.security import HttpBearer
from ninja.errors import AuthenticationError, HttpError

from .utils import (
    acreate_or_update_user,
    create_or_update_user,
    decode_jwt,
    TokenPayload,
)

logger = logging.getLogger()


class AuthBearer(HttpBearer):
    def __call__(self, request: HttpRequest):
        token = self._get_token(request)
        if not token:
            return None

        return self.authenticate(request, token)

    def authenticate(self, request: HttpRequest, token: str) -> TokenPayload:
        payload = self._decode_token(token)

        username = self._get_username(payload)

        user = create_or_update_user(username, payload)

        self._verify_scopes(request, payload)

        request.user = user

        # The return value is stored in request.auth
        return payload

    def _get_token(self, request: HttpRequest) -> Optional[str]:
        """
        This part of the token validation is similar to what 
        django-ninja is doing in HttpBearer.__call__
        """
        headers = request.headers
        auth_value = headers.get(self.header)
        if not auth_value:
            return None
        parts = auth_value.split(" ")

        if parts[0].lower() != self.openapi_scheme:
            if settings.DEBUG:
                logger.error(f"Unexpected auth - '{auth_value}'")
            return None

        return " ".join(parts[1:])

    def _decode_token(self, token: str) -> TokenPayload:
        try:
            return decode_jwt(token)
        except InvalidTokenError as e:
            raise AuthenticationError(f"Invalid token: {str(e)}") from e

    def _get_username(self, payload: TokenPayload) -> str:
        try:
            return payload["preferred_username"]
        except KeyError as e:
            raise AuthenticationError(
                "Invalid token: 'preferred_username' claim not present."
            ) from e

    def _verify_scopes(self, request, token_payload):
        allowed_scopes = self._get_view_allowed_scopes(request)

        if allowed_scopes == "*":
            return

        token_scopes_str = token_payload.get("scope", "")
        token_scopes = set(token_scopes_str.split())

        for scope in allowed_scopes:
            if f"{getattr(settings, 'JWT_SCOPE_PREFIX', '')}:{scope}" in token_scopes:
                return

        raise HttpError(403, "You are not allowed to access this resource.")

    def _get_view_allowed_scopes(self, request):
        view_function = self._get_view_function(request)
        scopes = getattr(view_function, "_allowed_scopes", None)

        if scopes is None:
            raise Exception(
                f"No allowed_scopes defined on the view {view_function.__name__}."
                "Add the decorator @allowed_scopes([...]) or @allowed_scopes('*') to the view."
            )

        return scopes

    def _get_view_function(self, request):
        view_func = request.resolver_match.func.__self__
        method = request.method.upper()
        for operation in view_func.operations:
            if operation.methods and method in operation.methods:
                return operation.view_func

        raise Exception(
            f"Could not determine the view function for {request.method} {request.path}."
        )


class AuthBearerAsync(AuthBearer):
    """
    Same as AuthBearer, but with async __call__ and authenticate methods.
    """

    async def __call__(self, request: HttpRequest):
        token = self._get_token(request)
        if not token:
            return None

        return await self.authenticate(request, token)

    async def authenticate(self, request: HttpRequest, token: str) -> TokenPayload:
        payload = self._decode_token(token)

        username = self._get_username(payload)

        user = await acreate_or_update_user(username, payload)

        self._verify_scopes(request, payload)

        request.user = user

        # The return value is stored in request.auth
        return payload


def allowed_scopes(scopes: list[str] | Literal["*"]):
    """
    A decorator that attaches a list of required scopes to a view function
    in the attribute `_allowed_scopes`.
    This is used by a global authenticator to perform authorization checks.
    """

    def decorator(view_func):
        if not isinstance(scopes, list) and scopes != "*":
            raise ValueError("scopes must be a list of strings or '*'")

        setattr(view_func, "_allowed_scopes", scopes)
        return view_func

    return decorator
