from django import forms
from django.contrib import admin, messages
from django.core.cache import cache
from django.db.models import Count
from django.urls import path
from django.shortcuts import redirect

from ..service import KeycloakService


class UserGroupAdminMetaclass(forms.MediaDefiningClass):
    """Metaclass to dynamically construct admin attributes based on app_entities."""

    def __new__(mcs, name, bases, namespace):
        app_entities = namespace.get("app_entities", ())

        allowed_entities_attrs = tuple(f"allowed_{entity}" for entity in app_entities)
        allowed_entities_count_attrs = tuple(f"allowed_{entity}_count" for entity in app_entities)
        allow_all_entities_attrs = tuple(f"allow_all_{entity}" for entity in app_entities)

        namespace["list_display"] = (
            *namespace.get("list_display", ()),
            "path",
            *allow_all_entities_attrs,
            *allowed_entities_count_attrs,
        )

        namespace["filter_horizontal"] = allowed_entities_attrs

        namespace["fieldsets"] = (
            (
                None,
                {
                    "fields": (
                        "id",
                        "path",
                        *allow_all_entities_attrs,
                        *allowed_entities_attrs,
                    )
                },
            ),
        )

        # Dynamically create count methods for each entity
        for count_attr in allowed_entities_count_attrs:
            if count_attr not in namespace:
                namespace[count_attr] = mcs._create_count_method(count_attr)

        return super().__new__(mcs, name, bases, namespace)

    def _create_count_method(attr):
        def count_method(self, obj):
            return getattr(obj, attr)

        # Add the @admin.display decorator
        count_method = admin.display(
            description=attr.replace("_", " ").title(),
            ordering=attr,
        )(count_method)
        return count_method


class UserGroupAdminBase(admin.ModelAdmin, metaclass=UserGroupAdminMetaclass):    
    app_entities = ()  # E.g. app_entities = ('transactions',)

    search_fields = ("id", "path")
    readonly_fields = ("id", "path")
    change_list_template = "user_groups_changelist.html"

    def get_queryset(self, request):
        queryset = super().get_queryset(request)

        for entity in self.app_entities:
            count_attr = f"allowed_{entity}_count"
            queryset = queryset.annotate(**{count_attr: Count(f"allowed_{entity}")})

        return queryset

    def construct_change_message(self, request, form, formsets, add=False):
        """
        Enhance the change message to include detailed information about changes
        to allowed and allow_all entity fields.
        """
        change_message = super().construct_change_message(request, form, formsets, add)

        for entity in self.app_entities:
            # Handle changes to allow_all_entities field
            allow_all_entities_attr = f"allow_all_{entity}"
            if not add and allow_all_entities_attr in form.changed_data:
                old_value = form.initial.get(allow_all_entities_attr, False)
                new_value = form.cleaned_data.get(allow_all_entities_attr, False)

                if old_value != new_value:
                    changed_fields = change_message[0]["changed"]["fields"]
                    field = changed_fields.index(allow_all_entities_attr.replace("_", " ").capitalize())
                    changed_fields[field] += f": set to {new_value}"

            # Handle changes to allowed_entities field
            allowed_entities_attr = f"allowed_{entity}"
            if not add and allowed_entities_attr in form.changed_data:
                old_entities = {str(rec) for rec in form.initial.get(allowed_entities_attr, [])}
                new_entities_queryset = form.cleaned_data.get(allowed_entities_attr, [])
                new_entities = {str(rec) for rec in new_entities_queryset}

                added_entities = new_entities - old_entities
                removed_entities = old_entities - new_entities

                details = []
                if added_entities:
                    details.append(f"added {', '.join(added_entities)}")
                if removed_entities:
                    details.append(f"removed {', '.join(removed_entities)}")

                if details:
                    changed_fields = change_message[0]["changed"]["fields"]
                    entity_label = allowed_entities_attr.replace("_", " ").capitalize()
                    field = changed_fields.index(entity_label)
                    changed_fields[field] += ": " + "; ".join(details)

        return change_message

    def has_add_permission(self, request):
        # Manual addition of user groups is not allowed
        return False

    def has_delete_permission(self, request, obj=None):
        # Manual deletion of user groups is not allowed
        return False

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
