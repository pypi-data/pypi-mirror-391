import json
import logging
from typing import Any, Tuple

from pydantic_ai import RunContext, RunUsage

from ...contexts import CompletionChoice, GenerationMessage, GenerationUsage
from ...utils import get
from .constants import VENDOR_ANTHROPIC, VENDOR_OPENAI, VENDOR_UNKNOWN


def calculate_total_tokens(usage: RunUsage) -> int | None:
    """Calculate the total tokens."""
    return (
        usage.input_tokens + usage.output_tokens
        if usage.input_tokens and usage.output_tokens
        else None
    )


def get_finish_reason(ctx: RunContext) -> str:
    """Get the finish reason from RunContext."""
    if hasattr(ctx, "messages") and ctx.messages:
        return get(ctx.messages[-1], "finish_reason", "")

    return ""


def get_generation_messages(
    ctx: RunContext,
) -> tuple[list[GenerationMessage], list[CompletionChoice]]:
    """
    Convert RunContext messages into prompt/completion payloads.

    Prompts capture system/user/tool responses. Completions capture assistant output.
    """
    prompts: list[GenerationMessage] = []
    completions: list[CompletionChoice] = []

    if not hasattr(ctx, "messages") or not ctx.messages:
        return prompts, completions

    for message in ctx.messages:
        if not hasattr(message, "parts"):
            continue

        assistant_content_parts = []
        assistant_tool_calls = []

        for part in message.parts:
            part_type = part.__class__.__name__

            if part_type == "SystemPromptPart":
                prompts.append(
                    GenerationMessage(
                        content=part.content,
                        function_call=None,
                        name=None,
                        role="system",
                        tool_calls=None,
                    )
                )
            elif part_type == "UserPromptPart":
                prompts.append(
                    GenerationMessage(
                        content=part.content,
                        function_call=None,
                        name=None,
                        role="user",
                        tool_calls=None,
                    )
                )
            elif part_type == "ToolReturnPart":
                prompts.append(
                    GenerationMessage(
                        content=json.dumps(part.content),
                        function_call=None,
                        name=None,
                        role="tool",
                        tool_calls=None,
                        id=get(part, "tool_call_id"),
                    )
                )
            elif part_type == "TextPart":
                assistant_content_parts.append(part.content)
            elif part_type == "ToolCallPart":
                assistant_tool_calls.append(
                    {
                        "function": {
                            "arguments": part.args,
                            "name": part.tool_name,
                        },
                        "id": part.tool_call_id,
                        "type": "function",
                    }
                )

        if assistant_tool_calls or assistant_content_parts:
            message_content = (
                " ".join(assistant_content_parts) if assistant_content_parts else ""
            )
            completions.append(
                CompletionChoice(
                    message={
                        "content": message_content,
                        "function_call": None,
                        "name": None,
                        "role": "assistant",
                        "tool_calls": assistant_tool_calls or None,
                    },
                    delta=None,
                    text=None,
                )
            )

    return prompts, completions


def get_llm_info_from_model(model: Any) -> Tuple[str, str]:
    """Get the vendor and model name."""
    try:
        if isinstance(model, get_model_instance(VENDOR_OPENAI)):
            return VENDOR_OPENAI, model.model_name
        if isinstance(model, get_model_instance(VENDOR_ANTHROPIC)):
            return VENDOR_ANTHROPIC, model.model_name

        return VENDOR_UNKNOWN, getattr(model, "model_name", VENDOR_UNKNOWN)
    except Exception:
        return VENDOR_UNKNOWN, VENDOR_UNKNOWN


def get_model_instance(model_name: str) -> Any:
    """Lazy load the vendor model by name."""
    try:
        if model_name.startswith(VENDOR_OPENAI):
            from pydantic_ai.models.openai import OpenAIChatModel

            return OpenAIChatModel
        if model_name.startswith(VENDOR_ANTHROPIC):
            from pydantic_ai.models.anthropic import AnthropicChatModel

            return AnthropicChatModel

        return None
    except Exception:
        logging.warning(f"Error loading model {model_name}", exc_info=True)
        return None


def get_operation_type(ctx: RunContext) -> str:
    """Get the operation type based on the messages."""
    if hasattr(ctx, "messages") and ctx.messages:
        return "chat"
    return "completion"


def get_usage(usage: RunUsage) -> GenerationUsage:
    """Get the usage from RunContext."""
    return GenerationUsage(
        completion_tokens=usage.output_tokens,
        input_tokens=usage.input_tokens,
        output_tokens=usage.output_tokens,
        prompt_tokens=usage.input_tokens,
        tool_calls=usage.tool_calls,
        total_tokens=calculate_total_tokens(usage),
    )
