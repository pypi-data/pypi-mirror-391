from opentelemetry.sdk.trace.export import BatchSpanProcessor, SpanExporter

from .attribute import AttributeProcessor


class AttributeBatchSpanProcessor(BatchSpanProcessor):
    """
    Small wrapper so that we can injected project ID attributes per exporter rather than globally.
    Realistically, only Verse cares about project ID and attribute propagation.
    """

    def __init__(self, exporter: SpanExporter, project_id: str):
        """Initialize the processor with the exporter and project ID."""
        self.attribute_processor = AttributeProcessor(project_id)
        super().__init__(exporter)

    def on_start(self, span, parent_context=None):
        """Run attribute processor when span starts."""
        self.attribute_processor.on_start(span, parent_context)
        super().on_start(span, parent_context)

    def on_end(self, span):
        """Run attribute processor before exporting spans."""
        self.attribute_processor.on_end(span)
        super().on_end(span)
