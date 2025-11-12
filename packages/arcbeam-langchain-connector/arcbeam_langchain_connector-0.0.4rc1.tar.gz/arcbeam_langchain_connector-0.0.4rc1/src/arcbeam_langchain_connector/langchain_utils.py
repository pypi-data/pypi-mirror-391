from typing import Any, Dict, List, Literal, Optional, Union, cast

import pydantic
from langchain_core.messages import (
    AIMessage,
    BaseMessage,
    ChatMessage,
    FunctionMessage,
    HumanMessage,
    SystemMessage,
    ToolMessage,
)
from langchain_core.outputs import LLMResult


def get_langchain_run_name(serialized: Optional[Dict[str, Any]], **kwargs: Any) -> str:
    """Retrieve the name of a serialized LangChain runnable.

    The prioritization for the determination of the run name is as follows:
    - The value assigned to the "name" key in `kwargs`.
    - The value assigned to the "name" key in `serialized`.
    - The last entry of the value assigned to the "id" key in `serialized`.
    - "<unknown>".

    Args:
        serialized (Optional[Dict[str, Any]]): A dictionary containing the runnable's serialized data.
        **kwargs (Any): Additional keyword arguments, potentially including the 'name' override.

    Returns:
        str: The determined name of the Langchain runnable.
    """
    if "name" in kwargs and kwargs["name"] is not None:
        return str(kwargs["name"])

    if serialized is None:
        return "<unknown>"

    try:
        return str(serialized["name"])
    except (KeyError, TypeError):
        pass

    try:
        return str(serialized["id"][-1])
    except (KeyError, TypeError):
        pass

    return "<unknown>"


