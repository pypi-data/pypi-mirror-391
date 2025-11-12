# arcbeam-langchain-connector

## Overview
`arcbeam-langchain-connector` captures LangChain runs and forwards richly annotated execution graphs to the Arcbeam observability platform. It ships with a drop-in callback handler that records chains, tools, retrievers, and token usage so teams can trace how agents reason and where they spend time.

## Features
- Builds an `ArcbeamHandler` that turns LangChain callback events into Arcbeam-compatible traces.
- Normalizes model names, token counts, and message payloads across providers via `langchain_utils`.
- Emits structured graphs over HTTP (default `http://localhost:3000/api/v0/traces`) ready for ingestion by Arcbeam dashboards.

## Requirements
- Python 3.13+
- Optional tooling: [`uv`](https://github.com/astral-sh/uv) for environment management, `pytest`, and `ruff` for linting.

## Installation
### Install uv
```bash
uv add arcbeam-langchain-connector
```

### Install from a Local Folder (editable) with uv
```bash
pip3 install arcbeam-langchain-connector
```

## Quick Start
### Basic LLM Call
```python
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from arcbeam_langchain_connector import ArcbeamHandler

handler = ArcbeamHandler(project_id="00000000-0000-4000-8000-000000000001")
llm = ChatOpenAI(callbacks=[handler])

response = llm.invoke([HumanMessage(content="Summarize Arcbeam's tracing flow in one sentence.")])
print(response.content)
```
The handler posts the captured trace to `http://localhost:5173`. Configure your Arcbeam service or override the target URL in your own subclass before running these snippets.

### Trace a Chain
```python
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from arcbeam_langchain_connector import ArcbeamHandler

handler = ArcbeamHandler()
llm = ChatOpenAI()
prompt = ChatPromptTemplate.from_template("Explain {topic} in two sentences.")
chain = prompt | llm

result = chain.invoke({"topic": "Arcbeam trace ingestion"}, config={"callbacks": [handler]})
print(result.content)
```
Any runnable built from LangChain components can emit callback events; pass the handler through the `config` to keep tracing out-of-band from chain construction.

### Trace an Agent
```python
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool
from arcbeam_langchain_connector import ArcbeamHandler

@tool
def uppercase(text: str) -> str:
    """Return the text in uppercase for demo purposes."""
    return text.upper()

handler = ArcbeamHandler()
llm = ChatOpenAI()
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant."),
    ("human", "{input}"),
])
agent = create_tool_calling_agent(llm, [uppercase], prompt)
agent_executor = AgentExecutor(agent=agent, tools=[uppercase])

agent_executor.invoke({"input": "use the tool to shout Arcbeam"}, config={"callbacks": [handler]})
```
Agents typically fan out across tools; the handler captures every intermediate tool call, final response, and LLM usage so Arcbeam can rebuild the execution graph.

## Development Tasks
- `uv sync` — create or refresh the local environment based on `uv.lock`.
- `uv run python -m pytest` — execute the test suite once you add coverage under `tests/`.
- `uv run ruff check .` — enforce the import-order rules declared in `[tool.ruff]`.

## Configuration Notes
- Provide production credentials via environment variables (for example `ARCBEAM_API_URL` and `ARCBEAM_API_KEY`) rather than hardcoding.
- Mock `requests.post` in tests so execution graphs never reach real services during CI.

## License
Distributed under the terms of the MIT license. See `LICENSE` for details.
