from __future__ import annotations

import logging
from contextlib import suppress
from contextvars import ContextVar
from typing import Any, ClassVar

from opentelemetry.trace import Status, StatusCode

from ...contexts import GenerationContext
from ...sdk import VerseSDK

_VERSE_LANGCHAIN_HANDLER_VAR: ContextVar[Any] = ContextVar(
    "verse_langchain_handler", default=None
)
_VERSE_LANGCHAIN_HOOK_REGISTERED = False


def configure_langchain(sdk: VerseSDK) -> None:
    """
    Register the Verse handler with LangChain via the configure hook mechanism so
    instrumentation is applied automatically to all chains.
    """
    from langchain_core.callbacks.base import BaseCallbackHandler

    from .utils import (
        get_completions_from_result,
        get_generation_messages_from_chat,
        get_generation_messages_from_prompts,
        get_usage_from_result,
        get_vendor_and_model,
    )

    class VerseLangChainHandler(BaseCallbackHandler):
        """
        Minimal LangChain callback handler that records GenAI metadata.
        """

        current: ClassVar[dict[Any, GenerationContext]] = {}

        def __init__(self, sdk: VerseSDK):
            super().__init__()
            self._sdk = sdk

        def on_chat_model_start(self, serialized: Any, messages, run_id, **kwargs):
            vendor, model = get_vendor_and_model(serialized, **kwargs)
            prompts = get_generation_messages_from_chat(messages)
            ctx = self._sdk.create_generation(
                name="LangChain: Chat",
                model=model,
                messages=prompts,
                vendor=vendor,
            )
            self.current[run_id] = ctx

        def on_chat_model_end(self, result, run_id, **kwargs):
            self._finish_generation(result, run_id)

        def on_chat_model_error(self, error: Exception, run_id, **kwargs):
            self._handle_error(error, run_id)

        def on_llm_start(self, serialized: Any, prompts, run_id, **kwargs):
            vendor, model = get_vendor_and_model(serialized, **kwargs)
            prompt_messages = get_generation_messages_from_prompts(prompts)
            ctx = self._sdk.create_generation(
                name="LangChain: Completion",
                model=model,
                messages=prompt_messages,
                vendor=vendor,
            )
            self.current[run_id] = ctx

        def on_llm_end(self, result, run_id, **kwargs):
            self._finish_generation(result, run_id)

        def on_llm_new_token(self, token: str, run_id, **kwargs):
            ctx = self.current.get(run_id)
            if ctx and token:
                with suppress(Exception):
                    ctx.event("gen_ai.stream.delta", metadata={"content": token[:512]})

        def on_llm_error(self, error: Exception, run_id, **kwargs):
            self._handle_error(error, run_id)

        def on_embedding_start(self, serialized: Any, inputs, run_id, **kwargs):
            vendor, model = get_vendor_and_model(serialized, **kwargs)
            ctx = self._sdk.create_generation(
                name="LangChain: Embedding",
                model=model,
                vendor=vendor,
            )
            self.current[run_id] = ctx

        def on_embedding_end(self, result, run_id, **kwargs):
            ctx = self.current.pop(run_id, None)
            if not ctx:
                return
            try:
                ctx.status(Status(StatusCode.OK))
            except Exception as exc:
                ctx.error(exc)
            finally:
                ctx.span.end()

        def on_embedding_error(self, error: Exception, run_id, **kwargs):
            self._handle_error(error, run_id)

        def _finish_generation(self, result: Any, run_id: Any) -> None:
            ctx = self.current.pop(run_id, None)
            if not ctx:
                return

            try:
                completions, finish_reason, model_used = get_completions_from_result(
                    result
                )

                if completions:
                    ctx.completions(completions)

                if finish_reason:
                    ctx.reason(finish_reason)

                usage = get_usage_from_result(result)
                if any(value is not None for value in usage.values()):
                    ctx.usage(usage)

                if model_used:
                    ctx.model_used(model_used)

                ctx.status(Status(StatusCode.OK))
            except Exception as exc:
                ctx.error(exc)
            finally:
                ctx.span.end()

        def _handle_error(self, error: Exception, run_id: Any) -> None:
            ctx = self.current.pop(run_id, None)
            if not ctx:
                return
            ctx.error(error)
            ctx.span.end()

    handler = getattr(sdk, "_verse_langchain_handler", None)
    if handler is None:
        handler = VerseLangChainHandler(sdk)
        sdk._verse_langchain_handler = handler
    else:
        handler._sdk = sdk

    _VERSE_LANGCHAIN_HANDLER_VAR.set(handler)

    from langchain_core.tracers.context import register_configure_hook

    global _VERSE_LANGCHAIN_HOOK_REGISTERED

    if not _VERSE_LANGCHAIN_HOOK_REGISTERED:
        register_configure_hook(_VERSE_LANGCHAIN_HANDLER_VAR, inheritable=True)
        _VERSE_LANGCHAIN_HOOK_REGISTERED = True

    logging.info("LangChain handler registered globally via configure hook")
