from unittest.mock import patch

import pytest
from opentelemetry import trace as otel_trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SpanExporter, SpanExportResult

from verse_sdk import VerseConfig, verse


class InMemorySpanExporter(SpanExporter):
    def __init__(self):
        self.spans = []

    def export(self, spans):
        self.spans.extend(spans)
        return SpanExportResult.SUCCESS

    def shutdown(self):
        pass

    def get_finished_spans(self):
        return self.spans


def get_spans_from_exporter(exporter: InMemorySpanExporter) -> list[dict]:
    spans = []
    for span in exporter.get_finished_spans():
        span_dict = {
            "name": span.name,
            "attributes": dict(span.attributes) if span.attributes else {},
            "context": {
                "trace_id": format(span.context.trace_id, "032x"),
                "span_id": format(span.context.span_id, "016x"),
            },
        }
        spans.append(span_dict)
    return spans


def force_flush():
    provider = otel_trace.get_tracer_provider()
    if isinstance(provider, TracerProvider):
        provider.force_flush()


@pytest.fixture(autouse=True)
def reset_sdk():
    yield
    verse._initialized = False
    verse._sdk = None
    verse._tracer = None
    provider = otel_trace.get_tracer_provider()
    if isinstance(provider, TracerProvider):
        provider.shutdown()
    otel_trace._TRACER_PROVIDER = None
    otel_trace._TRACER_PROVIDER_SET_ONCE._done = False


@patch("verse_sdk.exporters.verse.exporter.HTTPTraceExporter")
def test_context_managers(mock_http_exporter_class):
    memory_exporter = InMemorySpanExporter()
    mock_http_exporter_class.return_value = memory_exporter

    verse.init(
        app_name="test_context_managers",
        exporters=[
            verse.exporters.verse(
                VerseConfig(
                    project_id="test-project",
                    api_key="test-api-key",
                    host="test-host",
                )
            )
        ],
    )

    with verse.trace(name="test_trace") as trace:
        trace.input("test_input")
        trace.output("test_output")

        with verse.span(name="test_span") as span:
            span.input("test_span_input")
            span.output("test_span_output")

            with verse.generation(name="test_generation") as generation:
                generation.model("test_model")
                generation.input("test_generation_input")
                generation.output("test_generation_output")

    force_flush()

    spans = get_spans_from_exporter(memory_exporter)
    assert len(spans) == 3

    assert spans[0]["name"] == "test_generation"
    assert spans[0]["attributes"]["gen_ai.request.model"] == "test_model"
    assert spans[0]["attributes"]["gen_ai.prompt"] == "test_generation_input"
    trace_id = spans[0]["context"]["trace_id"]

    assert spans[1]["name"] == "test_span"
    assert spans[1]["context"]["trace_id"] == trace_id
    assert spans[1]["attributes"]["input"] == "test_span_input"
    assert spans[1]["attributes"]["output"] == "test_span_output"

    assert spans[2]["name"] == "test_trace"
    assert spans[2]["context"]["trace_id"] == trace_id
    assert spans[2]["attributes"]["input"] == "test_input"
    assert spans[2]["attributes"]["output"] == "test_output"


@patch("verse_sdk.exporters.verse.exporter.HTTPTraceExporter")
def test_session_and_project_propagation(mock_http_exporter_class):
    memory_exporter = InMemorySpanExporter()
    mock_http_exporter_class.return_value = memory_exporter

    verse.init(
        app_name="test_context_managers",
        exporters=[
            verse.exporters.verse(
                VerseConfig(
                    api_key="test-api-key",
                    host="test-host",
                    project_id="test-project",
                )
            )
        ],
    )

    with verse.trace(
        name="parent_trace",
        session_id="test-session-123",
    ) as trace:
        trace.input("parent_input")

        with verse.span(name="child_span") as span:
            span.input("child_span_input")

            with verse.generation(name="child_generation") as generation:
                generation.model("test_model")
                generation.input("child_generation_input")

    force_flush()

    spans = get_spans_from_exporter(memory_exporter)
    assert len(spans) == 3

    assert spans[0]["name"] == "child_generation"
    assert spans[0]["attributes"]["session.id"] == "test-session-123"
    assert spans[0]["attributes"]["project.id"] == "test-project"

    assert spans[1]["name"] == "child_span"
    assert spans[1]["attributes"]["session.id"] == "test-session-123"
    assert spans[1]["attributes"]["project.id"] == "test-project"

    assert spans[2]["name"] == "parent_trace"
    assert spans[2]["attributes"]["session.id"] == "test-session-123"
    assert spans[2]["attributes"]["project.id"] == "test-project"
