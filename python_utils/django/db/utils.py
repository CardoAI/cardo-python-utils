from functools import reduce
import json
import os
from typing import TypedDict
from django.db import connections


class DatabaseConfigData(TypedDict):
    host: str
    name: str
    user: str
    password: str
    port: int | None


def get_connection(tenant: str = None):
    """
    Get the connection to the database with the given tenant or the default one.
    Default value will be retrieved from TenantContext.get()
    This uses the connections dict from django.db to get the required connection.

    The default implementation of this function uses the 'default' alias
    if not argument is given. We want to use the TenantContext class to
    determine the correct alias.
    Args:
        tenant: Name of the tenant database alias

    Returns:    The connection to the database

    """
    from ..tenant_context import TenantContext

    database_alias = tenant or TenantContext.get()
    connection = connections[database_alias]

    return connection


def get_database_configs() -> dict[str, DatabaseConfigData]:
    """
    The env variables prefixed with 'DATABASE_CONFIG' should be provided in the following format:
    {
        "tenant1": {
            "host": "",
            "name": "",
            "user": "",
            "password": "",
            "port": 5432 / null
        },
        "tenant2": {
            "host": "",
            "name": "",
            "user": "",
            "password": ""
        }
    }
    If multiple 'DATABASE_CONFIG'-prefixed variables are set, they will be merged into a single dictionary.
    """
    configs = [json.loads(v or "{}") for k, v in os.environ.items() if k.startswith("DATABASE_CONFIG")]
    database_configs = reduce(lambda a, b: {**a, **b}, configs, {})
    for tenant, db_config in database_configs.items():
        for key in ["host", "name", "user", "password"]:
            if key not in db_config:
                raise ValueError(f"Missing required database config '{key}' for tenant {tenant}")

    return database_configs
