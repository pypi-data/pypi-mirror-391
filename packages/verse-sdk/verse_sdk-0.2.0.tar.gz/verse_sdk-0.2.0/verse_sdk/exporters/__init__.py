import logging
from functools import wraps

from .base import Exporter
from .console import ConsoleExporter
from .langfuse import LangfuseConfig, LangfuseExporter
from .otel import OtelConfig, OTLPExporter
from .types import ExporterConfig
from .verse import VerseConfig, VerseExporter


class ExportersRegistry:
    @staticmethod
    def safe_named_exporter(fn):
        """Create an error boundary around each exporter factory function."""

        @wraps(fn)
        def create_exporter(*args, **kwargs) -> Exporter | None:
            try:
                return fn(*args, **kwargs)
            except Exception as e:
                logging.warning("Error creating exporter `%s`", fn.__name__, exc_info=e)
                return None

        return create_exporter

    @safe_named_exporter
    def console(self, config: ExporterConfig = None) -> ConsoleExporter:
        """Create a console exporter."""
        return ConsoleExporter(config or {})

    @safe_named_exporter
    def langfuse(self, config: LangfuseConfig = None) -> LangfuseExporter:
        """Create a langfuse exporter."""
        return LangfuseExporter(config or {})

    @safe_named_exporter
    def otel(self, config: OtelConfig = None) -> OTLPExporter:
        """Create a otel exporter."""
        return OTLPExporter(config or {})

    @safe_named_exporter
    def verse(self, config: VerseConfig = None) -> VerseExporter:
        """Create a verse exporter."""
        return VerseExporter(config or {})


__all__ = [
    "Exporter",
    "ExportersRegistry",
    "LangfuseConfig",
    "OtelConfig",
    "VerseConfig",
]
