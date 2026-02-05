from ..tenant_context import TenantContext


def make_tenant_aware_key(key, key_prefix, version):
    return ":".join([TenantContext.get(), key_prefix, str(version), key])
