from verse_sdk.exporters.verse.utils import as_traces_endpoint


class TestAsTracesEndpoint:
    def test_as_traces_endpoint_with_formatted_host(self):
        host = "https://otel.verse.com/v1/traces"
        result = as_traces_endpoint(host)
        assert result == "https://otel.verse.com/v1/traces"

    def test_as_traces_endpoint_with_host_and_api_key(self):
        host = "https://otel.verse.com"
        api_key = "1234567890"
        result = as_traces_endpoint(host, api_key)
        assert result == "https://otel.verse.com/v1/traces?api_key=1234567890"

    def test_as_traces_endpoint_with_host_and_no_api_key(self):
        host = "https://otel.verse.com"
        result = as_traces_endpoint(host, None)
        assert result == "https://otel.verse.com/v1/traces"
