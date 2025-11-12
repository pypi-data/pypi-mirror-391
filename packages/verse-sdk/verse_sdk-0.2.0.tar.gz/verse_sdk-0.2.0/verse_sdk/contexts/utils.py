import logging
from typing import Any, Type

from opentelemetry import trace
from opentelemetry.trace import SpanContext, SpanKind, TraceFlags

from ..utils import get, uses_pydantic_base_model
from .base import BaseContext
from .types import CompletionChoice, CompletionChoiceMessage, GenerationMessage


def create_span_in_existing_trace(trace_id_hex: str, parent_span_id_hex: str):
    """Create a span without using context manager."""
    if not isinstance(trace_id_hex, str):
        trace_id_hex = str(trace_id_hex)
    if not isinstance(parent_span_id_hex, str):
        parent_span_id_hex = str(parent_span_id_hex)

    trace_id_hex = trace_id_hex.replace("0x", "").replace("0X", "")
    parent_span_id_hex = parent_span_id_hex.replace("0x", "").replace("0X", "")

    trace_id = int(trace_id_hex, 16)
    parent_span_id = int(parent_span_id_hex, 16)

    parent_span_context = SpanContext(
        trace_id=trace_id,
        span_id=parent_span_id,
        is_remote=True,
        trace_flags=TraceFlags(0x01),
    )

    parent_span = trace.NonRecordingSpan(parent_span_context)
    ctx = trace.set_span_in_context(parent_span)

    tracer = trace.get_tracer(__name__)
    span = tracer.start_span("llm_generation", context=ctx, kind=SpanKind.INTERNAL)
    return span


def get_choice_message(
    choice: CompletionChoice | None,
) -> CompletionChoiceMessage | None:
    """Get message dict from choice"""
    if uses_pydantic_base_model(choice):
        choice = choice.model_dump()

    if hasattr(choice, "message") and choice.message:
        if uses_pydantic_base_model(choice.message):
            return choice.message.model_dump()
        return choice.message
    elif hasattr(choice, "delta") and choice.delta:
        return choice.delta
    elif isinstance(choice, dict):
        return choice.get("message") or choice.get("delta") or None
    return None


def get_content_from_choice_message(message: CompletionChoiceMessage | None) -> str:
    """Get the content from the choice message"""
    content = get(message, "content")

    if content is None:
        content = ""
    elif not isinstance(content, str):
        content = str(content)

    return content


def get_content_from_generation_message(message: GenerationMessage | None) -> str:
    """Get the content from the generation message."""
    content = get(message, "content")

    if isinstance(content, list):
        text_parts = []
        for part in content:
            text = get(part, "text")
            if text:
                text_parts.append(text)
        content = "\n".join(text_parts)
    elif not isinstance(content, str):
        content = str(content)

    return content


def get_current_context(cls: Type[BaseContext]) -> BaseContext:
    def _get_current_context():
        """Get the current context from the current span"""
        current_span = trace.get_current_span()

        if (
            current_span
            and current_span.get_span_context().is_valid
            and hasattr(current_span, "_attributes")
        ):
            return cls(current_span)
        else:
            logging.error(
                "No valid span found to create context from", current_span=current_span
            )

            raise ValueError("Cannot create context from current span")

    return _get_current_context


def get_function_call(
    message: Any | None,
    default_name: str = "function_call",
) -> tuple[str | None, str | None]:
    """Get function call details from message"""
    func_call = get(message, default_name)
    return (
        (get(func_call, "arguments"), get(func_call, "name"))
        if func_call
        else (None, None)
    )


def get_tool_call_from_choice_message(
    message: CompletionChoiceMessage | None,
) -> list[dict]:
    """Get tools calls from message if available"""
    tool_calls = get(message, "tool_calls", [])
    return tool_calls if isinstance(tool_calls, list) else []


def get_tool_call(
    tool_call: Any | None,
) -> tuple[str | None, str | None]:
    """Get tool call details"""
    return (get(tool_call, "id"), get(tool_call, "type")) if tool_call else (None, None)
