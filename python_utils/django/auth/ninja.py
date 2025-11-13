from typing import Literal

from jwt import PyJWKClient, decode as jwt_decode
from jwt.exceptions import InvalidTokenError

from django.conf import settings
from django.contrib.auth import get_user_model
from ninja.security import HttpBearer
from ninja.errors import AuthenticationError, HttpError

jwks_client = PyJWKClient(getattr(settings, "JWKS_URL", ""))


class AuthBearer(HttpBearer):
    def authenticate(self, request, token):
        signing_key = jwks_client.get_signing_key_from_jwt(token)

        try:
            payload = jwt_decode(
                token,
                signing_key.key,
                algorithms=["RS256"],
                audience=getattr(settings, "JWT_AUDIENCE", None),
            )
        except InvalidTokenError as e:
            raise AuthenticationError(f"Invalid token: {str(e)}") from e

        try:
            username = payload["preferred_username"]
        except KeyError as e:
            raise AuthenticationError(
                "Invalid token: preferred_username not present."
            ) from e

        user = self._get_user(username, payload)

        self._verify_scopes(request, payload)

        return user

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
