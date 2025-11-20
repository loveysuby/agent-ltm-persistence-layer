from __future__ import annotations

from app.services.service import MemoryService

_service_instance: MemoryService | None = None


def get_memory_service() -> MemoryService:
    global _service_instance
    if _service_instance is None:
        _service_instance = MemoryService()
    return _service_instance


__all__ = ["MemoryService", "get_memory_service"]
