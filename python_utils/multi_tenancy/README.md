This package adds multi-tenancy support to a Django application, with a separate database for each tenant.
Several components are provided to facilitate this, including: database routing, middleware, celery tasks etc.

It is heavily inspired by the implementation of multi-tenancy in the Mercury app by Klement Omeri.

# Usage

To use this package, add the following to your Django settings.py file:

```python3
INSTALLED_APPS = [
    ...
    "python_utils.multi_tenancy",
    ...
]

MIDDLEWARE = [
    "python_utils.multi_tenancy.middleware.TenantAwareHttpMiddleware",
    ...
]

# Include the database configuration for each tenant in the DATABASES setting.
# You can use the get_database_configs() function from python_utils.multi_tenancy.db.utils as a helper.
DATABASES = {
    'tenant1': { ... },
    'tenant2': { ... },
    ...
}

# If you want to override the database alias to use for local development (when DEBUG is True).
# By default, the first database defined in DATABASES is used.
DEVELOPMENT_TENANT = "development"

# This is required to use the tenant context when routing database queries
DATABASE_ROUTERS = [
    "python_utils.multi_tenancy.db.routers.TenantAwareRouter"
]

# If using celery, set the task class to TenantAwareTask:
CELERY_TASK_CLS = "python_utils.multi_tenancy.celery.TenantAwareTask"

# If using Redis caching, configure the cache backend as follows:
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": REDIS_LOCATION,
        "KEY_FUNCTION": "python_utils.multi_tenancy.redis.make_key",
        **OPTIONS,
    }
}

# If using Django Storages with S3, configure the storage backends as follows:
STORAGES = {
    "default": {
        "BACKEND": "python_utils.multi_tenancy.storage.TenantAwarePrivateS3Storage",
    },
}

# If you want to exclude certain paths from tenant processing, use TENANT_AWARE_EXCLUDED_PATHS:
# They are considered as prefixes, so all paths starting with the given strings will be excluded.
TENANT_AWARE_EXCLUDED_PATHS = ("/some/path",)
```