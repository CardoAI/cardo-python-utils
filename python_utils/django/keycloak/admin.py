from django.conf import settings
from django.contrib import admin, messages
from django.core.cache import cache
from django.urls import path
from django.shortcuts import redirect
from mozilla_django_oidc.auth import OIDCAuthenticationBackend

from .service import KeycloakService


class KeycloakAuthenticationBackend(OIDCAuthenticationBackend):
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


class UserGroupAdminBase(admin.ModelAdmin):
    list_display = ("path",)
    search_fields = ("id", "path")
    readonly_fields = ("id", "path")

    # To show ManyToMany fields with a horizontal filter widget
    # filter_horizontal = ("allowed_entities",)

    change_list_template = "user_groups_changelist.html"

    # To show fields in this order in the detail view
    # fieldsets = (
    #     (
    #         None,
    #         {
    #             "fields": (
    #                 "id",
    #                 "path",
    #                 "allow_all_entities",
    #                 "allowed_entities",
    #             )
    #         },
    #     ),
    # )

    def has_add_permission(self, request):
        # Manual addition of user groups is not allowed
        return False

    def has_delete_permission(self, request, obj=None):
        # Manual deletion of user groups is not allowed
        return False

    # To show annotated fields in the list view
    # def get_queryset(self, request):
    #     return (
    #         super()
    #         .get_queryset(request)
    #         .annotate(allowed_job_configs_count=Count("allowed_job_configs"))
    #     )

    def get_urls(self):
        return [
            path("sync-with-keycloak/", self.sync_groups_with_keycloak),
            *super().get_urls(),
        ]

    @staticmethod
    def sync_groups_with_keycloak(request):  # noqa
        """Syncs user groups with Keycloak"""

        try:
            KeycloakService().sync_user_groups(raise_exceptions=True)
            messages.success(request, "User groups synced successfully.")
        except Exception as e:
            messages.error(request, f"Error syncing user groups: {e}")

        return redirect("..")

    # To allow sorting by annotated fields
    # @admin.display(
    #     description="Allowed Job Configs", ordering="allowed_job_configs_count"
    # )
    # def allowed_job_configs_count(self, obj):
    #     return obj.allowed_job_configs_count

    def changelist_view(self, request, extra_context=None):
        """
        When the list view is accessed, sync the user groups from Keycloak.
        Cache the sync for 10 minutes to avoid excessive requests.
        """
        cache_key = "keycloak_group_sync_lock"

        if cache.get(cache_key) is None:
            KeycloakService().sync_user_groups()
            cache.set(cache_key, "true", 60 * 10)

        return super().changelist_view(request, extra_context)
