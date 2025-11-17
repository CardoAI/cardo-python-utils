from django.contrib import admin, messages
from django.core.cache import cache
from django.urls import path
from django.shortcuts import redirect

from ..service import KeycloakService


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
