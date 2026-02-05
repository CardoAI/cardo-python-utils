from django.core.management.commands.migrate import Command as BaseMigrateCommand
from django.db.models.signals import post_migrate, pre_migrate
from django.dispatch import receiver

from ...settings import TENANT_DATABASES
from ...tenant_context import TenantContext


@receiver(pre_migrate)
def set_tenant_pre_migrate(sender, **kwargs):
    database_alias = kwargs.get("using")
    TenantContext.set(database_alias)


@receiver(post_migrate)
def clear_tenant_post_migrate(sender, **kwargs):
    TenantContext.clear()


class Command(BaseMigrateCommand):
    def handle(self, *args, **options):
        for tenant in TENANT_DATABASES:
            self.stdout.write(f"Migrating tenant: {tenant}")
            options["database"] = tenant
            super().handle(*args, **options)
