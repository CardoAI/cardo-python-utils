import logging
import sys
from contextlib import ContextDecorator
from threading import local
from typing import Optional

from .settings import DATABASES

logger = logging.getLogger(__name__)
thread_namespace = local()


class TenantContext(ContextDecorator):
    """
    Context manager that sets the current tenant.
    This class can be used in several ways:
    1. As a context manager:
        with TenantContext('tenant'):
            # do something

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

    def __enter__(self):
        TenantContext.set(self.tenant)

    def __exit__(self, exc_type, exc_val, exc_tb):
        TenantContext.clear()

    @staticmethod
    def is_set() -> bool:
        return hasattr(thread_namespace, TenantContext.field_name)

    @staticmethod
    def get() -> Optional[str]:
        try:
            return getattr(thread_namespace, TenantContext.field_name)
        except AttributeError as e:
            raise RuntimeError("Tenant context is not set.") from e

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
                # Normally in a request-response cycle, or a single task, the
                # tenant context is set only once. But there is an exception
                # for the migrate command, which sets the tenant context
                # multiple times to the same value.
                logger.info("Tenant context already set to %s", tenant)
                return
        
        if tenant not in DATABASES:
            logger.error(f"Tenant '{tenant}' not found in DATABASES settings.")
            return sys.exit(1)

        setattr(thread_namespace, TenantContext.field_name, tenant)
        logger.info(f"Tenant context set to {tenant}")

    @staticmethod
    def clear():
        if TenantContext.is_set():
            delattr(thread_namespace, TenantContext.field_name)
            logger.info("Tenant context cleared")
