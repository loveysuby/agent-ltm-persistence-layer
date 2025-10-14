from __future__ import annotations

from typing import Literal

from langchain_core.tools import tool

from app.infrastructure.memory.langmem_store import LangMemStore

### TODO : refactor with langmem Memory tools
# refs : https://langchain-ai.github.io/langmem/guides/memory_tools


def create_search_memory_tool(store: LangMemStore, user_id: str):
    @tool
    async def search_memory(query: str, limit: int = 5) -> list[dict]:
        """Search user memories by semantic similarity.

        Args:
            query: The search query to find relevant memories
            limit: Maximum number of memories to return (default: 5)

        Returns:
            List of relevant memories with their content and metadata
        """
        memories = await store.search_memories(user_id, query, limit)
        return memories

    return search_memory


def create_manage_memory_tool(store: LangMemStore, user_id: str):
    @tool
    async def manage_memory(
        action: Literal["create", "update", "delete"],
        memory_id: str | None = None,
        content: str | None = None,
    ) -> dict:
        """Create, update, or delete user memories.

        Args:
            action: The action to perform (create, update, or delete)
            memory_id: Required for update/delete actions
            content: Required for create/update actions

        Returns:
            Result of the memory operation
        """
        if action == "create":
            if content is None:
                return {"success": False, "error": "Content is required for create action"}
            result = await store.create_memory(user_id, content)
            return {"success": True, "memory": result}

        elif action == "update":
            if memory_id is None or content is None:
                return {"success": False, "error": "Memory ID and content are required for update action"}
            result = await store.update_memory(user_id, memory_id, content)
            if result is None:
                return {"success": False, "error": "Memory not found"}
            return {"success": True, "memory": result}

        elif action == "delete":
            if memory_id is None:
                return {"success": False, "error": "Memory ID is required for delete action"}
            success = await store.delete_memory(user_id, memory_id)
            return {"success": success}

        return {"success": False, "error": "Invalid action"}

    return manage_memory
