from copy import deepcopy

from celery import Task

from ..settings import TENANT_KEY
from ..tenant_context import TenantContext

try:
    # If celery_once is installed, use QueueOnce as the base class for TenantAwareTask.
    from celery_once.tasks import QueueOnce

    TaskClass = QueueOnce
    USE_QUEUE_ONCE = True
except ImportError:
    TaskClass = Task
    USE_QUEUE_ONCE = False


class TenantAwareTask(TaskClass):
    #: Enable argument checking.
    #: You can set this to false if you don't want the signature to be
    #: checked when calling the task.
    #: Set to false because we are attaching a tenant to the task
    #: and we don't want to check the signature.
    #: Defaults to :attr:`app.strict_typing <@Celery.strict_typing>`.
    typing = False

    once = {"graceful": True, "unlock_before_run": False}

    def __call__(self, *args, **kwargs):
        """Override the __call__ method to set the tenant name in the thread namespace."""

        # Only clear the lock before the task's execution if the
        # "unlock_before_run" option is True
        if USE_QUEUE_ONCE and self.unlock_before_run():
            key = self.get_key(args, kwargs)
            self.once_backend.clear_lock(key)

        if self.name != "celery.backend_cleanup":
            tenant = kwargs.pop(TENANT_KEY)
            TenantContext.set(tenant)

        return self.run(*args, **kwargs)

    def after_return(self, status, retval, task_id, args, kwargs, einfo):
        """Clear the tenant from the thread namespace after the task has returned."""
        TenantContext.clear()
        super().after_return(status, retval, task_id, args, kwargs, einfo)

    def _get_call_args(self, args, kwargs):
        """This method is used by QueueOnce, to create the key for the lock."""

        # Celery backend_cleanup doesn't need a tenant and cannot be configured to pass the tenant kwarg
        # because it is dynamically generated at @connect_on_app_finalize by celery itself
        # ref: celery/app/builtins.py def add_backend_cleanup_task
        if self.name == "celery.backend_cleanup":
            return super()._get_call_args(args, kwargs)

        # QueueOnce._get_call_args validates the args and kwargs
        # by binding them to the task signature.
        # Since the TENANT_KEY kwarg is not part of the signature,
        # we need to remove it from the kwargs before passing them
        # to QueueOnce._get_call_args.
        # Copy the kwargs so that we don't modify the original kwargs.
        _kwargs = deepcopy(kwargs)
        tenant = _kwargs.pop(TENANT_KEY)
        tenant_kwarg = {TENANT_KEY: tenant}
        task_call_args = super()._get_call_args(args, _kwargs)

        # Add the tenant kwarg back to the return value 
        # since this value is being used to create the key for the lock.
        # We want to lock the task for the tenant that is running it.
        return task_call_args | tenant_kwarg
