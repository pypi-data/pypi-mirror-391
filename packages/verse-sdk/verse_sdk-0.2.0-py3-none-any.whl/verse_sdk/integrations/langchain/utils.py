from __future__ import annotations

import logging
from typing import Any, Iterable

from ...contexts import CompletionChoice, GenerationMessage, GenerationUsage
from ...utils import get

# LangChain-specific vendor list for detecting LLM providers from serialized metadata.
# When LangChain serializes components, it uses an "id" field with a list structure:
# e.g., {"id": ["langchain", "openai", "chat"]} becomes "langchain/openai/chat"
# We then check if any of these vendor names appear in that serialized string.
# This approach is specific to LangChain's metadata format and differs from how
# other integrations (Pydantic AI, LiteLLM) handle vendor identification.
KNOWN_VENDORS = (
    "openai",
    "anthropic",
    "google",
    "groq",
    "mistral",
    "ollama",
    "cohere",
)


def _serialized_to_str(serialized: Any) -> str:
    if isinstance(serialized, dict) and "id" in serialized:
        identifier = serialized["id"]
        if isinstance(identifier, (list, tuple)):
            return "/".join(str(part) for part in identifier).lower()
        return str(identifier).lower()
    return str(serialized).lower()


def get_vendor_and_model(serialized: Any, **kwargs: Any) -> tuple[str, str]:
    """
    Best-effort vendor/model extraction based on LangChain metadata.

    LangChain serializes components with an "id" field containing a list:
    - {"id": ["langchain", "openai", "chat"]} -> detects "openai"
    - {"id": ["langchain", "anthropic", "claude"]} -> detects "anthropic"
    - {"id": ["langchain", "custom", "llm"]} -> returns "unknown"

    The detection works by converting the list to a string (e.g., "langchain/openai/chat")
    and checking if any KNOWN_VENDORS appear as substrings.
    """
    serialized_str = _serialized_to_str(serialized)
    vendor = next((v for v in KNOWN_VENDORS if v in serialized_str), "unknown")

    if vendor == "unknown" and serialized_str:
        logging.debug(
            f"Could not identify LangChain vendor from serialized metadata: {serialized_str}. "
        )

    invocation_params = kwargs.get("invocation_params", {}) or {}
    model = (
        get(invocation_params, "model")
        or get(invocation_params, "model_name")
        or get(kwargs, "model")
        or get(kwargs, "model_name")
        or ""
    )

    return vendor, model or "unknown"


def _role_from_message_obj(message: Any) -> str:
    explicit_role = getattr(message, "role", None) or getattr(message, "type", None)
    if explicit_role:
        role = str(explicit_role).lower()
        if role in {"assistant", "ai"}:
            return "assistant"
        if role in {"human", "user"}:
            return "user"
        if role in {"system"}:
            return "system"
        if role in {"tool", "function"}:
            return "tool"
        return role

    name = message.__class__.__name__.lower()
    if "system" in name:
        return "system"
    if "human" in name or "user" in name:
        return "user"
    if "ai" in name or "assistant" in name:
        return "assistant"
    if "tool" in name or "function" in name:
        return "tool"
    return "user"


def _text_from_content(content: Any) -> str:
    if isinstance(content, list):
        parts: list[str] = []
        for part in content:
            text = get(part, "text") or get(part, "content")
            parts.append(str(text) if text is not None else str(part))
        return "\n".join(parts)
    return str(content) if content is not None else ""


def get_generation_messages_from_chat(
    messages_batches: Iterable[Iterable[Any]],
) -> list[GenerationMessage]:
    prompts: list[GenerationMessage] = []
    for batch in messages_batches or []:
        for message in batch or []:
            prompts.append(
                GenerationMessage(
                    role=_role_from_message_obj(message),
                    content=_text_from_content(get(message, "content")),
                    function_call=None,
                    name=None,
                    tool_calls=None,
                )
            )

    return prompts


