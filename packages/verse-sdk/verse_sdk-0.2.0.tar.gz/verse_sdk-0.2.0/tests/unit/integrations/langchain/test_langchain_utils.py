"""Tests for LangChain integration utilities."""

import types

from verse_sdk.integrations.langchain.utils import (
    get_completions_from_result,
    get_generation_messages_from_chat,
    get_generation_messages_from_prompts,
    get_usage_from_result,
    get_vendor_and_model,
)


def make_chat_message(class_name, content, **extra):
    message_cls = type(class_name, (), {})
    message = message_cls()
    message.content = content
    for key, value in extra.items():
        setattr(message, key, value)
    return message


def make_chat_generation(content, *, tool_calls=None, finish_reason="stop"):
    message = make_chat_message(
        "AIMessage",
        content,
        additional_kwargs={"tool_calls": tool_calls} if tool_calls else {},
        response_metadata={"finish_reason": finish_reason},
    )
    return types.SimpleNamespace(
        message=message,
        generation_info={"finish_reason": finish_reason},
    )


def make_text_generation(text, finish_reason="stop"):
    return types.SimpleNamespace(
        text=text,
        generation_info={"finish_reason": finish_reason},
        message=None,
    )


def make_llm_result(
    generations, *, model_name="gpt-4o", prompt=10, completion=5, total=15
):
    return types.SimpleNamespace(
        generations=generations,
        llm_output={
            "model_name": model_name,
            "token_usage": {
                "prompt_tokens": prompt,
                "completion_tokens": completion,
                "total_tokens": total,
            },
        },
    )


class TestGetVendorAndModel:
    def test_extracts_vendor_from_serialized_id(self):
        vendor, model = get_vendor_and_model(
            {"id": ["langchain", "openai", "chat"]},
            invocation_params={"model": "gpt-4"},
        )
        assert vendor == "openai"
        assert model == "gpt-4"

    def test_returns_unknown_for_unrecognized_vendor(self):
        vendor, model = get_vendor_and_model(
            {"id": ["langchain", "custom", "llm"]},
        )
        assert vendor == "unknown"
        assert model == "unknown"

    def test_extracts_model_from_kwargs(self):
        _vendor, model = get_vendor_and_model(
            {"id": ["langchain", "openai"]}, model="gpt-3.5-turbo"
        )
        assert model == "gpt-3.5-turbo"


class TestGetGenerationMessagesFromChat:
    def test_converts_chat_messages_to_generation_format(self):
        sys_msg = make_chat_message("SystemMessage", "You are helpful")
        user_msg = make_chat_message("HumanMessage", "Hi")

        messages = get_generation_messages_from_chat([[sys_msg, user_msg]])

        assert len(messages) == 2
        assert messages[0]["role"] == "system"
        assert messages[0]["content"] == "You are helpful"
        assert messages[1]["role"] == "user"
        assert messages[1]["content"] == "Hi"

    def test_handles_empty_message_batches(self):
        messages = get_generation_messages_from_chat([])
        assert messages == []

    def test_uses_explicit_role_when_available(self):
        assistant_msg = make_chat_message("ChatMessage", "Hello!", role="assistant")

        messages = get_generation_messages_from_chat([[assistant_msg]])

        assert messages == [
            {
                "role": "assistant",
                "content": "Hello!",
                "function_call": None,
                "name": None,
                "tool_calls": None,
            }
        ]


class TestGetGenerationMessagesFromPrompts:
    def test_converts_prompts_to_user_messages(self):
        messages = get_generation_messages_from_prompts(["prompt1", "prompt2"])

        assert len(messages) == 2
        assert all(m["role"] == "user" for m in messages)
        assert messages[0]["content"] == "prompt1"
        assert messages[1]["content"] == "prompt2"

    def test_handles_empty_prompts(self):
        messages = get_generation_messages_from_prompts([])
        assert messages == []


class TestGetCompletionsFromResult:
    def test_extracts_chat_completions_with_tool_calls(self):
        tool_calls = [{"type": "function", "function": {"name": "weather"}}]
        result = make_llm_result(
            [[make_chat_generation("response", tool_calls=tool_calls)]]
        )

        completions, finish_reason, model_used = get_completions_from_result(result)

        assert len(completions) == 1
        assert completions[0]["message"]["content"] == "response"
        assert completions[0]["message"]["tool_calls"] == tool_calls
        assert finish_reason == "stop"
        assert model_used == "gpt-4o"

    def test_extracts_text_completions(self):
        result = make_llm_result([[make_text_generation("A haiku appears.")]])

        completions, finish_reason, _model_used = get_completions_from_result(result)

        assert len(completions) == 1
        assert completions[0]["text"] == "A haiku appears."
        assert completions[0]["message"] is None
        assert finish_reason == "stop"

    def test_handles_multiple_generations(self):
        result = make_llm_result(
            [[make_text_generation("first"), make_text_generation("second")]]
        )

        completions, _, _ = get_completions_from_result(result)
        assert len(completions) == 2


class TestGetUsageFromResult:
    def test_extracts_token_usage(self):
        result = make_llm_result([[]], prompt=100, completion=50, total=150)
        usage = get_usage_from_result(result)

        assert usage["prompt_tokens"] == 100
        assert usage["completion_tokens"] == 50
        assert usage["total_tokens"] == 150
        assert usage["input_tokens"] == 100
        assert usage["output_tokens"] == 50

    def test_calculates_total_when_missing(self):
        result = types.SimpleNamespace(
            llm_output={
                "token_usage": {
                    "prompt_tokens": 30,
                    "completion_tokens": 20,
                }
            }
        )
        usage = get_usage_from_result(result)
        assert usage["total_tokens"] == 50

    def test_returns_empty_usage_when_no_data(self):
        result = types.SimpleNamespace(llm_output={})
        usage = get_usage_from_result(result)

        assert usage["prompt_tokens"] is None
        assert usage["completion_tokens"] is None
        assert usage["total_tokens"] is None
