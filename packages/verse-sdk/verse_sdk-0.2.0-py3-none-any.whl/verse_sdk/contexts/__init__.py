from __future__ import annotations

from .base import BaseContext
from .generation import GenerationContext
from .span import SpanContext
from .trace import TraceContext
from .types import (
    CompletionChoice,
    ContextMetadata,
    ContextType,
    EventMetadata,
    GenerationMessage,
    GenerationUsage,
    ObservationType,
    OperationType,
    Score,
)
from .utils import create_span_in_existing_trace, get_current_context

get_current_generation_context = get_current_context(GenerationContext)
get_current_span_context = get_current_context(SpanContext)
get_current_trace_context = get_current_context(TraceContext)


__all__ = [
    "BaseContext",
    "CompletionChoice",
    "ContextMetadata",
    "ContextType",
    "EventMetadata",
    "GenerationContext",
    "GenerationMessage",
    "GenerationUsage",
    "ObservationType",
    "OperationType",
    "Score",
    "SpanContext",
    "TraceContext",
    "create_span_in_existing_trace",
    "get_current_generation_context",
    "get_current_span_context",
    "get_current_trace_context",
]
