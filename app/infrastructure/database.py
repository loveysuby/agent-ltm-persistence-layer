from __future__ import annotations

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from psycopg import AsyncConnection
from psycopg.rows import dict_row
from psycopg_pool import AsyncConnectionPool

from app.config.settings import get_pg_store_conn_string


class DatabaseManager:
    def __init__(self):
        self.pool: AsyncConnectionPool | None = None
        self._connection_string: str = get_pg_store_conn_string()

    async def initialize(self) -> None:
        if self.pool is None:
            self.pool = AsyncConnectionPool(
                self._connection_string,
                min_size=2,
                max_size=10,
                timeout=30.0,
                check=AsyncConnectionPool.check_connection,
                kwargs={"row_factory": dict_row},
            )
            await self.pool.open()

    async def close(self) -> None:
        if self.pool:
            await self.pool.close()

    @asynccontextmanager
    async def get_connection(self) -> AsyncGenerator[AsyncConnection, None]:
        if not self.pool:
            await self.initialize()
        connection = await self.pool.getconn()
        try:
            yield connection
        finally:
            await self.release_connection(connection)

    async def release_connection(self, connection: AsyncConnection) -> None:
        if self.pool:
            await self.pool.putconn(connection)


db_manager = DatabaseManager()


async def get_db_connection() -> AsyncGenerator[AsyncConnection, None]:
    async with db_manager.get_connection() as connection:
        yield connection


async def close_database() -> None:
    """데이터베이스 연결 종료"""
    await db_manager.close()
