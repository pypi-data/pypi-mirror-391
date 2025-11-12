import os

from opentelemetry.exporter.otlp.proto.http.trace_exporter import (
    OTLPSpanExporter as HTTPTraceExporter,
)
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import SpanProcessor

from ...processors import AttributeBatchSpanProcessor
from ..base import Exporter
from .constants import VERSE_API_KEY, VERSE_HOST, VERSE_PROJECT_ID
from .types import VerseConfig
from .utils import as_traces_endpoint


class VerseExporter(Exporter):
    """Verse HTTP trace exporter."""

    def __init__(self, config: VerseConfig = None):
        self.config = config or VerseExporter.env()

    @property
    def endpoint(self) -> str:
        """Get the Verse HTTP endpoint."""
        return as_traces_endpoint(
            self.config.get("host"),
            self.config.get("api_key"),
        )

    def create_span_processor(self, resource: Resource) -> SpanProcessor:
        if not self.config.get("project_id"):
            raise ValueError("Project ID is required to export traces to Verse")

        return AttributeBatchSpanProcessor(
            HTTPTraceExporter(self.endpoint),
            self.config.get("project_id"),
        )

    def get_name(self) -> str:
        return "verse"

    @staticmethod
    def env() -> VerseConfig:
        """Get the Verse config from environment variables."""
        return VerseConfig(
            api_key=os.environ.get(VERSE_API_KEY),
            host=os.environ.get(VERSE_HOST),
            project_id=os.environ.get(VERSE_PROJECT_ID),
        )