def _extract_model_name(
    serialized: Optional[Dict[str, Any]],
    **kwargs: Any,
) -> Optional[str]:
    """Extracts the model name from the serialized or kwargs object. This is used to get the model names for Langfuse."""
    # In this function we return on the first match, so the order of operations is important

    # First, extract known models where we know the model name aka id
    # Extract the model name from the provided path (aray) in the serialized or kwargs object
    models_by_id = [
        ("ChatGoogleGenerativeAI", ["kwargs", "model"], "serialized"),
        ("ChatMistralAI", ["kwargs", "model"], "serialized"),
        ("ChatVertexAi", ["kwargs", "model_name"], "serialized"),
        ("ChatVertexAI", ["kwargs", "model_name"], "serialized"),
        ("OpenAI", ["invocation_params", "model_name"], "kwargs"),
        ("ChatOpenAI", ["invocation_params", "model_name"], "kwargs"),
        ("AzureChatOpenAI", ["invocation_params", "model"], "kwargs"),
        ("AzureChatOpenAI", ["invocation_params", "model_name"], "kwargs"),
        (
            "AzureChatOpenAI",
            ["invocation_params", "azure_deployment"],
            "kwargs",
        ),
        ("HuggingFacePipeline", ["invocation_params", "model_id"], "kwargs"),
        ("BedrockChat", ["kwargs", "model_id"], "serialized"),
        ("Bedrock", ["kwargs", "model_id"], "serialized"),
        ("BedrockLLM", ["kwargs", "model_id"], "serialized"),
        ("ChatBedrock", ["kwargs", "model_id"], "serialized"),
        ("LlamaCpp", ["invocation_params", "model_path"], "kwargs"),
        ("WatsonxLLM", ["invocation_params", "model_id"], "kwargs"),
    ]

    for model_name, keys, select_from in models_by_id:
        model = _extract_model_by_path_for_id(
            model_name,
            serialized,
            kwargs,
            keys,
            cast(Literal["serialized", "kwargs"], select_from),
        )
        if model:
            return model

    # Second, we match AzureOpenAI as we need to extract the model name, fdeployment version and deployment name
    if serialized:
        serialized_id = serialized.get("id")
        if (
            serialized_id
            and isinstance(serialized_id, list)
            and len(serialized_id) > 0
            and serialized_id[-1] == "AzureOpenAI"
        ):
            invocation_params = kwargs.get("invocation_params")
            if invocation_params and isinstance(invocation_params, dict):
                if invocation_params.get("model"):
                    return str(invocation_params.get("model"))

                if invocation_params.get("model_name"):
                    return str(invocation_params.get("model_name"))

            deployment_name = None
            deployment_version = None

            serialized_kwargs = serialized.get("kwargs")
            if serialized_kwargs and isinstance(serialized_kwargs, dict):
                if serialized_kwargs.get("openai_api_version"):
                    deployment_version = serialized_kwargs.get("deployment_version")

                if serialized_kwargs.get("deployment_name"):
                    deployment_name = serialized_kwargs.get("deployment_name")

            if not isinstance(deployment_name, str):
                return None

            if not isinstance(deployment_version, str):
                return deployment_name

            return (
                deployment_name + "-" + deployment_version
                if deployment_version not in deployment_name
                else deployment_name
            )

    # Third, for some models, we are unable to extract the model by a path in an object. Langfuse provides us with a string representation of the model pbjects
    # We use regex to extract the model from the repr string
    # models_by_pattern = [
    #     ("Anthropic", "model", "anthropic"),
    #     ("ChatAnthropic", "model", None),
    #     ("ChatTongyi", "model_name", None),
    #     ("ChatCohere", "model", None),
    #     ("Cohere", "model", None),
    #     ("HuggingFaceHub", "model", None),
    #     ("ChatAnyscale", "model_name", None),
    #     ("TextGen", "model", "text-gen"),
    #     ("Ollama", "model", None),
    #     ("OllamaLLM", "model", None),
    #     ("ChatOllama", "model", None),
    #     ("ChatFireworks", "model", None),
    #     ("ChatPerplexity", "model", None),
    #     ("VLLM", "model", None),
    #     ("Xinference", "model_uid", None),
    #     ("ChatOCIGenAI", "model_id", None),
    #     ("DeepInfra", "model_id", None),
    # ]

    # for model_name, pattern, default in models_by_pattern:
    #     model = _extract_model_from_repr_by_pattern(model_name, serialized, pattern, default)
    #     if model:
    #         return model

    # Finally, we try to extract the most likely paths as a catch all
    random_paths = [
        ["kwargs", "model_name"],
        ["kwargs", "model"],
        ["invocation_params", "model_name"],
        ["invocation_params", "model"],
    ]
    for select in ["kwargs", "serialized"]:
        for path in random_paths:
            model = _extract_model_by_path(
                serialized,
                kwargs,
                path,
                cast(Literal["serialized", "kwargs"], select),
            )
            if model:
                return str(model)

    return None


def _extract_model_by_path_for_id(
    id: str,
    serialized: Optional[Dict[str, Any]],
    kwargs: Dict[str, Any],
    keys: List[str],
    select_from: Literal["serialized", "kwargs"],
) -> Optional[str]:
    if serialized is None and select_from == "serialized":
        return None

    if serialized:
        serialized_id = serialized.get("id")
        if serialized_id and isinstance(serialized_id, list) and len(serialized_id) > 0 and serialized_id[-1] == id:
            result = _extract_model_by_path(serialized, kwargs, keys, select_from)
            return str(result) if result is not None else None

    return None


def _extract_model_by_path(
    serialized: Optional[Dict[str, Any]],
    kwargs: dict,
    keys: List[str],
    select_from: Literal["serialized", "kwargs"],
) -> Optional[str]:
    if serialized is None and select_from == "serialized":
        return None

    current_obj = kwargs if select_from == "kwargs" else serialized

    for key in keys:
        if current_obj and isinstance(current_obj, dict):
            current_obj = current_obj.get(key)
        else:
            return None
        if not current_obj:
            return None

    return str(current_obj) if current_obj else None


