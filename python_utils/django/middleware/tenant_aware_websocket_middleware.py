import logging
from urllib.parse import parse_qs

from django.conf import settings
from django.contrib.auth import get_user_model

from ..api.utils import decode_jwt, TokenPayload
from ..settings import DEVELOPMENT_TENANT
from ..tenant_context import TenantContext

logger = logging.getLogger(__name__)


def parse_query_params_from_scope(scope):
    """
    Parse query params from scope

    Parameters:
        scope (dict): scope from consumer

    Returns:
        dict: query params
    """
    return parse_qs(scope["query_string"].decode("utf-8"))


class TenantAwareWebsocketMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        """
        Extract authentication token from request query params and authenticate user,
        used by django channels.

        Also sets the tenant context from the subdomain, mirroring
        the TenantAwareHttpMiddleware logic for HTTP requests.

        Parameters:
            scope (dict): ASGI scope
            receive (callable): ASGI receive callable
            send (callable): ASGI send callable
        """
        query_params = parse_query_params_from_scope(scope)
        access_token = query_params.get("authorization", [None])[0]
        if not access_token:
            await self._reject_connection(send, "Authorization token is missing")
            return

        tenant = self._get_tenant(scope)

        async with TenantContext(tenant):
            token_payload: TokenPayload = decode_jwt(access_token)
            username = token_payload.get("preferred_username")
            if not username:
                await self._reject_connection(send, "Username cannot be extracted from the token")
                return

            exp_timestamp = token_payload.get("exp")
            if not exp_timestamp:
                await self._reject_connection(send, "Token does not have an expiration time")
                return

            user = await get_user_model().objects.filter(username=username).afirst()
            if not user:
                await self._reject_connection(send, "User not found.")
                return

            scope["user"] = user
            scope["auth"] = token_payload
            scope["exp_timestamp"] = exp_timestamp

            return await self.app(scope, receive, send)

    @staticmethod
    async def _reject_connection(send, reason):
        """
        Reject the WebSocket connection with a specific reason.

        Parameters:
            send (callable): ASGI send callable
            reason (str): Reason for rejecting the connection

        Returns:
            None
        """
        await send(
            {"type": "websocket.close", "code": 4000, "reason": reason}
        )  # Custom close code for rejection

    def _get_tenant(self, scope) -> str:
        """
        Determine the tenant from the websocket scope.

        In DEBUG mode, uses DEVELOPMENT_TENANT directly.
        In production, extracts tenant from the Host header subdomain.
        """
        if settings.DEBUG:
            return DEVELOPMENT_TENANT

        host = self._get_host_from_scope(scope)

        if host == "testserver":
            return "default"

        parts = host.split(".")

        if len(parts) >= 3:
            tenant = parts[1].replace("-internal", "")
            logger.debug(f"Tenant '{tenant}' extracted from websocket host: {host}")
            return tenant

        raise Exception(
            f"Could not determine tenant from websocket subdomain. Host: {host}"
        )

    @staticmethod
    def _get_host_from_scope(scope) -> str:
        """Extract the host from ASGI scope headers."""
        for header_name, header_value in scope.get("headers", []):
            if header_name == b"host":
                return header_value.decode("utf-8").split(":")[0]

        # Fallback to scope["server"] if no Host header
        server = scope.get("server")
        if server:
            return server[0]

        raise Exception(f"Could not determine host from websocket scope: {scope}")
