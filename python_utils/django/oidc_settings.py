"""
This module provides dynamic OIDC configuration based on the current tenant context.
Each tenant has its own Keycloak realm, and the OIDC endpoints are computed
dynamically based on the tenant.
"""

import json
import os
import requests

from .tenant_context import TenantContext


KEYCLOAK_SERVER_URL = os.getenv("KEYCLOAK_SERVER_URL", None)
KEYCLOAK_CONFIDENTIAL_CLIENT_ID = os.getenv("KEYCLOAK_CONFIDENTIAL_CLIENT_ID", None)
KEYCLOAK_CONFIDENTIAL_CLIENT_SERVICE_ACCOUNT_TOKEN_FILE_PATHS: dict[str, str] = json.loads(
    os.getenv("KEYCLOAK_CONFIDENTIAL_CLIENT_SERVICE_ACCOUNT_TOKEN_FILE_PATHS", "{}")
)
KEYCLOAK_CLIENT_CREDENTIALS_GRANT_TYPE = "client_credentials"
KEYCLOAK_CLIENT_ASSERTION_TYPE = "urn:ietf:params:oauth:client-assertion-type:jwt-bearer"


def get_oidc_op_base_url() -> str:
    """Get the base URL for the OIDC provider (Keycloak realm URL)."""

    realm = TenantContext.get()
    return f"{KEYCLOAK_SERVER_URL}/realms/{realm}"


def get_oidc_op_authorization_endpoint() -> str:
    return f"{get_oidc_op_base_url()}/protocol/openid-connect/auth"


def get_oidc_op_token_endpoint() -> str:
    return f"{get_oidc_op_base_url()}/protocol/openid-connect/token"


def get_oidc_op_user_endpoint() -> str:
    return f"{get_oidc_op_base_url()}/protocol/openid-connect/userinfo"


def get_oidc_op_jwks_endpoint() -> str:
    return f"{get_oidc_op_base_url()}/protocol/openid-connect/certs"


def get_oidc_op_logout_endpoint() -> str:
    return f"{get_oidc_op_base_url()}/protocol/openid-connect/logout"


def get_confidential_client_service_account_token() -> str:
    """
    Reads the Keycloak confidential client service account token for the current tenant from a file.
    """
    tenant = TenantContext.get()
    token_file_path = KEYCLOAK_CONFIDENTIAL_CLIENT_SERVICE_ACCOUNT_TOKEN_FILE_PATHS.get(tenant)
    if not token_file_path or not os.path.isfile(token_file_path):
        raise FileNotFoundError(f"Keycloak service account token file for tenant {tenant} not found: {token_file_path}")

    with open(token_file_path, "r") as f:
        token = f.read().strip()

    if not token:
        raise ValueError(f"Keycloak service account token for tenant {tenant} is empty.")

    return token


def get_oidc_confidential_client_token(**kwargs) -> dict:
    """
    Obtains token for an OIDC confidential client with the client credentials grant,
    using a service account token for authentication.
    """

    response = requests.post(
        get_oidc_op_token_endpoint(),
        data={
            "grant_type": KEYCLOAK_CLIENT_CREDENTIALS_GRANT_TYPE,
            "client_assertion_type": KEYCLOAK_CLIENT_ASSERTION_TYPE,
            "client_assertion": get_confidential_client_service_account_token(),
            **kwargs,
        },
    )
    response.raise_for_status()

    return response.json()
