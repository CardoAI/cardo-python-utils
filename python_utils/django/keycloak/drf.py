import jwt

from django.conf import settings
from django.contrib.auth import get_user_model
from jwt import PyJWKClient
from jwt.exceptions import InvalidTokenError

from rest_framework import authentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import BasePermission


jwks_client = PyJWKClient(getattr(settings, "JWKS_URL", ""))


class AuthenticationBackend(authentication.TokenAuthentication):
    keyword = "Bearer"

    def authenticate_credentials(self, token: str):
        signing_key = jwks_client.get_signing_key_from_jwt(token)

        try:
            payload = jwt.decode(
                token,
                signing_key.key,
                algorithms=["RS256"],
                audience=getattr(settings, "JWT_AUDIENCE", None),
            )
        except InvalidTokenError as e:
            raise AuthenticationFailed(f"Invalid token: {str(e)}") from e

        try:
            username = payload["preferred_username"]
        except KeyError as e:
            raise AuthenticationFailed(
                "Invalid token: preferred_username not present."
            ) from e

        user = self._get_user(username, payload)
        return user, payload

    def _get_user(self, username: str, payload: dict):
        """
        Get or create a user based on the JWT payload.
        If the user exists, update their details.
        """
        user_model = get_user_model()
        user_data = {
            "first_name": payload.get("given_name") or "",
            "last_name": payload.get("family_name") or "",
            "email": payload.get("email") or "",
            "is_staff": payload.get("is_staff", False),
        }
        if hasattr(user_model, "is_demo"):
            user_data["is_demo"] = payload.get("is_demo", False)

        user = user_model.objects.filter(username=username).first()
        if user:
            update_needed = False

            for field, value in user_data.items():
                if getattr(user, field) != value:
                    setattr(user, field, value)
                    update_needed = True

            if update_needed:
                user.save(update_fields=list(user_data.keys()))

            return user
        else:
            return user_model.objects.create(
                username=username,
                **user_data,
            )


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
