from django.conf import settings
from mozilla_django_oidc.auth import OIDCAuthenticationBackend


class AdminAuthenticationBackend(OIDCAuthenticationBackend):
    def _get_user_data(self, claims) -> dict:
        client_roles = (
            claims.get("resource_access", {})
            .get(getattr(settings, "OIDC_RP_CLIENT_ID", ""), {})
            .get("roles", [])
        )
        is_superuser = "Admin" in client_roles

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
