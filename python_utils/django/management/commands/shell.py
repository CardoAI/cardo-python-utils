from django.core.management.commands.shell import Command as ShellCommand

from ...settings import TENANT_DATABASES
from ...tenant_context import TenantContext


class Command(ShellCommand):
    help = "Runs a Python interactive interpreter for a specific tenant."

    def add_arguments(self, parser):
        super().add_arguments(parser)

        parser.add_argument(
            "--tenant",
            action="store",
            dest="tenant",
            help="Specify the tenant to run the shell for.",
            required=True,
            type=str,
        )

    def handle(self, **options):
        tenant = options["tenant"]

        if tenant not in TENANT_DATABASES:
            self.stdout.write(self.style.ERROR(f"Tenant '{tenant}' not found in DATABASES settings."))
            return

        self.stdout.write(self.style.SUCCESS(f"Starting shell for tenant: {tenant}"))

        with TenantContext(tenant):
            super().handle(**options)
