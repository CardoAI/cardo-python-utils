from typing import Literal

from jwt.exceptions import InvalidTokenError

from django.conf import settings
from ninja.security import HttpBearer
from ninja.errors import AuthenticationError, HttpError

from .utils import create_or_update_user, decode_jwt


class AuthBearer(HttpBearer):
    def authenticate(self, request, token):
        try:
            payload = decode_jwt(token)
        except InvalidTokenError as e:
            raise AuthenticationError(f"Invalid token: {str(e)}") from e

        try:
            username = payload["preferred_username"]
        except KeyError as e:
            raise AuthenticationError(
                "Invalid token: preferred_username not present."
            ) from e

        user = create_or_update_user(username, payload)

        self._verify_scopes(request, payload)

        request.user = user

        # The return value is stored in request.auth
        return payload

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
