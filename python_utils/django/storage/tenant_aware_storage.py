import json
import os
from typing import Optional

from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage

from ..tenant_context import TenantContext


def get_tenant_bucket_names() -> dict:
    """
    Retrieve the tenant bucket names from the environment variable.
    The environment variable AWS_STORAGE_TENANT_BUCKET_NAMES should be a JSON
    dictionary where each key is the tenant name and the value is the bucket name.

    Returns:
        A dictionary mapping tenant names to their S3 bucket names.
    """
    bucket_names_raw = os.getenv("AWS_STORAGE_TENANT_BUCKET_NAMES", "{}")
    try:
        return json.loads(bucket_names_raw)
    except json.JSONDecodeError:
        return {}


def get_bucket_name_for_tenant(tenant: Optional[str] = None) -> str:
    """
    Get the S3 bucket name for a specific tenant.

    Args:
        tenant: The tenant name. If None, uses the current tenant from context.

    Returns:
        The S3 bucket name for the tenant.

    Raises:
        ValueError: If no bucket is configured for the tenant.
    """
    if tenant is None:
        tenant = TenantContext.get()

    tenant_buckets = get_tenant_bucket_names()

    if tenant not in tenant_buckets:
        raise ValueError(
            f"No S3 bucket configured for tenant '{tenant}'. "
            f"Please set AWS_STORAGE_TENANT_BUCKET_NAMES environment variable."
        )

    return tenant_buckets[tenant]


class TenantAwareS3Storage(S3Boto3Storage):
    """
    A tenant-aware S3 storage backend that dynamically selects the bucket
    based on the current tenant context.
    """

    def __init__(self, *args, **kwargs):
        # Don't set bucket_name here; it will be resolved dynamically
        super().__init__(*args, **kwargs)
        self._buckets = {}

    @property
    def bucket(self):
        bucket_name = self.bucket_name  # resolves current tenant
        if bucket_name not in self._buckets:
            self._buckets[bucket_name] = self.connection.Bucket(bucket_name)
        return self._buckets[bucket_name]

    @property
    def bucket_name(self):
        """Dynamically resolve the bucket name based on current tenant."""
        try:
            return get_bucket_name_for_tenant()
        except (RuntimeError, ValueError):
            # Fallback to default bucket if tenant context is not set
            return getattr(settings, "AWS_STORAGE_BUCKET_NAME", None)

    @bucket_name.setter
    def bucket_name(self, value):
        # Allow setting bucket_name but it will be overridden by the property getter
        self._bucket_name_override = value

    def __getstate__(self):
        """Override __getstate__ to exclude the _buckets cache from being pickled."""
        state = super().__getstate__()
        state.pop("_buckets", None)
        return state

    def __setstate__(self, state):
        """Override __setstate__ to reinitialize the _buckets cache after unpickling."""
        super().__setstate__(state)
        self._buckets = {}


class TenantAwarePrivateS3Storage(TenantAwareS3Storage):
    """
    Tenant-aware private media storage with file overwrite disabled.
    """

    location = "private"
    file_overwrite = False
    custom_domain = False
