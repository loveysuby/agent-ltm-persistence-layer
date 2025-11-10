from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock


class MockStore:
    def __init__(self, storage: dict[str, dict[str, Any]]):
        self._storage = storage

    async def aput(self, namespace: tuple[str, ...], key: str, value: dict[str, Any]) -> None:
        storage_key = f"{':'.join(namespace)}:{key}"
        self._storage[storage_key] = value

    async def aget(self, namespace: tuple[str, ...], key: str):
        storage_key = f"{':'.join(namespace)}:{key}"
        if storage_key in self._storage:
            mock_result = MagicMock()
            mock_result.value = self._storage[storage_key]
            return mock_result
        return None

    async def asearch(self, namespace: tuple[str, ...], query: str, limit: int = 10) -> list[Any]:
        results: list[Any] = []
        namespace_prefix = ":".join(namespace)

        for storage_key, value in self._storage.items():
            if storage_key.startswith(namespace_prefix):
                if query.lower() in str(value).lower() or query == "":
                    key = storage_key.split(":")[-1]
                    mock_item = MagicMock()
                    mock_item.key = key
                    mock_item.value = value
                    results.append(mock_item)

        return results[:limit]

    async def adelete(self, namespace: tuple[str, ...], key: str) -> None:
        storage_key = f"{':'.join(namespace)}:{key}"
        if storage_key in self._storage:
            del self._storage[storage_key]
        else:
            raise KeyError(f"Key not found: {storage_key}")
