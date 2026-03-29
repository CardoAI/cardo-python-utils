from django.core.management.commands.showmigrations import Command as ShowMigrationsCommand

from ...settings import TENANT_DATABASES
from ...tenant_context import TenantContext


class Command(ShowMigrationsCommand):
    help = "Shows all available migrations for a specific tenant."

    def add_arguments(self, parser):
        super().add_arguments(parser)

        parser.add_argument(
            "-t",
            "--tenant",
            action="store",
            dest="tenant",
            help="Specify the tenant to show migrations for, either a single tenant name or 'all'.",
            required=True,
            type=str,
        )

    def handle(self, *args, **options):
        tenant = options["tenant"]

        if tenant.lower() == "all":
            tenants_to_use = list(TENANT_DATABASES)
        else:
            if tenant not in TENANT_DATABASES:
                self.stdout.write(self.style.ERROR(f"Tenant '{tenant}' not found in DATABASES settings."))
                return
            tenants_to_use = [tenant]

        for t in tenants_to_use:
            self.stdout.write(self.style.MIGRATE_LABEL(f"\n=== Tenant: {t} ==="))
            options["database"] = t
            with TenantContext(t):
                super().handle(*args, **options)
