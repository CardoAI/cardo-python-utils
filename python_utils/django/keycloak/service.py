from django.apps import apps
from django.conf import settings
from keycloak import KeycloakAdmin
from keycloak import KeycloakOpenIDConnection
from keycloak.exceptions import KeycloakGetError

def _get_user_group_model():
    """
    Dynamically get the UserGroup model.

    Attempts to use the model specified in settings.KEYCLOAK_USER_GROUP_MODEL.

    Returns:
        The UserGroup model class.

    Raises:
        LookupError: If the model cannot be found.
    """
    try:
        model_string = getattr(settings, "KEYCLOAK_USER_GROUP_MODEL")
    except AttributeError:
        raise LookupError(
            "Please set KEYCLOAK_USER_GROUP_MODEL in your Django settings "
            "(e.g., 'myapp.UserGroup')."
        )

    return apps.get_model(model_string)


class KeycloakService:
    def __init__(self):
        self._user_group_model = _get_user_group_model()
        self._keycloak_admin = self._get_keycloak_admin()

    def sync_user_groups(self, raise_exceptions: bool = False):
        print("Syncing user groups from Keycloak...")

        try:
            groups = self._keycloak_admin.get_groups(full_hierarchy=True)
        except KeycloakGetError as e:
            print(f"Failed to fetch groups from Keycloak: {str(e)}")
            if raise_exceptions:
                raise e

            return

        # Process existing and new groups
        existing_groups = self._user_group_model.objects.all()
        existing_groups_by_id = {str(group.id): group for group in existing_groups}

        reported_group_ids = set()
        for group in groups:
            self._process_group_recursively(
                group, existing_groups_by_id, reported_group_ids
            )

        # Identify deleted groups
        deleted_groups = self._user_group_model.objects.exclude(
            id__in=reported_group_ids
        )
        if deleted_groups.exists():
            print(
                f"Deleting groups no longer present in Keycloak: {list(deleted_groups.values_list('path', flat=True))}"
            )
            deleted_groups.delete()

    def _get_keycloak_admin(self):
        keycloak_connection = KeycloakOpenIDConnection(
            server_url=settings.KEYCLOAK_SERVER_URL,
            realm_name=settings.KEYCLOAK_REALM,
            user_realm_name=settings.KEYCLOAK_REALM,
            client_id=settings.KEYCLOAK_ADMIN_CLIENT_ID,
            client_secret_key=settings.KEYCLOAK_ADMIN_CLIENT_SECRET,
            verify=True,
        )
        return KeycloakAdmin(connection=keycloak_connection)

    def _process_group_recursively(
        self, group, existing_groups_by_id, reported_group_ids
    ):
        group_id = str(group["id"])
        reported_group_ids.add(group_id)

        if group_id in existing_groups_by_id:
            existing_group = existing_groups_by_id[group_id]
            if existing_group.path != group["path"]:
                print(
                    f"Updating group path from {existing_group.path} to {group['path']}..."
                )
                existing_group.path = group["path"]
                existing_group.save()
        else:
            print(f"Creating new group with path {group['path']}...")
            self._user_group_model.objects.create(id=group_id, path=group["path"])

        if subgroups := group.get("subGroups"):
            for subgroup in subgroups:
                self._process_group_recursively(
                    subgroup, existing_groups_by_id, reported_group_ids
                )


class AuthServiceBase:
    @staticmethod
    def _get_all_level_paths(path: str) -> list[str]:
        """
        Given a group path, return all level paths up to the root.
        E.g., for "/a/b/c", return ["/a/b/c", "/a/b", "/a"]
        """
        paths = []
        while "/" in path:
            paths.append(path)
            path = "/".join(path.split("/")[:-1])
        return paths

    @classmethod
    def _get_user_groups_from_paths(cls, group_paths: list[str]):
        all_group_paths = set()
        for path in group_paths:
            all_group_paths.update(cls._get_all_level_paths(path))

        UserGroup = _get_user_group_model()
        user_groups = UserGroup.objects.filter(path__in=all_group_paths)

        # If a group is missing/has been renamed in Keycloak, sync the groups
        if user_groups.count() != len(all_group_paths):
            KeycloakService().sync_user_groups()
            user_groups = UserGroup.objects.filter(path__in=all_group_paths)

        return user_groups
