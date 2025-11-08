from __future__ import annotations

import logging
from typing import Any

from langgraph.store.postgres import AsyncPostgresStore

logger = logging.getLogger(__name__)

_store_instance: AsyncPostgresStore | None = None
_store_cm: Any = None


async def _init_store() -> AsyncPostgresStore:
    global _store_instance, _store_cm
    if _store_instance is None:
        from app.config.settings import get_pg_store_conn_string

        conn_string = get_pg_store_conn_string()
        _store_cm = AsyncPostgresStore.from_conn_string(conn_string)

        store = await _store_cm.__aenter__()  # type: ignore[union-attr]
        await store.setup()  # type: ignore[union-attr]
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
