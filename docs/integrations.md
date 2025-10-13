### Basic Usage

```python
from ltm.integrations.langchain import LangChainIntegration

integration = LangChainIntegration()
tools = integration.get_tools()
```

### With Agent

```python
from langchain_openai import ChatOpenAI
from langchain.agents import create_openai_functions_agent, AgentExecutor

llm = ChatOpenAI(model="gpt-4")
agent = create_openai_functions_agent(llm, tools, prompt)
executor = AgentExecutor(agent=agent, tools=tools)

result = await executor.ainvoke({"input": "Remember that I like Python"})
```

## LangGraph Integration

### Basic Usage

```python
from ltm.integrations.langgraph import LangGraphIntegration

integration = LangGraphIntegration()
nodes = integration.get_nodes()
```

### With Graph

```python
from langgraph.graph import StateGraph, END

graph = StateGraph(dict)

graph.add_node("load_memories", nodes["load_memories"])
graph.add_node("inject_memories", nodes["inject_memories"])
graph.add_node("process", your_process_node)
graph.add_node("save_memories", nodes["save_memories"])

graph.add_edge("load_memories", "inject_memories")
graph.add_edge("inject_memories", "process")
graph.add_edge("process", "save_memories")
graph.add_edge("save_memories", END)

graph.set_entry_point("load_memories")
compiled = graph.compile()

result = await compiled.ainvoke({
    "messages": [HumanMessage(content="Hello")],
    "user_id": "uuid"
})
```

## Direct Usage

### Save Memory

```python
from ltm import MemoryManager, MemoryCreate, MemoryType
from uuid import UUID

manager = MemoryManager()

memory = await manager.save(MemoryCreate(
    user_id=UUID("..."),
    content="User likes AI",
    memory_type=MemoryType.SEMANTIC
))
```

### Search Memory

```python
results = await manager.search(
    query="AI preferences",
    user_id=UUID("..."),
    limit=5,
    threshold=0.7
)

for memory, score in results:
    print(f"{memory.content} (score: {score})")
```

### Get User Memories

```python
memories = await manager.get_user_memories(
    user_id=UUID("..."),
    limit=50
)
```

### Delete Memory

```python
deleted = await manager.delete(
    memory_id=UUID("..."),
    user_id=UUID("...")
)
```
