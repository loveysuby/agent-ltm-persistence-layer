from __future__ import annotations

import asyncio
from typing import Any

from langchain_core.messages import HumanMessage
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

from app.api.dependencies import get_database_conn_string
from app.core.graph import create_memory_graph
from app.core.tools import create_manage_memory_tool, create_search_memory_tool
from app.infrastructure.memory.langmem_store import LangMemStore


class AgentService:
    def __init__(self, user_id: str):
        self.user_id = user_id
        self._store_instance: LangMemStore | None = None
        self._store_lock = asyncio.Lock()
        self._checkpointer_instance: AsyncPostgresSaver | None = None
        self._checkpointer_cm: AsyncPostgresSaver | None = None
        self._checkpointer_lock = asyncio.Lock()
        self._database_url: str = get_database_conn_string()
        self._closed = False

    async def get_store(self) -> LangMemStore:
        if self._store_instance is not None:
            return self._store_instance

        async with self._store_lock:
            store = LangMemStore()
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

        from langmem import create_memory_store_manager

        memory_manager = create_memory_store_manager(
            "gpt-4o-mini",
            namespace=("memories", self.user_id),
            instructions="Extract user profile information",
            store=store.store,
        )

        memories = await memory_manager.asearch(
            query=message,
            config={
                "configurable": {"user_id": self.user_id},
            },
            limit=3,
        )

        # memories = await store.search_memories(user_id=self.user_id, query=message, limit=5)
        config = {"configurable": {"thread_id": f"{self.user_id}-{thread_id}"}}

        response = await memory_manager.ainvoke({"messages": [HumanMessage(content=message)]}, config=config)

        last_message = response[-1]
        assistant_response = last_message.content if hasattr(last_message, "content") else str(last_message)

        await store.process_conversation(
            user_id=self.user_id,
            messages=[
                {"role": "user", "content": message},
                {"role": "assistant", "content": assistant_response},
            ],
        )

        return {
            "response": memories,
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
        if enable_memory_tools:
            tools.append(create_search_memory_tool(store, self.user_id))
            tools.append(create_manage_memory_tool(store, self.user_id))

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
            await self._store_instance.aclose()
        if self._checkpointer_cm is not None:
            self._checkpointer_cm = None
            self._checkpointer_instance = None
        self._closed = True
