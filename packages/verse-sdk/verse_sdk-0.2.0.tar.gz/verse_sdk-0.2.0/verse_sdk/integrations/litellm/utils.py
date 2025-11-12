import logging
from typing import Any

from opentelemetry.trace import Span

from ...contexts import CompletionChoice, GenerationUsage, create_span_in_existing_trace


def calculate_total_tokens(
    prompt_tokens: int | None, completion_tokens: int | None
) -> int | None:
    """Calculate the total tokens."""
    if prompt_tokens is not None or completion_tokens is not None:
        return (prompt_tokens or 0) + (completion_tokens or 0)
    return None


def get_completition_choices(data: Any) -> list[CompletionChoice]:
    """Get the completion choices from the response."""

    choices = []
    if hasattr(data, "choices"):
        choices = data.choices
    elif isinstance(data, dict) and "choices" in data:
        choices = data["choices"]

    return choices if len(choices) > 0 else []


def get_finish_reason(response_obj: Any) -> str | None:
    """Trace response metadata like model and ID."""
    if getattr(response_obj, "choices", None):
        fr = getattr(response_obj.choices[0], "finish_reason", None)
        if fr:
            return fr

    return None


def get_operation_type(messages: list, kwargs: dict) -> str:
    """Determine the operation type based on request parameters."""
    try:
        if kwargs.get("litellm_params", {}).get("api_base", "").endswith("/embeddings"):
            return "embedding"

        return "chat" if messages else "completion"
    except Exception as e:
        logging.warning("Error determining operation type from Litellm", exc_info=e)
        return "completion"


def get_stream_text(response_obj: Any) -> str:
    """Get the text from the response."""
    chunk = getattr(response_obj, "choices", None)
    if not chunk:
        return ""

    c = chunk[0]
    return (
        getattr(getattr(c, "delta", None), "content", None)
        or getattr(c, "text", None)
        or ""
    )


def get_trace_metadata(kwargs: dict) -> dict[str, str | None]:
    """
    Extract trace ID and parent observation ID from LiteLLM metadata.
    Useful when using Router().completion() or parallel processing.
    """
    try:
        litellm_params = kwargs.get("litellm_params", {}).get("metadata", {})
        parent_observation_id = litellm_params.get("parent_observation_id", None)
        trace_id = litellm_params.get("trace_id", None)
        return {
            "parent_observation_id": parent_observation_id,
            "trace_id": trace_id,
        }
    except Exception:
        return {
            "parent_observation_id": None,
            "trace_id": None,
        }


def get_trace_span_from_metadata(kwargs: dict) -> Span | None:
    """
    Generate parent trace from metadata.
    Needed when the LLM call is outside of the context manager.
    """
    try:
        trace_metadata = get_trace_metadata(kwargs)
        if (
            trace_metadata
            and trace_metadata.get("trace_id")
            and trace_metadata.get("parent_observation_id")
        ):
            return create_span_in_existing_trace(
                trace_metadata.get("trace_id"),
                trace_metadata.get("parent_observation_id"),
            )
    except Exception:
        return None


def get_usage(kwargs: dict) -> GenerationUsage:
    """Get the usage for the request."""
    try:
        optional = kwargs.get("optional_params", {})
        return {
            "max_tokens": kwargs.get("max_tokens", optional.get("max_tokens")),
            "temperature": kwargs.get("temperature", optional.get("temperature")),
            "top_p": kwargs.get("top_p", optional.get("top_p")),
            "stream": kwargs.get("stream", optional.get("stream")),
        }
    except Exception as e:
        logging.warning("Error getting usage from Litellm", exc_info=e)
        return {}


def get_usage_from_response(response_obj: Any) -> GenerationUsage:
    """Get the usage from the response."""
    try:
        usage = getattr(response_obj, "usage", None)

        usage_output = {
            "prompt_tokens": getattr(usage, "prompt_tokens", None),
            "completion_tokens": getattr(usage, "completion_tokens", None),
        }

        usage_output["total_tokens"] = getattr(
            usage,
            "total_tokens",
            calculate_total_tokens(
                usage_output["prompt_tokens"],
                usage_output["completion_tokens"],
            ),
        )

        return usage_output

    except Exception as e:
        logging.warning("Error getting usage from response", exc_info=e)
        return {}