def get_generation_messages_from_prompts(
    prompts: Iterable[str],
) -> list[GenerationMessage]:
    prompt_messages: list[GenerationMessage] = []
    for prompt in prompts or []:
        prompt_messages.append(
            GenerationMessage(
                role="user",
                content=str(prompt),
                function_call=None,
                name=None,
                tool_calls=None,
            )
        )
    return prompt_messages


def _tool_calls_from_message(message: Any) -> list[dict] | None:
    tool_calls = getattr(message, "tool_calls", None)
    if not tool_calls:
        additional = getattr(message, "additional_kwargs", None)
        if isinstance(additional, dict):
            tool_calls = additional.get("tool_calls")

    if isinstance(tool_calls, list) and tool_calls:
        return tool_calls
    return None


def _content_from_generation(generation: Any) -> str:
    """Extract text content from a generation object (handles both text and chat formats)."""
    if hasattr(generation, "text") and generation.text is not None:
        return str(generation.text)

    message = getattr(generation, "message", None)
    if message is not None:
        return _text_from_content(get(message, "content"))

    return ""


def _finish_reason_from_generation(generation: Any) -> str | None:
    generation_info = getattr(generation, "generation_info", None)
    if isinstance(generation_info, dict) and generation_info.get("finish_reason"):
        return str(generation_info["finish_reason"])

    message = getattr(generation, "message", None)
    response_metadata = getattr(message, "response_metadata", None)
    if isinstance(response_metadata, dict) and response_metadata.get("finish_reason"):
        return str(response_metadata["finish_reason"])

    return None


def get_completions_from_result(
    result: Any,
) -> tuple[list[CompletionChoice], str | None, str | None]:
    completions: list[CompletionChoice] = []
    finish_reason: str | None = None
    model_used: str | None = None

    generations = getattr(result, "generations", None) or []
    flat_generations: list[Any] = []
    for generation in generations:
        if isinstance(generation, (list, tuple)):
            flat_generations.extend(generation)
        else:
            flat_generations.append(generation)

    for generation in flat_generations:
        message = getattr(generation, "message", None)

        if message is not None:
            completions.append(
                CompletionChoice(
                    message={
                        "role": "assistant",
                        "content": _text_from_content(get(message, "content")),
                        "function_call": None,
                        "name": None,
                        "tool_calls": _tool_calls_from_message(message),
                    },
                    delta=None,
                    text=None,
                )
            )
        else:
            completions.append(
                CompletionChoice(
                    message=None,
                    delta=None,
                    text=_content_from_generation(generation),
                )
            )

        finish_reason = _finish_reason_from_generation(generation) or finish_reason

    llm_output = getattr(result, "llm_output", None)
    if isinstance(llm_output, dict):
        model_used = (
            llm_output.get("model_name")
            or llm_output.get("model")
            or llm_output.get("model_id")
        )

    return completions, finish_reason, model_used


def get_usage_from_result(result: Any) -> GenerationUsage:
    llm_output = getattr(result, "llm_output", None)
    token_usage = None
    if isinstance(llm_output, dict):
        token_usage = llm_output.get("token_usage") or llm_output.get("usage")
    # Fallback: some LC wrappers surface usage here
    token_usage = token_usage or getattr(result, "usage_metadata", None)

    if not isinstance(token_usage, dict):
        return GenerationUsage(
            completion_tokens=None,
            input_tokens=None,
            max_tokens=None,
            output_tokens=None,
            prompt_tokens=None,
            stream=None,
            temperature=None,
            tool_calls=None,
            total_tokens=None,
            top_p=None,
        )

    prompt_tokens = token_usage.get("prompt_tokens")
    completion_tokens = token_usage.get("completion_tokens")
    total_tokens = token_usage.get("total_tokens")

    return GenerationUsage(
        completion_tokens=completion_tokens,
        input_tokens=prompt_tokens,
        max_tokens=None,
        output_tokens=completion_tokens,
        prompt_tokens=prompt_tokens,
        stream=None,
        temperature=None,
        tool_calls=None,
        total_tokens=total_tokens
        if total_tokens is not None
        else (
            (prompt_tokens or 0) + (completion_tokens or 0)
            if prompt_tokens is not None or completion_tokens is not None
            else None
        ),
        top_p=None,
    )
