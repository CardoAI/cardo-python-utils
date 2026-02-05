from celery import Task

from ..settings import TENANT_KEY
from ..tenant_context import TenantContext


class TenantAwareTask(Task):
    #: Enable argument checking.
    #: You can set this to false if you don't want the signature to be
    #: checked when calling the task.
    #: Set to false because we are attaching a tenant to the task
    #: and we don't want to check the signature.
    #: Defaults to :attr:`app.strict_typing <@Celery.strict_typing>`.
    typing = False

    def __call__(self, *args, **kwargs):
        """Override the __call__ method to set the tenant name in the thread namespace."""

        # Celery backend_cleanup doesn't need a tenant and cannot be configured to pass the tenant kwarg
        # because it is dynamically generated at @connect_on_app_finalize by celery itself
        # ref: celery/app/builtins.py def add_backend_cleanup_task
        if self.name != "celery.backend_cleanup":
            tenant = kwargs.pop(TENANT_KEY)
            TenantContext.set(tenant)

        return self.run(*args, **kwargs)

    def after_return(self, status, retval, task_id, args, kwargs, einfo):
        """Clear the tenant from the thread namespace after the task has returned."""
        TenantContext.clear()
        super().after_return(status, retval, task_id, args, kwargs, einfo)
