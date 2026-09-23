"""Row-level security plumbing.

Broker-private tables carry a ``broker_org_id`` column and a Postgres policy that only
exposes rows whose org matches the ``app.broker_org_id`` setting of the current
transaction. The setting is transaction-local (``set_config(..., true)``), so it can
never leak across requests on a pooled connection.

System jobs that need cross-broker *aggregates* (map cells, anonymised status
notifications) run inside :func:`platform_context`.
"""

from contextlib import contextmanager

from django.db import connection, migrations, transaction

RLS_FUNCTION_SQL = """
CREATE OR REPLACE FUNCTION ob_rls_allows(org uuid) RETURNS boolean
LANGUAGE sql STABLE AS $$
  SELECT coalesce(current_setting('app.rls_bypass', true), '') = 'on'
      OR org = nullif(current_setting('app.broker_org_id', true), '')::uuid
$$;
"""


def _set(name: str, value: str) -> None:
    with connection.cursor() as cur:
        cur.execute("SELECT set_config(%s, %s, true)", [name, value])


def set_org(org_id) -> None:
    _set("app.broker_org_id", str(org_id) if org_id else "")


def clear() -> None:
    _set("app.broker_org_id", "")
    _set("app.rls_bypass", "")


def current_org():
    with connection.cursor() as cur:
        cur.execute("SELECT nullif(current_setting('app.broker_org_id', true), '')")
        return cur.fetchone()[0]


@contextmanager
def org_context(org_id):
    """Run a block as broker org ``org_id`` (for Celery tasks, consumers and tests)."""
    with transaction.atomic():
        with connection.cursor() as cur:
            cur.execute("SELECT current_setting('app.broker_org_id', true), current_setting('app.rls_bypass', true)")
            prev_org, prev_bypass = cur.fetchone()
        set_org(org_id)
        _set("app.rls_bypass", "")
        try:
            yield
        finally:
            _set("app.broker_org_id", prev_org or "")
            _set("app.rls_bypass", prev_bypass or "")


@contextmanager
def platform_context():
    """Cross-tenant access for trusted system code. Must only emit aggregates or anonymised data."""
    with transaction.atomic():
        with connection.cursor() as cur:
            cur.execute("SELECT current_setting('app.rls_bypass', true)")
            prev = cur.fetchone()[0]
        _set("app.rls_bypass", "on")
        try:
            yield
        finally:
            _set("app.rls_bypass", prev or "")


class RlsResetMiddleware:
    """Start every request with an empty RLS context; authentication sets the org later."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        clear()
        if request.path.startswith("/django-admin/") and getattr(request.user, "is_superuser", False):
            # Platform staff using the Django admin see across tenants (audited via admin log).
            _set("app.rls_bypass", "on")
        return self.get_response(request)


def enable_rls(table: str, column: str = "broker_org_id") -> migrations.RunSQL:
    """Migration operation: turn on (forced) RLS with the org-isolation policy."""
    return migrations.RunSQL(
        sql=[
            RLS_FUNCTION_SQL,
            f'ALTER TABLE "{table}" ENABLE ROW LEVEL SECURITY',
            f'ALTER TABLE "{table}" FORCE ROW LEVEL SECURITY',
            f'CREATE POLICY org_isolation ON "{table}" USING (ob_rls_allows({column})) WITH CHECK (ob_rls_allows({column}))',
        ],
        reverse_sql=[
            f'DROP POLICY IF EXISTS org_isolation ON "{table}"',
            f'ALTER TABLE "{table}" NO FORCE ROW LEVEL SECURITY',
            f'ALTER TABLE "{table}" DISABLE ROW LEVEL SECURITY',
        ],
    )


def forbid_update_delete(table: str) -> migrations.RunSQL:
    """Migration operation: make a ledger table append-only."""
    fn = f"{table}_append_only"
    return migrations.RunSQL(
        sql=[
            f"""CREATE OR REPLACE FUNCTION {fn}() RETURNS trigger LANGUAGE plpgsql AS $$
                BEGIN RAISE EXCEPTION '{table} is append-only'; END $$;""",
            f'CREATE TRIGGER {fn}_trg BEFORE UPDATE OR DELETE ON "{table}" FOR EACH ROW EXECUTE FUNCTION {fn}()',
        ],
        reverse_sql=[f'DROP TRIGGER IF EXISTS {fn}_trg ON "{table}"', f"DROP FUNCTION IF EXISTS {fn}()"],
    )
