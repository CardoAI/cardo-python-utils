from django.db import models


class UserGroupBase(models.Model):
    """
    Abstract base model for Keycloak user groups.
    """
    id = models.UUIDField(
        primary_key=True,
        help_text="The ID of the group, as coming from Keycloak.",
    )
    path = models.CharField(
        max_length=255,
        help_text="The full path of the group, as coming from Keycloak.",
        db_index=True,
    )

    def __str__(self):
        return self.path

    class Meta:
        abstract = True