def _parse_usage(response: LLMResult) -> Any:
    # langchain-anthropic uses the usage field
    llm_usage_keys = ["token_usage", "usage"]
    llm_usage = None
    if response.llm_output is not None:
        for key in llm_usage_keys:
            if key in response.llm_output and response.llm_output[key]:
                llm_usage = _parse_usage_model(response.llm_output[key])
                break

    if hasattr(response, "generations"):
        for generation in response.generations:
            for generation_chunk in generation:
                if generation_chunk.generation_info and ("usage_metadata" in generation_chunk.generation_info):
                    llm_usage = _parse_usage_model(generation_chunk.generation_info["usage_metadata"])

                    if llm_usage is not None:
                        break

                message_chunk = getattr(generation_chunk, "message", {})
                response_metadata = getattr(message_chunk, "response_metadata", {})

                chunk_usage = (
                    (
                        response_metadata.get("usage", None)  # for Bedrock-Anthropic
                        if isinstance(response_metadata, dict)
                        else None
                    )
                    or (
                        response_metadata.get("amazon-bedrock-invocationMetrics", None)  # for Bedrock-Titan
                        if isinstance(response_metadata, dict)
                        else None
                    )
                    or getattr(message_chunk, "usage_metadata", None)  # for Ollama
                )

                if chunk_usage:
                    llm_usage = _parse_usage_model(chunk_usage)
                    break

    return llm_usage


def _parse_usage_model(usage: Union[pydantic.BaseModel, dict]) -> Any:
    # maintains a list of key translations. For each key, the usage model is checked
    # and a new object will be created with the new key if the key exists in the usage model
    # All non matched keys will remain on the object.

    if hasattr(usage, "__dict__"):
        usage = usage.__dict__

    conversion_list = [
        # https://pypi.org/project/langchain-anthropic/ (works also for Bedrock-Anthropic)
        ("input_tokens", "input"),
        ("output_tokens", "output"),
        ("total_tokens", "total"),
        # ChatBedrock API follows a separate format compared to ChatBedrockConverse API
        ("prompt_tokens", "input"),
        ("completion_tokens", "output"),
        # https://cloud.google.com/vertex-ai/generative-ai/docs/multimodal/get-token-count
        ("prompt_token_count", "input"),
        ("candidates_token_count", "output"),
        ("total_token_count", "total"),
        # Bedrock: https://docs.aws.amazon.com/bedrock/latest/userguide/monitoring-cw.html#runtime-cloudwatch-metrics
        ("inputTokenCount", "input"),
        ("outputTokenCount", "output"),
        ("totalTokenCount", "total"),
        # langchain-ibm https://pypi.org/project/langchain-ibm/
        ("input_token_count", "input"),
        ("generated_token_count", "output"),
    ]

    usage_model = cast(Dict, usage.copy())  # Copy all existing key-value pairs

    # Skip OpenAI usage types as they are handled server side
    if (
        all(
            openai_key in usage_model
            for openai_key in [
                "prompt_tokens",
                "completion_tokens",
                "total_tokens",
                "prompt_tokens_details",
                "completion_tokens_details",
            ]
        )
        and len(usage_model.keys()) == 5
    ) or (
        all(
            openai_key in usage_model
            for openai_key in [
                "prompt_tokens",
                "completion_tokens",
                "total_tokens",
            ]
        )
        and len(usage_model.keys()) == 3
    ):
        return usage_model

    for model_key, langfuse_key in conversion_list:
        if model_key in usage_model:
            captured_count = usage_model.pop(model_key)
            final_count = (
                sum(captured_count) if isinstance(captured_count, list) else captured_count
            )  # For Bedrock, the token count is a list when streamed

            usage_model[langfuse_key] = final_count  # Translate key and keep the value

    if isinstance(usage_model, dict):
        if "input_token_details" in usage_model:
            input_token_details = usage_model.pop("input_token_details", {})

            for key, value in input_token_details.items():
                usage_model[f"input_{key}"] = value

                if "input" in usage_model:
                    usage_model["input"] = max(0, usage_model["input"] - value)

        if "output_token_details" in usage_model:
            output_token_details = usage_model.pop("output_token_details", {})

            for key, value in output_token_details.items():
                usage_model[f"output_{key}"] = value

                if "output" in usage_model:
                    usage_model["output"] = max(0, usage_model["output"] - value)

        # Vertex AI
        if "prompt_tokens_details" in usage_model and isinstance(usage_model["prompt_tokens_details"], list):
            prompt_tokens_details = usage_model.pop("prompt_tokens_details")

            for item in prompt_tokens_details:
                if isinstance(item, dict) and "modality" in item and "token_count" in item:
                    value = item["token_count"]
                    usage_model[f"input_modality_{item['modality']}"] = value

                    if "input" in usage_model:
                        usage_model["input"] = max(0, usage_model["input"] - value)

        # Vertex AI
        if "candidates_tokens_details" in usage_model and isinstance(usage_model["candidates_tokens_details"], list):
            candidates_tokens_details = usage_model.pop("candidates_tokens_details")

            for item in candidates_tokens_details:
                if isinstance(item, dict) and "modality" in item and "token_count" in item:
                    value = item["token_count"]
                    usage_model[f"output_modality_{item['modality']}"] = value

                    if "output" in usage_model:
                        usage_model["output"] = max(0, usage_model["output"] - value)

        # Vertex AI
        if "cache_tokens_details" in usage_model and isinstance(usage_model["cache_tokens_details"], list):
            cache_tokens_details = usage_model.pop("cache_tokens_details")

            for item in cache_tokens_details:
                if isinstance(item, dict) and "modality" in item and "token_count" in item:
                    value = item["token_count"]
                    usage_model[f"cached_modality_{item['modality']}"] = value

                    if "input" in usage_model:
                        usage_model["input"] = max(0, usage_model["input"] - value)

    usage_model = {k: v for k, v in usage_model.items() if isinstance(v, int)}

    return usage_model if usage_model else None


