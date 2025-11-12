from typing import ClassVar

from opentelemetry.context import Context
from opentelemetry.sdk.trace import ReadableSpan, Span, SpanProcessor


class AttributeProcessor(SpanProcessor):
    _project_id: str
    _propagated_attributes: ClassVar[list[str]] = [
        "session.id",
        "project.id",
        "user.id",
    ]

    def __init__(self, project_id: str):
        """Initialize the processor with span tracking structures."""
        self._active_spans: dict[int, Span] = {}
        self._project_id = project_id
        self._span_cache: dict[int, dict[str, str]] = {}

    def force_flush(self, timeout_millis: int = 30000):
        """Force flush any buffered spans. This processor has no buffer."""
        return True

    def on_end(self, span: ReadableSpan):
        """Called when a span ends. Cache attributes for future children and cleanup."""
        span_id = span.get_span_context().span_id

        if span.attributes:
            attribute_store = {
                attribute: span.attributes[attribute]
                for attribute in self._propagated_attributes
                if attribute in span.attributes
            }
            if attribute_store:
                self._span_cache[span_id] = attribute_store

        self._active_spans.pop(span_id, None)

    def on_start(self, span: Span, parent_context: Context | None = None):
        """Called when a span starts. Propagates attributes from parent and registers span."""
        span_id = span.get_span_context().span_id
        self._active_spans[span_id] = span
        self._inject_project_id(span)

        if not span.parent or not span.parent.is_valid:
            return

        self._propagate_attributes(span, span.parent.span_id)

    def shutdown(self):
        """Called when the tracer provider shuts down. Cleans up all caches."""
        self._active_spans.clear()
        self._span_cache.clear()
        return True

    def _copy_attributes(self, source_attributes: dict, target_span: Span):
        """Copy propagated attributes from parent to child span."""
        for attribute in self._propagated_attributes:
            attribute_value = source_attributes.get(attribute)
            if attribute_value is not None:
                target_span.set_attribute(attribute, attribute_value)

    def _inject_project_id(self, span: Span):
        if self._project_id:
            span.set_attribute("project.id", self._project_id)

    def _propagate_attributes(self, span: Span, parent_span_id: int):
        """Propagate configured attributes from parent to child span."""
        parent_span = self._active_spans.get(parent_span_id)
        if parent_span and hasattr(parent_span, "_attributes"):
            self._copy_attributes(parent_span._attributes, span)
            return

        cached_attributes = self._span_cache.get(parent_span_id)
        if cached_attributes:
            self._copy_attributes(cached_attributes, span)
