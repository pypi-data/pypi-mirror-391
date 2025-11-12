import asyncio
import types
from unittest.mock import Mock

from verse_sdk.integrations.pydantic_ai.patch import patch_pydantic_ai


class DummySpan:
    def __init__(self):
        self.ended = False

    def end(self):
        self.ended = True


class DummyGenerationContext:
    def __init__(self):
        self.span = DummySpan()
        self.captured_messages = None
        self.captured_completions = None
        self.captured_reason = None

    def messages(self, messages):
        self.captured_messages = messages

    def completions(self, completions):
        self.captured_completions = completions

    def reason(self, reason):
        self.captured_reason = reason


def make_part(part_type: str, **attrs):
    part_cls = type(part_type, (), {})
    part = part_cls()
    for key, value in attrs.items():
        setattr(part, key, value)
    return part


def test_patch_pydantic_ai_records_messages_and_completions(monkeypatch):
    """
    Ensure patched Agent propagates prompts/completions into the Verse generation span.
    """

    async def run_test():
        captured_kwargs = {}
        generation_ctx = DummyGenerationContext()
        sdk = Mock()
        sdk.create_generation.return_value = generation_ctx

        async def fake_events():
            if False:  # pragma: no cover - required for async generator syntax
                yield None

        def make_message(parts, finish_reason=""):
            return types.SimpleNamespace(parts=parts, finish_reason=finish_reason)

        ctx_messages = [
            make_message([make_part("SystemPromptPart", content="You are helpful")]),
            make_message([make_part("UserPromptPart", content="Hello")]),
            make_message(
                [make_part("TextPart", content="Hi there!")],
                finish_reason="stop",
            ),
        ]

        fake_ctx = types.SimpleNamespace(
            messages=ctx_messages,
            model=types.SimpleNamespace(model_name="test-model"),
            usage=types.SimpleNamespace(
                input_tokens=10,
                output_tokens=5,
                tool_calls=0,
            ),
        )

        class FakeAgent:
            _verse_patched = False

            async def run(self, *args, event_stream_handler=None, **kwargs):
                captured_kwargs["handler"] = event_stream_handler
                captured_kwargs["args"] = args
                captured_kwargs["kwargs"] = kwargs
                if event_stream_handler:
                    await event_stream_handler(fake_ctx, fake_events())
                return "ok"

        monkeypatch.setattr("pydantic_ai.Agent", FakeAgent)

        patch_pydantic_ai(sdk)

        agent = FakeAgent()
        result = await agent.run("ignored")

        assert result == "ok"
        assert sdk.create_generation.call_count == 1

        # prompts captured from system + user messages
        assert generation_ctx.captured_messages is not None
        prompt_roles = [m["role"] for m in generation_ctx.captured_messages]
        assert prompt_roles == ["system", "user"]

        # completions captured from assistant text
        assert generation_ctx.captured_completions is not None
        assert generation_ctx.captured_completions[0]["message"]["role"] == "assistant"
        assert (
            generation_ctx.captured_completions[0]["message"]["content"] == "Hi there!"
        )

        # finish reason propagates
        assert generation_ctx.captured_reason == "stop"
        assert generation_ctx.span.ended is True

    asyncio.run(run_test())
