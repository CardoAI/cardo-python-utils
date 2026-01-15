import os
import requests

KEYCLOAK_SERVER_URL = os.getenv("KEYCLOAK_SERVER_URL")
KEYCLOAK_REALM = os.getenv("KEYCLOAK_REALM")
KEYCLOAK_REALM_URL = f"{KEYCLOAK_SERVER_URL}/realms/{KEYCLOAK_REALM}"
KEYCLOAK_TOKEN_ENDPOINT = f"{KEYCLOAK_REALM_URL}/protocol/openid-connect/token"

KEYCLOAK_CONFIDENTIAL_CLIENT_ID = os.getenv("KEYCLOAK_CONFIDENTIAL_CLIENT_ID")
KEYCLOAK_CONFIDENTIAL_CLIENT_SERVICE_ACCOUNT_TOKEN_FILE_PATH = os.getenv(
    "KEYCLOAK_CONFIDENTIAL_CLIENT_SERVICE_ACCOUNT_TOKEN_FILE_PATH"
)
KEYCLOAK_CLIENT_CREDENTIALS_GRANT_TYPE = "client_credentials"
KEYCLOAK_CLIENT_ASSERTION_TYPE = "urn:ietf:params:oauth:client-assertion-type:jwt-bearer"


def get_confidential_client_service_account_token() -> str:
    """
    Reads the Keycloak confidential client service account token from a file.
    """
    token_file_path = KEYCLOAK_CONFIDENTIAL_CLIENT_SERVICE_ACCOUNT_TOKEN_FILE_PATH
    if not token_file_path or not os.path.isfile(token_file_path):
        raise FileNotFoundError(f"Keycloak service account token file not found: {token_file_path}")

    with open(token_file_path, "r") as f:
        token = f.read().strip()

    if not token:
        raise ValueError("Keycloak service account token is empty.")

    return token


def get_keycloak_confidential_client_token(**kwargs) -> dict:
    """
    Obtains token for a Keycloak confidential client with the client credentials grant,
    using a service account token for authentication.
    """

    response = requests.post(
        KEYCLOAK_TOKEN_ENDPOINT,
        data={
            "grant_type": KEYCLOAK_CLIENT_CREDENTIALS_GRANT_TYPE,
            "client_assertion_type": KEYCLOAK_CLIENT_ASSERTION_TYPE,
            "client_assertion": get_confidential_client_service_account_token(),
            **kwargs,
        },
    )
    response.raise_for_status()

    return response.json()
