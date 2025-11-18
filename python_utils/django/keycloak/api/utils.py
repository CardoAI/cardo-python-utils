from typing import TypedDict

from django.conf import settings
from django.contrib.auth import get_user_model
from jwt import decode, PyJWKClient

jwks_client = PyJWKClient(getattr(settings, "JWKS_URL", ""))


class TokenPayload(TypedDict, total=False):
    exp: int
    iat: int
    jti: str
    iss: str
    aud: str | list[str]
    typ: str
    azp: str
    sid: str
    scope: str
    preferred_username: str
    given_name: str
    family_name: str
    email: str
    is_staff: bool
    is_demo: bool
    groups: list[str]  # Full path of the user group, e.g. "/group1/subgroup1"


def decode_jwt(token: str) -> TokenPayload:
    """
    Decode a JWT token using the public certificate of the Auth Server.

    Raises:
        jwt.exceptions.InvalidTokenError: If the token is invalid or cannot be decoded.
    """
    signing_key = jwks_client.get_signing_key_from_jwt(token)

    return decode(
        token,
        signing_key.key,
        algorithms=["RS256"],
        audience=getattr(settings, "JWT_AUDIENCE", None),
    )


def create_or_update_user(username: str, payload: TokenPayload):
    """
    Create or update a user based on the JWT payload.
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
