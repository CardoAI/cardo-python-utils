import base64
from collections.abc import Callable
import jwt
import time

from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend
from django.conf import settings
from unittest.mock import patch

import pytest

from ..models.user_group import UserGroupBase


class MockKeycloakIdP:
    def __init__(self, audience="test-audience"):
        self.private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048, backend=default_backend())
        self.public_key = self.private_key.public_key()
        self.kid = "test-key-id"
        self.audience = audience

    def get_jwks(self):
        """Return the JWKS JSON payload"""
        public_numbers = self.public_key.public_numbers()

        def to_b64(val):
            bytes_data = val.to_bytes((val.bit_length() + 7) // 8, "big")
            return base64.urlsafe_b64encode(bytes_data).decode("utf-8").rstrip("=")

        return {
            "keys": [
                {
                    "kid": self.kid,
                    "kty": "RSA",
                    "alg": "RS256",
                    "use": "sig",
                    "n": to_b64(public_numbers.n),
                    "e": to_b64(public_numbers.e),
                }
            ]
        }

    def generate_token(self, **claims):
        """Generate a valid signed token"""
        now = time.time()
        payload = {
            "iss": "http://test-keycloak/auth/realms/test",
            "aud": self.audience,
            "exp": now + 300,
            "iat": now,
            "sub": "default-test-user-id",
            **claims,
        }
        return jwt.encode(payload, self.private_key, algorithm="RS256", headers={"kid": self.kid})


@pytest.fixture(scope="session")
def keycloak_idp() -> MockKeycloakIdP:
    """
    Initializes the Mock IdP once for the entire test session,
    as generating RSA keys is slow.
    """
    return MockKeycloakIdP(audience=getattr(settings, "JWT_AUDIENCE", "test-audience"))


@pytest.fixture(autouse=True)
def mock_pyjwk_client(keycloak_idp):
    """
    Patches PyJWKClient to return our mock keys instead of hitting the network.
    """
    with patch("jwt.jwks_client.PyJWKClient.fetch_data") as mock_fetch:
        mock_fetch.return_value = keycloak_idp.get_jwks()
        yield mock_fetch


@pytest.fixture
def mock_verify_scopes_ninja():
    """
    Patches AuthBearer._verify_scopes, so that no real scope checking is done during tests.
    This is done because scope checking uses route resolution, which the test client does not support.
    """
    with patch("python_utils.keycloak.django.api.ninja.AuthBearer._verify_scopes") as mock_verify:
        mock_verify.return_value = None
        yield mock_verify


@pytest.fixture
def make_user_group() -> Callable[..., UserGroupBase]:
    from model_bakery import baker

    def _prepare_user_group(**overrides) -> UserGroupBase:
        user_group = baker.make("UserGroup", **overrides)

        if not user_group.path.startswith("/"):
            user_group.path = f"/{user_group.path}"
            user_group.save()

        return user_group

    return _prepare_user_group
