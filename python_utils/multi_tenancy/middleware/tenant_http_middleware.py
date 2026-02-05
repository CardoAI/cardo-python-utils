import logging
from typing import Callable, Optional

from django.conf import settings
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse

from ..settings import DEVELOPMENT_TENANT, TENANT_AWARE_EXCLUDED_PATHS, TENANT_DATABASES
from ..tenant_context import TenantContext

logger = logging.getLogger(__name__)


class TenantAwareHttpMiddleware:
    """
    Middleware that sets the thread local variable `tenant`.
    This middleware must be placed before any other middleware that
    executes queries on the database.
    In this way, the database alias is set before any other middleware is
    called and it is removed after all of them are called.

    Tenant detection:
    - Production (DEBUG=False): Subdomain pattern <app>.<tenant>.domain.com
    - Development (DEBUG=True): Uses DEVELOPMENT_TENANT setting directly

    The subdomain pattern expects: <app>.<tenant>.<domain>
    where <app> can be any value (e.g., app, portal, dashboard)
    and <tenant> can contain alphanumeric characters and hyphens.
    The -internal suffix is stripped from tenant names.
    """

    def __init__(self, get_response: Callable):
        """
        Middleware initialization. Only called once per Django application initialization.
        Args:
            get_response: Callable to get the response of the view.
        """
        self.get_response = get_response

    def __call__(self, request: WSGIRequest) -> HttpResponse:
        """
        Called by Django for each http request to process it and return a response.
        Everything that should be done before the view is called is done before
        the get_response method is called and everything that should be done
        after the view is called is done after the get_response method is called.
        Args:
            request: Django request object.

        Returns:    HttpResponse object.
        """
        if self._is_excluded_path(request.path):
            return self.get_response(request)

        if TenantContext.is_set():
            raise Exception("Tenant context already set")

        # In DEBUG mode, use DEVELOPMENT_TENANT directly
        # In production, extract tenant from subdomain
        if settings.DEBUG:
            tenant = DEVELOPMENT_TENANT
            logger.debug(f"Using development tenant: {tenant}")
        else:
            tenant = self._get_tenant_from_subdomain(request)
            if tenant is None:
                raise Exception(f"Could not determine tenant from subdomain. Host: {request.get_host()}")

        # Validate tenant exists in configured databases
        if not self._is_valid_tenant(tenant):
            raise Exception(f"Unknown tenant: {tenant}")

        # Call the next middleware in the chain until the response is returned.
        # After that, the database alias is removed from the thread local variable.
        with TenantContext(tenant):
            response = self.get_response(request)

        return response

    def _is_excluded_path(self, path: str) -> bool:
        """
        Check if the path should be excluded from tenant handling.
        """
        for excluded_path in TENANT_AWARE_EXCLUDED_PATHS:
            if path.startswith(excluded_path):
                return True

        return False

    def _get_tenant_from_subdomain(self, request: WSGIRequest) -> Optional[str]:
        """
        Extract tenant from subdomain.

        Expected formats:
        - <app>.tenant.domain.com -> tenant
        - <app>.tenant-internal.domain.com -> tenant (strips -internal suffix)
        """
        host = request.get_host().split(":")[0]  # Remove port if present
        parts = host.split(".")

        # Need at least 3 parts: <app>.<tenant>.<domain>
        if len(parts) >= 3:
            tenant = self._normalize_tenant(parts[1])
            logger.debug(f"Tenant '{tenant}' extracted from subdomain: {host}")
            return tenant

        return None

    @staticmethod
    def _normalize_tenant(tenant: str) -> str:
        # Remove -internal suffix if present
        if tenant.endswith("-internal"):
            return tenant[: -len("-internal")]
        return tenant

    @staticmethod
    def _is_valid_tenant(tenant: str) -> bool:
        """
        Validate that the tenant exists in configured databases.
        Skip 'default' as it's typically a placeholder.
        """
        return tenant in TENANT_DATABASES
