"""
Tenant-aware OIDC views for mozilla-django-oidc.

These views override the default mozilla-django-oidc views to dynamically
resolve OIDC endpoints based on the current tenant context.
"""

from mozilla_django_oidc.views import OIDCAuthenticationRequestView

from ..oidc_settings import get_oidc_op_authorization_endpoint


class TenantAwareOIDCAuthenticationRequestView(OIDCAuthenticationRequestView):
    """
    Tenant-aware OIDC authentication request view.

    Dynamically resolves the authorization endpoint based on the current tenant.
    """

    def get_settings(self, attr, *args):
        if attr == "OIDC_OP_AUTHORIZATION_ENDPOINT":
            return get_oidc_op_authorization_endpoint()

        return super().get_settings(attr, *args)
