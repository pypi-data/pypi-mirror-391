from typing import Optional

from ..types import ExporterConfig


class VerseConfig(ExporterConfig):
    api_key: Optional[str]
    host: Optional[str]
    project_id: str
