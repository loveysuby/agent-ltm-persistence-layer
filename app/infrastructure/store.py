from __future__ import annotations

import logging
from typing import Any

import psycopg
from langgraph.store.postgres import AsyncPostgresStore

logger = logging.getLogger(__name__)

_store_instance: AsyncPostgresStore | None = None
_store_cm: Any = None


async def _ensure_schema_exists(schema_name: str) -> None:
    if schema_name == "public":
        return

    from psycopg import sql

    from app.config.settings import get_settings

    settings = get_settings()
    base_conn_string = f"postgresql://{settings.db_user}:{settings.db_password}@{settings.db_host}:{settings.db_port}/{settings.db_name}"

    try:
        async with await psycopg.AsyncConnection.connect(base_conn_string) as conn:
            async with conn.cursor() as cur:
                query = sql.SQL("CREATE SCHEMA IF NOT EXISTS {}").format(sql.Identifier(schema_name))
                await cur.execute(query)
                await conn.commit()
                logger.info(f"Schema '{schema_name}' ensured")
    except Exception as e:
        logger.error(f"Failed to create schema '{schema_name}': {e}")
        raise


def _log_migrations() -> None:
    logger.info("=" * 80)
    logger.info("MIGRATIONS TO BE EXECUTED:")
    logger.info("=" * 80)

    for i, migration_sql in enumerate(AsyncPostgresStore.MIGRATIONS):
        logger.info(f"\n--- Migration {i} ---")
        logger.info(migration_sql.strip())

    logger.info("\n" + "=" * 80)
    logger.info("VECTOR MIGRATIONS TO BE EXECUTED:")
    logger.info("=" * 80)

    if hasattr(AsyncPostgresStore, 'VECTOR_MIGRATIONS'):
        for i, migration in enumerate(AsyncPostgresStore.VECTOR_MIGRATIONS):
            logger.info(f"\n--- Vector Migration {i} ---")
            logger.info(f"SQL: {migration.sql.strip()}")
            if hasattr(migration, 'params') and migration.params:
                logger.info(f"Params: {migration.params}")

    logger.info("\n" + "=" * 80)


async def _init_store() -> AsyncPostgresStore:
    global _store_instance, _store_cm
    if _store_instance is None:
        from app.config.settings import get_pg_store_conn_string, get_settings

        settings = get_settings()
        conn_string = get_pg_store_conn_string()

        logger.info("=" * 80)
        logger.info("Initializing AsyncPostgresStore")
        logger.info(f"Schema: {settings.store_schema}")
        masked_conn = conn_string.split('@')[0].split('//')[1] if '@' in conn_string else '***'
        logger.info(f"Connection String: {conn_string.replace(masked_conn, '***')}")
        logger.info("=" * 80)

        await _ensure_schema_exists(settings.store_schema)

        _log_migrations()

        _store_cm = AsyncPostgresStore.from_conn_string(conn_string)

        store = await _store_cm.__aenter__()  # type: ignore[union-attr]

        logger.info("=" * 80)
        logger.info("Executing store.setup()")
        logger.info("=" * 80)

        await store.setup()  # type: ignore[union-attr]

        logger.info("=" * 80)
        logger.info("store.setup() completed successfully")
        logger.info(f"Tables created in schema: {settings.store_schema}")
        logger.info("=" * 80)

        _store_instance = store
        logger.info("AsyncPostgresStore initialized with connection pool (singleton)")

    assert _store_instance is not None
    return _store_instance


async def get_store() -> AsyncPostgresStore:
    """
    Usage:
        store = await get_store()
        await store.aput(namespace, key, value)
    """
    return await _init_store()


