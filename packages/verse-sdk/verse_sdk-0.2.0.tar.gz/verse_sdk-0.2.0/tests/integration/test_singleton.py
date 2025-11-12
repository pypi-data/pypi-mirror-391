import json

from verse_sdk import observe, verse


def parse_spans(out: str) -> list[dict]:
    """Parse the spans from the output."""
    spans = []
    buffer = ""
    for line in out.splitlines():
        line = line.strip()
        if not line:
            continue
        buffer += line
        if buffer.count("{") == buffer.count("}"):
            try:
                span = json.loads(buffer)
                spans.append(span)
            except json.JSONDecodeError:
                pass
            buffer = ""

    spans.reverse()
    return spans


def test_lazy_singleton_init(capfd):
    @observe()
    def trace_function():
        pass

    # Initialize the SDK after the decorator is defined
    verse.init(
        app_name="test_lazy_singleton_init",
        exporters=[verse.exporters.console()],
    )

    trace_function()
    out, _ = capfd.readouterr()
    spans = parse_spans(out)

    assert len(spans) == 1
    assert spans[0]["name"] == "trace_function"
