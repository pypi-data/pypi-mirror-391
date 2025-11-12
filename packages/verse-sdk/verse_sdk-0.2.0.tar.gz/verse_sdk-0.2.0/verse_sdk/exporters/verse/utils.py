def as_traces_endpoint(host: str | None, api_key: str | None = None) -> str:
    """Convert a host to a traces endpoint."""

    traces_endpoint = ""

    if host:
        traces_endpoint = host if host.endswith("traces") else f"{host}/v1/traces"

    if api_key:
        return f"{traces_endpoint}?api_key={api_key}"

    return traces_endpoint
