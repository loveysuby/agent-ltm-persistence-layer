from __future__ import annotations

from typing import Any, TypedDict

from langchain_core.messages import BaseMessage
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import create_react_agent

from app.infrastructure.memory.langmem_store import LangMemStore


class AgentState(TypedDict):
    messages: list[BaseMessage]
    user_id: str
    memories: list[dict[str, Any]]
    system_prompt: str


async def load_memories_node(state: AgentState, store: LangMemStore) -> dict[str, Any]:
    if not state["messages"]:
        return {"memories": []}

    last_message = state["messages"][-1].content
    memories = await store.search_memories(user_id=state["user_id"], query=str(last_message), limit=5)

    return {"memories": memories}


async def inject_memory_context_node(state: AgentState) -> dict[str, Any]:
    memories = state.get("memories", [])
    base_prompt = state.get("system_prompt", "You are a helpful assistant.")

    memory_contents = [m.get("content", "") for m in memories if m.get("content")]
    memory_text = "\n".join([f"- {content}" for content in memory_contents])

    enhanced_prompt = f"{base_prompt}\n\nRelevant user information:\n{memory_text}"
    return {"system_prompt": enhanced_prompt}

    return state


async def save_memory_node(state: AgentState, store: LangMemStore) -> dict[str, Any]:
    messages = state["messages"]
    if len(messages) < 2:
        return {}

    last_two_messages = messages[-2:]
    message_dicts = [{"role": msg.type, "content": msg.content} for msg in last_two_messages]

    await store.process_conversation(user_id=state["user_id"], messages=message_dicts)

    return {}


def create_memory_graph(store: LangMemStore, checkpointer: AsyncPostgresSaver, tools: list | None = None):
    workflow = StateGraph(AgentState)

    async def load_memories(state: AgentState) -> dict[str, Any]:
        return await load_memories_node(state, store)

    async def inject_context(state: AgentState) -> dict[str, Any]:
        return await inject_memory_context_node(state)

    async def agent_node(state: AgentState) -> dict[str, Any]:
        from langchain_openai import ChatOpenAI

        model = ChatOpenAI(model="gpt-4o-mini", temperature=0)

        if tools:
            agent = create_react_agent(
                model=model, prompt=state.get("system_prompt", "You are a helpful assistant."), tools=tools
            )
        else:
            agent = create_react_agent(model=model, prompt=state.get("system_prompt", "You are a helpful assistant."))

        config = {"configurable": {"thread_id": f"{state['user_id']}-graph"}}
        result = await agent.ainvoke({"messages": state["messages"]}, config=config)

        return {"messages": result["messages"]}

    async def save_memory(state: AgentState) -> dict[str, Any]:
        return await save_memory_node(state, store)

    workflow.add_node("load_memories", load_memories)
    workflow.add_node("inject_context", inject_context)
    workflow.add_node("agent", agent_node)
    workflow.add_node("save_memory", save_memory)

    workflow.add_edge(START, "load_memories")
    workflow.add_edge("load_memories", "inject_context")
    workflow.add_edge("inject_context", "agent")
    workflow.add_edge("agent", "save_memory")
    workflow.add_edge("save_memory", END)

    return workflow.compile(checkpointer=checkpointer)
