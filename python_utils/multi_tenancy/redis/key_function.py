from ..tenant_context import TenantContext


def make_key(key, key_prefix, version):
    return ":".join([TenantContext.get(), key_prefix, str(version), key])
