"""
Tenant-aware OIDC views for mozilla-django-oidc.

These views override the default mozilla-django-oidc views to dynamically
resolve OIDC endpoints based on the current tenant context.
"""

from mozilla_django_oidc.views import (
    OIDCAuthenticationCallbackView,
    OIDCAuthenticationRequestView,
    OIDCLogoutView,
)

from ..oidc_settings import (
    get_oidc_op_authorization_endpoint,
    get_oidc_op_logout_endpoint,
)


class TenantAwareOIDCAuthenticationRequestView(OIDCAuthenticationRequestView):
    """
    Tenant-aware OIDC authentication request view.

    Dynamically resolves the authorization endpoint based on the current tenant.
    """

    @property
    def OIDC_OP_AUTH_ENDPOINT(self):
        """Dynamically get the authorization endpoint for the current tenant."""
        return get_oidc_op_authorization_endpoint()

    def get_settings(self, attr, *args):
        if attr == "OIDC_OP_AUTHORIZATION_ENDPOINT":
            return self.OIDC_OP_AUTH_ENDPOINT
        return super().get_settings(attr, *args)


class TenantAwareOIDCAuthenticationCallbackView(OIDCAuthenticationCallbackView):
    """
    Tenant-aware OIDC authentication callback view.

    Uses the tenant-aware authentication backend.
    """

    pass


class TenantAwareOIDCLogoutView(OIDCLogoutView):
    """
    Tenant-aware OIDC logout view.

    Dynamically resolves the logout endpoint based on the current tenant.
    """

    @property
    def OIDC_OP_LOGOUT_ENDPOINT(self):
        """Dynamically get the logout endpoint for the current tenant."""
        return get_oidc_op_logout_endpoint()

    def get_settings(self, attr, *args):
        if attr == "OIDC_OP_LOGOUT_ENDPOINT":
            return self.OIDC_OP_LOGOUT_ENDPOINT
        return super().get_settings(attr, *args)