def _extract_raw_response(last_response: Any) -> Any:
    """Extract the response from the last response of the LLM call."""
    # We return the text of the response if not empty
    if last_response.text is not None and last_response.text.strip() != "":
        return last_response.text.strip()
    elif hasattr(last_response, "message"):
        # Additional kwargs contains the response in case of tool usage
        return last_response.message.additional_kwargs
    else:
        # Not tool usage, some LLM responses can be simply empty
        return ""


def _convert_message_to_dict(message: BaseMessage) -> Dict[str, Any]:
    # assistant message
    if isinstance(message, HumanMessage):
        message_dict: Dict[str, Any] = {
            "role": "user",
            "content": message.content,
        }
    elif isinstance(message, AIMessage):
        message_dict = {"role": "assistant", "content": message.content}

        if hasattr(message, "tool_calls") and message.tool_calls is not None and len(message.tool_calls) > 0:
            message_dict["tool_calls"] = message.tool_calls

    elif isinstance(message, SystemMessage):
        message_dict = {"role": "system", "content": message.content}
    elif isinstance(message, ToolMessage):
        message_dict = {
            "role": "tool",
            "content": message.content,
            "tool_call_id": message.tool_call_id,
        }
    elif isinstance(message, FunctionMessage):
        message_dict = {"role": "function", "content": message.content}
    elif isinstance(message, ChatMessage):
        message_dict = {"role": message.role, "content": message.content}
    else:
        raise ValueError(f"Got unknown type {message}")
    if "name" in message.additional_kwargs:
        message_dict["name"] = message.additional_kwargs["name"]

    if message.additional_kwargs:
        message_dict["additional_kwargs"] = message.additional_kwargs  # type: ignore

    return message_dict
