from abc import abstractmethod
from django.core.management import BaseCommand

from ...settings import TENANT_DATABASES
from ...tenant_context import TenantContext


class TenantAwareCommand(BaseCommand):
    """
    Base class for all tenant aware commands.
    The usage is like this:

    class MyCommand(TenantAwareCommand):
        def add_arguments(self, parser):
            super().add_arguments(parser)
            # add your own arguments here

        def execute_command(self, *args, **options):
            # logic to execute for each tenant
    """

    def add_arguments(self, parser):
        """
        Add the tenant argument to the command. The tenant argument is
        required in a multi tenant environment.
        The tenant value can either be a single tenant name or 'all' to run
        the command for all tenants.
        """
        parser.add_argument(
            "--tenant",
            action="store",
            dest="tenant",
            help="Specify the tenant to run the command for, either a single tenant name or 'all'.",
            required=True,
            type=str,
        )

    def handle(self, *args, **options):
        """
        Get the tenant name from the command line arguments and set it as
        the current tenant using TenantContext.set().
        """
        tenant = options["tenant"]
        if tenant is None:
            self.stdout.write(
                self.style.ERROR(
                    "Please provide --tenant in order to run this command, either a single tenant name or 'all'!"
                )
            )
            exit()

        if tenant.lower() == "all":
            tenants_to_use = TENANT_DATABASES
        else:
            if tenant not in TENANT_DATABASES:
                self.stdout.write(self.style.ERROR(f"Tenant '{tenant}' not found in DATABASES settings."))
                exit()

            tenants_to_use = [tenant]

        for tenant in tenants_to_use:
            self.stdout.write(f"Executing command for tenant: {tenant}")
            options["database"] = tenant
            with TenantContext(tenant):
                self.execute_command(*args, **options)

    @abstractmethod
    def execute_command(self, *args, **options):
        """
        Abstract method to be implemented by the child class.
        This method will be called by the handle() method after
        setting the tenant context.
        """
        pass
