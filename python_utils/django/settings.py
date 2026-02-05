from django.conf import settings

TENANT_KEY = "tenant"
TENANT_DATABASES = set(settings.DATABASES.keys()) - {"default"}

TENANT_AWARE_EXCLUDED_PATHS = getattr(settings, "TENANT_AWARE_EXCLUDED_PATHS", ())
TENANT_AWARE_EXCLUDED_PATHS = (
    *TENANT_AWARE_EXCLUDED_PATHS,
    "/health",
    "/healthz",
    "/static",
    "/staticfiles",
    "/media",
    "/mediafiles",
)

DEVELOPMENT_TENANT = getattr(settings, "DEVELOPMENT_TENANT", list(TENANT_DATABASES)[0])
