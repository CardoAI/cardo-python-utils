from django.conf import settings
from jwt.exceptions import InvalidTokenError

from rest_framework import authentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import BasePermission

from .utils import create_or_update_user, decode_jwt


class AuthenticationBackend(authentication.TokenAuthentication):
    keyword = "Bearer"

    def authenticate_credentials(self, token: str):
        try:
            payload = decode_jwt(token)
        except InvalidTokenError as e:
            raise AuthenticationFailed(f"Invalid token: {str(e)}") from e

        try:
            username = payload["preferred_username"]
        except KeyError as e:
            raise AuthenticationFailed(
                "Invalid token: preferred_username not present."
            ) from e

        user = create_or_update_user(username, payload)
        return user, payload


class HasScope(BasePermission):
    """
    Permission class to check for allowed scopes in the access token.

    This permission class checks if any of the scopes defined in the `allowed_scopes`
    attribute of the view are present in the 'scope' claim of the access token.

    Example Usage in a View:

    class MyApiView(APIView):
        permission_classes = [IsAuthenticated, HasScope]
        allowed_scopes = ["jobs"]
        ...

    If no particular scope is required, you can set `allowed_scopes = "*"`
        to allow access without scope checks.
    """

    def has_permission(self, request, view):
        allowed_scopes = getattr(view, "allowed_scopes", [])

        if not allowed_scopes:
            raise Exception(
                f"No allowed_scopes defined on the view '{view.__class__.__name__}'. "
                "Define allowed_scopes or set it to '*' to allow any scope."
            )

        if allowed_scopes == "*":
            return True

        if not request.auth or "scope" not in request.auth:
            return False

        token_scopes_str = request.auth.get("scope", "")
        token_scopes = set(token_scopes_str.split())

        for scope in allowed_scopes:
            if f"{getattr(settings, 'JWT_SCOPE_PREFIX', '')}:{scope}" in token_scopes:
                return True

        return False
