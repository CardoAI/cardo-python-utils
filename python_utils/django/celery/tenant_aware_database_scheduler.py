"""
Multi-tenant Celery Beat scheduler.

Reads periodic tasks from every tenant database and injects the ``tenant``
kwarg so that ``TenantAwareTask`` can route each execution to the correct
database.  Static beat-schedule entries (``CELERY_BEAT_SCHEDULE``) are also
run once per tenant.
"""

from contextlib import contextmanager

from celery.utils.log import get_logger
from django.db import close_old_connections, transaction
from django.db.utils import DatabaseError, InterfaceError
from django_celery_beat.models import PeriodicTask, PeriodicTasks
from django_celery_beat.schedulers import DatabaseScheduler, ModelEntry

from ..settings import TENANT_DATABASES, TENANT_KEY
from ..tenant_context import TenantContext

logger = get_logger(__name__)
debug, info, warning = logger.debug, logger.info, logger.warning


class TenantAwareModelEntry(ModelEntry):
    """
    A schedule entry that remembers which tenant it belongs to and
    injects the tenant kwarg when the task is applied.
    """

    def __init__(self, model, app=None, tenant=None):
        self.tenant = tenant
        super().__init__(model, app=app)
        # Prefix the name so entries from different tenants don't collide.
        self.name = f"{self.tenant}::{self.name}"

    @contextmanager
    def _ensure_tenant_context(self):
        """Set TenantContext only when not already active (TenantContext is not re-entrant)."""
        if TenantContext.is_set():
            yield
        else:
            with TenantContext(self.tenant):
                yield

    def _disable(self, model):
        """Route the save to the correct tenant database."""
        with self._ensure_tenant_context():
            super()._disable(model)

    def save(self):
        """Persist last_run_at / total_run_count to the correct tenant database."""
        with self._ensure_tenant_context():
            super().save()

    def __next__(self):
        self.model.last_run_at = self._default_now()
        self.model.total_run_count += 1
        self.model.no_changes = True
        return self.__class__(self.model, app=self.app, tenant=self.tenant)

    next = __next__

    def __repr__(self):
        return f"<TenantAwareModelEntry: [{self.tenant}] {self.task} {self.schedule}>"


class TenantAwareDatabaseScheduler(DatabaseScheduler):
    """
    ``DatabaseScheduler`` subclass that aggregates periodic tasks across
    **all** tenant databases.

    For every tick it:

    1. Reads ``PeriodicTask`` rows from each tenant DB.
    2. Wraps them in ``TenantAwareModelEntry`` (which carries the tenant name).
    3. When a task is due, injects ``tenant=<name>`` into the task kwargs
       so that ``TenantAwareTask`` can set the context on the worker side.
    """

    Entry = TenantAwareModelEntry

    def __init__(self, *args, **kwargs):
        self._last_timestamps: dict[str, object] = {}
        super().__init__(*args, **kwargs)

    @staticmethod
    def _get_tenant_databases() -> set[str]:
        return TENANT_DATABASES

    def all_as_schedule(self):
        """Build the combined schedule dict from all tenant databases."""
        debug("TenantAwareDatabaseScheduler: Fetching schedule from all tenants")
        combined: dict[str, TenantAwareModelEntry] = {}

        for tenant in self._get_tenant_databases():
            with TenantContext(tenant):
                try:
                    for model in PeriodicTask.objects.enabled():
                        try:
                            entry = TenantAwareModelEntry(model, app=self.app, tenant=tenant)
                            combined[entry.name] = entry
                        except ValueError as exc:
                            logger.warning(
                                "TenantAwareDatabaseScheduler: skipping malformed periodic task '%s' in tenant '%s': %r",
                                model.name,
                                tenant,
                                exc,
                            )
                except Exception as exc:
                    logger.exception(
                        "TenantAwareDatabaseScheduler: error reading tenant %s: %r",
                        tenant,
                        exc,
                    )

        return combined

    def schedule_changed(self):
        """Check whether *any* tenant database has had a schedule change."""
        changed = False
        try:
            close_old_connections()

            for tenant in self._get_tenant_databases():
                try:
                    transaction.commit(using=tenant)
                except transaction.TransactionManagementError:
                    pass

                try:
                    with TenantContext(tenant):
                        ts = PeriodicTasks.last_change()
                    last = self._last_timestamps.get(tenant)
                    if ts and ts > (last if last else ts):
                        changed = True
                    self._last_timestamps[tenant] = ts
                except (DatabaseError, InterfaceError) as exc:
                    logger.warning(
                        "TenantAwareDatabaseScheduler: error checking schedule_changed for tenant %s: %r",
                        tenant,
                        exc,
                    )
        except (DatabaseError, InterfaceError) as exc:
            logger.exception("Database error in schedule_changed: %r", exc)
            return False

        return changed

    def is_due(self, entry):
        """Wrap in TenantContext so that any model.save() calls within
        (e.g. disabling one-off tasks) are routed to the correct tenant DB."""
        tenant = getattr(entry, "tenant", None)
        if tenant:
            with TenantContext(tenant):
                return entry.is_due()
        return entry.is_due()

    def apply_entry(self, entry, producer=None):
        """Inject the ``tenant`` kwarg before dispatching the task so that
        ``TenantAwareTask.__call__`` can set the tenant context on the worker.

        Built-in tasks like ``celery.backend_cleanup`` are skipped because
        they are not ``TenantAwareTask`` subclasses and don't accept the kwarg.
        """
        tenant = getattr(entry, "tenant", None)
        if tenant and entry.task != "celery.backend_cleanup":
            extra_kwargs = dict(entry.kwargs or {})
            extra_kwargs[TENANT_KEY] = tenant
            entry.kwargs = extra_kwargs
        super().apply_entry(entry, producer=producer)

    def setup_schedule(self):
        # Skip install_default_entries: it calls update_from_dict →
        # Entry.from_entry which writes via _default_manager (no tenant
        # routing). The celery.backend_cleanup task can be added to
        # CELERY_BEAT_SCHEDULE in settings if needed.
        self._update_static_schedule_per_tenant()

    def _update_static_schedule_per_tenant(self):
        """
        For each entry in ``app.conf.beat_schedule``, create a
        ``PeriodicTask`` row in every tenant database so that static
        cron jobs run once per tenant.

        Uses ``TenantContext`` so that all DB operations inside
        ``_unpack_fields`` (schedule model lookups and saves) are
        routed to the correct tenant database.
        """
        beat_schedule = self.app.conf.beat_schedule or {}
        if not beat_schedule:
            return

        for tenant in self._get_tenant_databases():
            with TenantContext(tenant):
                for name, entry_fields in beat_schedule.items():
                    try:
                        defaults = ModelEntry._unpack_fields(**entry_fields)
                        PeriodicTask.objects.update_or_create(name=name, defaults=defaults)
                    except Exception as exc:
                        logger.exception(
                            "TenantAwareDatabaseScheduler: could not create "
                            "static schedule entry '%s' for tenant '%s': %r",
                            name,
                            tenant,
                            exc,
                        )
