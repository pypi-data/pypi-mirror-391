import os
from typing import Any, List, Optional, Sequence, Tuple
from uuid import UUID

import requests

try:
    import langchain

    if langchain.__version__.startswith("1"):
        # Langchain v1
        from langchain_core.agents import AgentAction, AgentFinish
        from langchain_core.callbacks import (
            BaseCallbackHandler as LangchainBaseCallbackHandler,
        )
        from langchain_core.documents import Document
        from langchain_core.outputs import ChatGeneration

    else:
        # Langchain v0
        from langchain.callbacks.base import (  # type: ignore
            BaseCallbackHandler as LangchainBaseCallbackHandler,
        )
        from langchain.schema.agent import AgentAction, AgentFinish  # type: ignore
        from langchain.schema.document import Document  # type: ignore
        from langchain_core.outputs import (
            ChatGeneration,
        )

except ImportError:
    raise ModuleNotFoundError(
        "Please install langchain to use the Langfuse langchain integration: 'pip install langchain'"
    )

from pydantic import BaseModel, ConfigDict

from arcbeam_langchain_connector.langchain_utils import (
    _convert_message_to_dict,
    _extract_model_name,
    _extract_raw_response,
    _parse_usage,
    get_langchain_run_name,
)


class ArcbeamDocument(BaseModel):
    id: str
    content: str
    score: float
    metadata: dict


class ExecutionNode(BaseModel):
    id: str | UUID
    parent_id: str | UUID | None
    label: str
    type: str
    description: str = ""
    input: Any | None = None
    output: Any | None = None
    documents: List[ArcbeamDocument] | None = None
    model: str | None = None
    model_provider: str | None = None
    llm_usage: dict[str, int] | None = None


class ExecutionGraph(BaseModel):
    nodes: dict[str | UUID, ExecutionNode] = {}
    edges: List[Tuple[str | UUID, str | UUID]] = []
    _parent_id_lineage: dict[str | UUID, List[str | UUID]] = {}
    model: str = ""
    model_provider: str = ""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def __setitem__(self, name: str | UUID, value: ExecutionNode, /) -> None:
        self.nodes[name] = value

    def __getitem__(self, name: str | UUID, /) -> ExecutionNode:
        return self.nodes[name]


class ArcbeamHandler(LangchainBaseCallbackHandler):
    def __init__(
        self,
        project_id: Optional[str] = None,
        base_url: str = "https://platform.arcbeam.ai",
        api_key: Optional[str] = None,
    ):
        self.graph = ExecutionGraph()
        self.project_id = project_id
        self.base_url = base_url
        self.api_key = api_key or os.environ.get("ARCBEAM_API_KEY")
        self.run_inline = True

    def _add_node(self, run_id, parent_id, label, type_):
        if parent_id:
            if parent_id not in self.graph._parent_id_lineage:
                self.graph._parent_id_lineage[parent_id] = []

            if len(self.graph._parent_id_lineage[parent_id]) >= 1:
                self.graph.edges.append((self.graph._parent_id_lineage[parent_id][-1], run_id))
            else:
                self.graph.edges.append((parent_id, run_id))

            self.graph._parent_id_lineage[parent_id].append(run_id)

        self.graph.nodes[run_id] = ExecutionNode(id=run_id, parent_id=parent_id, label=label, type=type_)

    def on_chain_start(self, serialized, inputs, run_id, parent_run_id, metadata, **kwargs):
        type_ = "llm_chain"
        name = get_langchain_run_name(serialized, **kwargs)

        if serialized and "id" in serialized:
            class_path = serialized["id"]
            if any("agent" in part.lower() for part in class_path):
                type_ = "agent"

        if "agent" in name.lower():
            type_ = "agent"

        self._add_node(run_id=run_id, parent_id=parent_run_id, label=name, type_=type_)

        node_input = ""
        for v in inputs.values():
            if isinstance(v, list):
                self.graph.nodes[run_id].documents = [
                    ArcbeamDocument(
                        id=str(doc.id),
                        content=doc.page_content,
                        metadata=doc.metadata,
                        score=-1,
                    )
                    for doc in v
                ]
            else:
                node_input += v + "\n"

        if node_input:
            self.graph[run_id].input = node_input.strip()

    def on_chain_end(self, outputs, run_id, parent_run_id, **kwargs):
        # output for agents
        # text for llm chains
        self.graph[run_id].output = (
            outputs.get("text") or outputs.get("output") or outputs.get("output_text") or outputs.get("result")
        )

        if not parent_run_id:
            request_data = {
                "trace": self.graph.model_dump_json(),
            }

            if self.project_id:
                request_data["projectId"] = self.project_id

            headers = {"x-arcbeam-api-key": self.api_key}
            _ = requests.post(f"{self.base_url}/api/v0/traces", json=request_data, headers=headers)

    def on_agent_action(
        self,
        action: AgentAction,
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        **kwargs: Any,
    ) -> Any:
        self.graph.nodes.get(run_id, None)

        # if agent_run is not None:
        #     agent_run.input = kwargs.get("inputs")
        #     agent_run.output = action

    def on_agent_finish(
        self,
        finish: AgentFinish,
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        **kwargs: Any,
    ) -> Any:
        agent_run = self.graph.nodes.get(run_id, None)

        if agent_run is not None:
            agent_run.output = finish

    def on_llm_start(self, serialized, prompts, run_id, parent_run_id, metadata, **kwargs):
        name = get_langchain_run_name(serialized, **kwargs)
        model = _extract_model_name(serialized, **kwargs) or ""
        model_provider = metadata.get("ls_provider")

        if not self.graph.model:
            self.graph.model = model
            self.graph.model_provider = model_provider

        self._add_node(run_id=run_id, parent_id=parent_run_id, label=name, type_="llm_call")
        self.graph.nodes[run_id].input = prompts if len(prompts) > 1 else prompts[0]
        self.graph[run_id].model = model
        self.graph[run_id].model_provider = model_provider

    def on_llm_end(self, response, run_id, parent_run_id, **kwargs):
        response_generation = response.generations[-1][-1]
        extracted_response = (
            _convert_message_to_dict(response_generation.message)
            if isinstance(response_generation, ChatGeneration)
            else _extract_raw_response(response_generation)
        )
        llm_usage = _parse_usage(response)

        self.graph[run_id].output = extracted_response["content"]
        self.graph[run_id].llm_usage = llm_usage

    def on_tool_start(self, serialized, input_str, run_id, parent_run_id, **kwargs):
        tool_name = get_langchain_run_name(serialized, **kwargs)
        description = serialized.get("description", "")

        self._add_node(
            run_id=run_id,
            parent_id=parent_run_id,
            label=tool_name,
            type_="tool",
        )

        self.graph[run_id].description = description
        self.graph[run_id].input = input_str

    def on_tool_end(self, output, run_id, parent_run_id, **kwargs):
        self.graph.nodes[run_id].output = output

    def on_retriever_start(
        self,
        serialized: dict[str, Any],
        query: str,
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        tags: Optional[list[str]] = None,
        metadata: Optional[dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Any:
        self._add_node(
            run_id=run_id,
            parent_id=parent_run_id,
            label="Retriever",
            type_="retriever",
        )
        self.graph[run_id].input = query

    def on_retriever_end(
        self,
        documents: Sequence[Document],
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        **kwargs: Any,
    ) -> Any:
        self.graph.nodes[run_id].documents = [
            ArcbeamDocument(
                id=str(doc.id),
                content=doc.page_content,
                metadata=doc.metadata,
                score=-1,
            )
            for doc in documents
        ]
