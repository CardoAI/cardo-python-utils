from django.conf import settings
from mozilla_django_oidc.auth import OIDCAuthenticationBackend

from ..oidc_settings import (
    get_oidc_confidential_client_token,
    get_oidc_op_token_endpoint,
    get_oidc_op_user_endpoint,
    get_oidc_op_jwks_endpoint,
)


class AdminAuthenticationBackend(OIDCAuthenticationBackend):
    """
    Tenant-aware OIDC authentication backend for Django admin.

    This backend dynamically resolves OIDC endpoints based on the current
    tenant context, allowing each tenant to authenticate against their
    own Keycloak realm.
    """

    @property
    def OIDC_OP_TOKEN_ENDPOINT(self):
        """Dynamically get the token endpoint for the current tenant."""

        return get_oidc_op_token_endpoint()

    @property
    def OIDC_OP_USER_ENDPOINT(self):
        """Dynamically get the userinfo endpoint for the current tenant."""

        return get_oidc_op_user_endpoint()

    @property
    def OIDC_OP_JWKS_ENDPOINT(self):
        """Dynamically get the JWKS endpoint for the current tenant."""

        return get_oidc_op_jwks_endpoint()

    def get_token(self, payload):
        # Instead of passing client_id and client_secret,
        # client_assertion with service account token will be used
        payload.pop("client_id", None)
        payload.pop("client_secret", None)

        return get_oidc_confidential_client_token(**payload)

    def _get_user_data(self, claims) -> dict:
        client_roles = (
            claims.get("resource_access", {}).get(getattr(settings, "OIDC_RP_CLIENT_ID", ""), {}).get("roles", [])
        )
        is_superuser = "AdminPanel" in client_roles

        return {
            "username": claims.get("preferred_username"),
            "email": claims.get("email"),
            "first_name": claims.get("given_name", ""),
            "last_name": claims.get("family_name", ""),
            "is_staff": claims.get("is_staff", False),
            "is_superuser": is_superuser,
        }

    def filter_users_by_claims(self, claims):
        username = claims.get("preferred_username")
        if not username:
            return self.UserModel.objects.none()
        return self.UserModel.objects.filter(username=username)

    def create_user(self, claims):
        return self.UserModel.objects.create_user(**self._get_user_data(claims))

    def update_user(self, user, claims):
        save_needed = False

        for attr, value in self._get_user_data(claims).items():
            if getattr(user, attr) != value:
                setattr(user, attr, value)
                save_needed = True

        if save_needed:
            user.save()

        return user


def has_admin_site_permission(request):
    """Admin site is not publicly accessible."""
    return request.user.is_active
