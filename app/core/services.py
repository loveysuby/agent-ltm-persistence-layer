from __future__ import annotations

import asyncio
from typing import Any

from langchain_core.messages import HumanMessage
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

from app.api.dependencies import get_database_conn_string
from app.core.graph import create_memory_graph
from app.infrastructure.memory.memory_manager import MemoryManager


class AgentService:
    def __init__(self, user_id: str):
        self.user_id = user_id
        self._store_instance: MemoryManager | None = None
        self._store_lock = asyncio.Lock()
        self._checkpointer_instance: AsyncPostgresSaver | None = None
        self._checkpointer_cm: AsyncPostgresSaver | None = None
        self._checkpointer_lock = asyncio.Lock()
        self._database_url: str = get_database_conn_string()
        self._closed = False

    async def get_store(self) -> MemoryManager:
        if self._store_instance is not None:
            return self._store_instance

        async with self._store_lock:
            store = MemoryManager()
            await store.setup()
            self._store_instance = store
        return self._store_instance

    async def get_checkpointer(self) -> AsyncPostgresSaver:
        if self._checkpointer_instance is not None:
            return self._checkpointer_instance

        async with self._checkpointer_lock:
            conn_string = self._database_url
            cm = AsyncPostgresSaver.from_conn_string(conn_string)
            instance = await cm.__aenter__()
            await instance.setup()
            self._checkpointer_cm = cm
            self._checkpointer_instance = instance
        return self._checkpointer_instance

    async def chat(self, message: str, thread_id: str = "default") -> dict[str, Any]:
        store = await self.get_store()
        memories = await store.search_memories(user_id=self.user_id, query=message, limit=3)

        assistant_response = f"I understand you said: {message}. I found {len(memories)} relevant memories."

        # 대화 처리 및 메모리 저장
        await store.process_conversation(
            user_id=self.user_id,
            messages=[
                {"role": "user", "content": message},
                {"role": "assistant", "content": assistant_response},
            ],
        )

        return {
            "response": assistant_response,
            "memories": memories,
            "thread_id": thread_id,
            "conversation": {"user": message, "assistant": assistant_response},
        }

    async def get_memories(self) -> list[dict[str, Any]]:
        store = await self.get_store()
        return await store.get_all_memories(user_id=self.user_id)

    async def chat_with_tools(
        self, message: str, thread_id: str = "default", enable_memory_tools: bool = True
    ) -> dict[str, Any]:
        store = await self.get_store()
        checkpointer = await self.get_checkpointer()

        tools = []

        graph = create_memory_graph(store=store, checkpointer=checkpointer, tools=tools if tools else None)

        initial_state = {
            "messages": [HumanMessage(content=message)],
            "user_id": self.user_id,
            "memories": [],
            "system_prompt": "You are a helpful assistant with access to user memories.",
        }

        result = await graph.ainvoke(initial_state)

        last_message = result["messages"][-1]
        assistant_response = last_message.content if hasattr(last_message, "content") else str(last_message)

        return {
            "response": assistant_response,
            "thread_id": thread_id,
            "conversation": {"user": message, "assistant": assistant_response},
            "memories_used": len(result.get("memories", [])),
        }

    async def aclose(self):
        if self._store_instance is not None:
            await self._store_instance.__aclose__()
        if self._checkpointer_cm is not None:
            self._checkpointer_cm = None
            self._checkpointer_instance = None
        self._closed = True
