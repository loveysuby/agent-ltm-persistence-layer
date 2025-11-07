from __future__ import annotations

from collections.abc import AsyncGenerator
from typing import Any

from langgraph.store.postgres import AsyncPostgresStore

_store_instance: AsyncPostgresStore | None = None
_store_cm: Any = None


async def _init_store() -> AsyncPostgresStore:
    """
    스토어 인스턴스 초기화 (내부 사용)
    """
    global _store_instance, _store_cm
    if _store_instance is None:
        from app.config.settings import get_pg_store_conn_string

        conn_string = get_pg_store_conn_string()
        _store_cm = AsyncPostgresStore.from_conn_string(conn_string)

        store = await _store_cm.__aenter__()
        await store.setup()
        _store_instance = store
        logger.info("AsyncPostgresStore initialized with connection pool (singleton)")

    assert _store_instance is not None
    return _store_instance


async def get_memory_store() -> AsyncGenerator[AsyncPostgresStore, None]:
    """
    FastAPI 의존성 주입용 제너레이터.

    Usage:
        @app.get("/memories")
        async def get_memories(store: AsyncPostgresStore = Depends(get_memory_store)):
            memories = await store.asearch(...)
            return memories
    """
    store = await _init_store()
    yield store


async def get_store() -> AsyncPostgresStore:
    """
    Usage:
        store = await get_store()
        await store.aput(namespace, key, value)
    """
    return await _init_store()
