"""
This module provides dynamic OIDC configuration based on the current tenant context.
Each tenant has its own Keycloak realm, and the OIDC endpoints are computed
dynamically based on the tenant.
"""

import json
import os
import requests

from django.conf import settings
from .tenant_context import TenantContext


KEYCLOAK_SERVER_URL_TEMPLATE = os.getenv("KEYCLOAK_SERVER_URL_TEMPLATE", "https://keycloak.{realm}.company.com")
KEYCLOAK_CONFIDENTIAL_CLIENT_ID = os.getenv("KEYCLOAK_CONFIDENTIAL_CLIENT_ID", None)

OIDC_CLIENT_AUTH_METHOD = getattr(settings, "OIDC_CLIENT_AUTH_METHOD", "client_assertion")
if OIDC_CLIENT_AUTH_METHOD not in ("client_assertion", "client_secret"):
    raise ValueError(
        f"Invalid OIDC_CLIENT_AUTH_METHOD: {OIDC_CLIENT_AUTH_METHOD}. "
        f"Supported methods are 'client_assertion' and 'client_secret'."
    )

KEYCLOAK_CONFIDENTIAL_CLIENT_SERVICE_ACCOUNT_TOKEN_FILE_PATHS: dict[str, str] = json.loads(
    os.getenv("KEYCLOAK_CONFIDENTIAL_CLIENT_SERVICE_ACCOUNT_TOKEN_FILE_PATHS", "{}")
)
KEYCLOAK_CLIENT_CREDENTIALS_GRANT_TYPE = "client_credentials"
KEYCLOAK_CLIENT_ASSERTION_TYPE = "urn:ietf:params:oauth:client-assertion-type:jwt-bearer"

KEYCLOAK_CONFIDENTIAL_CLIENT_SECRETS: dict[str, str] = json.loads(
    os.getenv("KEYCLOAK_CONFIDENTIAL_CLIENT_SECRETS", "{}")
)

TENANT_REALM_MAPPING: dict[str, str] = getattr(
    settings, "TENANT_REALM_MAPPING", json.loads(os.getenv("TENANT_REALM_MAPPING", "{}"))
)


def get_realm_for_tenant(tenant: str) -> str:
    """
    Get the Keycloak realm name for a given tenant.
    By default, we assume the realm name is the same as the tenant name.
    """
    return TENANT_REALM_MAPPING.get(tenant, tenant)


def get_keycloak_server_url() -> str:
    """Get the Keycloak server URL for the current tenant."""

    return KEYCLOAK_SERVER_URL_TEMPLATE.format(realm=get_realm_for_tenant(TenantContext.get()))


def get_oidc_op_base_url() -> str:
    """Get the base URL for the OIDC provider (Keycloak realm URL)."""

    realm = get_realm_for_tenant(TenantContext.get())
    return f"{get_keycloak_server_url()}/realms/{realm}"


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
    realm = get_realm_for_tenant(TenantContext.get())
    token_file_path = KEYCLOAK_CONFIDENTIAL_CLIENT_SERVICE_ACCOUNT_TOKEN_FILE_PATHS.get(realm)
    if not token_file_path or not os.path.isfile(token_file_path):
        raise FileNotFoundError(f"Keycloak service account token file for tenant {realm} not found: {token_file_path}")

    with open(token_file_path, "r") as f:
        token = f.read().strip()

    if not token:
        raise ValueError(f"Keycloak service account token for tenant {realm} is empty.")

    return token


def get_confidential_client_secret() -> str:
    """
    Retrieves the Keycloak confidential client secret for the current tenant.
    """
    realm = get_realm_for_tenant(TenantContext.get())
    client_secret = KEYCLOAK_CONFIDENTIAL_CLIENT_SECRETS.get(realm)
    if not client_secret:
        raise ValueError(f"Keycloak confidential client secret for tenant {realm} not found.")

    return client_secret


def get_oidc_confidential_client_token(**kwargs) -> dict:
    """
    Obtains token for an OIDC confidential client with the client credentials grant,
    using a service account token for authentication.
    """

    data = {
        "grant_type": KEYCLOAK_CLIENT_CREDENTIALS_GRANT_TYPE,
        **kwargs,
    }
    if OIDC_CLIENT_AUTH_METHOD == "client_secret":
        data["client_id"] = KEYCLOAK_CONFIDENTIAL_CLIENT_ID
        data["client_secret"] = get_confidential_client_secret()
    else:
        data["client_assertion_type"] = KEYCLOAK_CLIENT_ASSERTION_TYPE
        data["client_assertion"] = get_confidential_client_service_account_token()

    response = requests.post(
        get_oidc_op_token_endpoint(),
        data=data,
    )
    response.raise_for_status()

    return response.json()
