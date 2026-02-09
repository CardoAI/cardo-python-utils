import logging
import sys
from contextlib import ContextDecorator
from contextvars import ContextVar
from typing import Optional

from .settings import DATABASES

logger = logging.getLogger(__name__)

# ContextVar propagates automatically to async threads via sync_to_async
_tenant_var: ContextVar[Optional[str]] = ContextVar('tenant', default=None)


class TenantContext(ContextDecorator):
    """
    Context manager that sets the current tenant.
    This class can be used in several ways:
    1. As a context manager (sync and async):
        with TenantContext('tenant'):
            # do something
        
        async with TenantContext('tenant'):
            # do something async

    2. As a decorator:
        @TenantContext('tenant')
        def some_function():
            # do something

    3. Directly using static methods:
        TenantContext.set('tenant')
        # do something
        TenantContext.clear()
    """

    field_name = "tenant"

    def __init__(self, tenant: str):
        self.tenant = tenant
        self._token = None

    def __enter__(self):
        self._token = TenantContext.set(self.tenant)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        TenantContext.clear(self._token)

    async def __aenter__(self):
        self._token = TenantContext.set(self.tenant)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        TenantContext.clear(self._token)

    @staticmethod
    def is_set() -> bool:
        return _tenant_var.get() is not None

    @staticmethod
    def get() -> Optional[str]:
        tenant = _tenant_var.get()
        if tenant is None:
            raise RuntimeError("Tenant context is not set.")
        return tenant

    @staticmethod
    def set(tenant):
        if TenantContext.is_set():
            # If the tenant is already set, we do not allow to set it
            # again unless it is the same value.
            # This is to prevent the tenant to be set to a different
            # value in the same thread.
            # A request-response cycle is required to set the tenant
            # only once and operate on the same tenant in its lifecycle.
            # The same applies to a single task, it is not allowed to set the
            # tenant in the same task to a different value.
            if TenantContext.get() != tenant:
                logger.error("ERROR: TENANT CONTEXT ALREADY SET")
                logger.error(f"Current tenant: {TenantContext.get()}, new tenant: {tenant}")
                return sys.exit(1)
            else:
                # If the tenant is already set to the same value, we do nothing and return None.
                return None

        if tenant not in DATABASES:
            logger.error(f"Tenant '{tenant}' not found in DATABASES settings.")
            return sys.exit(1)

        token = _tenant_var.set(tenant)
        logger.info(f"Tenant context set to {tenant}")
        return token

    @staticmethod
    def clear(token=None):
        if TenantContext.is_set():
            if token is not None:
                _tenant_var.reset(token)
            else:
                _tenant_var.set(None)
            logger.info("Tenant context cleared")