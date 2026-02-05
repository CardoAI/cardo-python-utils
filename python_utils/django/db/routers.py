from ..tenant_context import TenantContext


class TenantAwareRouter:
    @staticmethod
    def db_for_read(model, **hints):
        return TenantContext.get()

    @staticmethod
    def db_for_write(model, **hints):
        return TenantContext.get()
