This package provides utilities for facilitating IDP communication and multi-tenancy support.

# Usage

## Environment variables to set

- AWS_STORAGE_TENANT_BUCKET_NAMES
  - _This variable should be set if separate tenant buckets are needed._
  - A JSON dictionary where each key is the tenant name and the value is the bucket name.
- DATABASE_CONFIG
  - A JSON dictionary where each key is the tenant name and the value is a dict with the datase config.
  - If multiple 'DATABASE_CONFIG'-prefixed variables are set, they will be merged into a single dictionary.
- KEYCLOAK_CONFIDENTIAL_CLIENT_ID
  - The id of the confidential client of the backend service
- KEYCLOAK_CONFIDENTIAL_CLIENT_SERVICE_ACCOUNT_TOKEN_FILE_PATHS
  - A JSON dictionary where each key is the tenant name and the value is the file path of the service account token for the confidential client of that tenant

## settings.py file

### For multi-tenancy

```python3
INSTALLED_APPS = [
    ...
    "python_utils.django",
    ...
]

MIDDLEWARE = [
    "python_utils.django.middleware.TenantAwareHttpMiddleware",
    ...
]

AUTH_USER_MODEL = "idp_user.User"

# Include the database configuration for each tenant in the DATABASES setting.
# You can use the get_database_configs() function from python_utils.django.db.utils as a helper.
from python_utils.django.db.utils import get_database_configs

for tenant, tenant_db_config in get_database_configs().items():
    DATABASES[tenant] = {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": tenant_db_config["name"],
        "USER": tenant_db_config["user"],
        "PASSWORD": tenant_db_config["password"],
        "HOST": tenant_db_config["host"],
        "PORT": tenant_db_config.get("port", 5432),
    }

# If you want to override the database alias to use for local development (when DEBUG is True).
# By default, the first database defined in DATABASES is used.
DEVELOPMENT_TENANT = "development"

# This is required to use the tenant context when routing database queries
DATABASE_ROUTERS = ["python_utils.django.db.routers.TenantAwareRouter"]

# If using celery, set the task class to TenantAwareTask:
CELERY_TASK_CLS = "python_utils.django.celery.TenantAwareTask"

# If using Redis caching, configure the cache backend as follows:
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": REDIS_LOCATION,
        "KEY_FUNCTION": "python_utils.django.redis.make_tenant_aware_key",
        **OPTIONS,
    }
}

# If using Django Storages with S3, and separate tenant buckets are needed, 
# configure the storage backends as follows:
STORAGES = {
    "default": {
        "BACKEND": "python_utils.django.storage.TenantAwarePrivateS3Storage",
    },
}

# If you want to exclude certain paths from tenant processing, use TENANT_AWARE_EXCLUDED_PATHS:
# They are considered as prefixes, so all paths starting with the given strings will be excluded.
TENANT_AWARE_EXCLUDED_PATHS = ("/some/path",)
```

### For OIDC auth

```python3
from python_utils.django.admin.templates import TEMPLATE_PATH

INSTALLED_APPS.append("mozilla_django_oidc")
TEMPLATES[0]["DIRS"].append(TEMPLATE_PATH)

JWT_AUDIENCE = "myapp"
JWT_SCOPE_PREFIX = "myapp"

# If using DRF
REST_FRAMEWORK.update(
    {
        "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
        "DEFAULT_AUTHENTICATION_CLASSES": ("python_utils.django.api.drf.AuthenticationBackend",),
        "DEFAULT_PERMISSION_CLASSES": (
            "rest_framework.permissions.IsAuthenticated",
            "python_utils.django.api.drf.HasScope",
        ),
    }
)

# Admin auth backends
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "python_utils.django.admin.auth.AdminAuthenticationBackend",
]

# If user groups are used for Row Level Security (RLS)
KEYCLOAK_USER_GROUP_MODEL = "myapp.UserGroup"

KEYCLOAK_CONFIDENTIAL_CLIENT_ID = os.getenv("KEYCLOAK_CONFIDENTIAL_CLIENT_ID", f"{JWT_AUDIENCE}_confidential")

OIDC_RP_CLIENT_ID = KEYCLOAK_CONFIDENTIAL_CLIENT_ID
OIDC_RP_SIGN_ALGO = "RS256"
OIDC_CREATE_USER = True
OIDC_AUTHENTICATE_CLASS = "python_utils.django.admin.views.TenantAwareOIDCAuthenticationRequestView"

LOGIN_REDIRECT_URL = "/admin"
SESSION_COOKIE_AGE = 60 * 30  # 30 minutes
SESSION_SAVE_EVERY_REQUEST = True  # Extend session on each request

# If using django-easy-audit

from python_utils.django.db.alias import DynamicDatabaseAlias
DJANGO_EASY_AUDIT_DATABASE_ALIAS = DynamicDatabaseAlias()
```

## urls.py file

The views of the `mozilla-django-oidc` package need to be exposed as well, for the OIDC auth:

```python3
urlpatterns.append(path("oidc/", include("mozilla_django_oidc.urls")))
```

## admin.py file

The Django Admin Panel needs to be configured to automatically redirect to the OIDC login page:

```python3
from python_utils.django.admin.auth import has_admin_site_permission
from python_utils.django.admin.views import TenantAwareOIDCAuthenticationRequestView

admin.site.login = TenantAwareOIDCAuthenticationRequestView.as_view()
admin.site.has_permission = has_admin_site_permission
```

## With django-ninja

If using `django-ninja`, apart from the settings configured above, auth utils are provided in the django/api/ninja.py module.

## Atomic Transactions

Django's `transaction.atomic` uses the default database. To make it tenant-aware, use `tenant_atomic`.
If `transaction.on_commit` is used, make sure to pass the tenant as DB alias as well:

```python3
from python_utils.django.db.transaction import tenant_atomic

@tenant_atomic
def my_function():
    # Some logic

    transaction.on_commit(do_smth, using=TenantContext.get())
```

## Explicit database connection

If using django.db.connection anywhere in the code, you need to change that to get a tenant-aware connection:

```python3
from python_utils.django.db.utils import get_connection
from python_utils.django.tenant_context import TenantContext

connection = get_connection(TenantContext.get())
```

## Django Shell

This library overrides the shell command of Django, so that it requires the `tenant` arg. 
This way, the shell is automatically initialized with the context set to the tenant. 

```bash
./manage.py shell --tenant=tenant1

Starting shell for tenant: -tenant=tenant
>>>
```

## Testing

In order for tests to work, create the following autouse fixtures:

```python3
import pytest

from python_utils.django.tenant_context import TenantContext

# Add this, if the test utils of the package are needed
pytest_plugins = ["python_utils.django.tests"]


@pytest.fixture(scope="session", autouse=True)
def test_database() -> str:
    return "default"


@pytest.fixture(scope="session", autouse=True)
def set_tenant_context_session(test_database):
    """Set tenant context for the entire test session."""
    TenantContext.set(test_database)
    yield
    TenantContext.clear()


@pytest.fixture(autouse=True)
def set_tenant_context(set_tenant_context_session, test_database):
    """Ensure tenant context is set for each test (depends on session fixture)."""
    # Re-set in case it was cleared between tests
    if not TenantContext.is_set():
        TenantContext.set(test_database)
    yield
```