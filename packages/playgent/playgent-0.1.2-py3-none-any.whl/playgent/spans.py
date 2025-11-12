"""OpenTelemetry-based span utilities for Playgent SDK."""

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider, ReadableSpan
from opentelemetry.sdk.trace.export import BatchSpanProcessor, SpanExporter, SpanExportResult
from opentelemetry.sdk.resources import Resource
from opentelemetry.trace import Status, StatusCode
from typing import Any, Dict, Optional, Sequence
import httpx
import json
import uuid

from . import state


class PlaygentSpanExporter(SpanExporter):
    """Custom OpenTelemetry SpanExporter that sends spans to Playgent backend."""

    def __init__(self, api_key: Optional[str] = None, server_url: Optional[str] = None):
        self.client = httpx.Client(timeout=2.0)
        self.api_key = api_key
        self.server_url = server_url or "https://run.blaxel.ai/pharmie-agents/agents/playgent"

    def export(self, spans: Sequence[ReadableSpan]) -> SpanExportResult:
        """Export spans to Playgent backend."""
        if not self.api_key:
            return SpanExportResult.SUCCESS

        try:
            span_dicts = [self._convert_span(s) for s in spans if s]

            if not span_dicts:
                return SpanExportResult.SUCCESS

            response = self.client.post(
                f"{self.server_url}/spans",
                json={"spans": span_dicts},
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
            )

            return SpanExportResult.SUCCESS if response.status_code == 200 else SpanExportResult.FAILURE

        except Exception:
            return SpanExportResult.FAILURE

    def _convert_span(self, otel_span: ReadableSpan) -> Dict[str, Any]:
        """Convert OpenTelemetry span to Playgent format."""
        # Convert trace_id (128-bit) to UUID
        trace_id = str(uuid.UUID(format(otel_span.context.trace_id, '032x')))

        # Convert span_id (64-bit) to UUID by left-shifting to upper 64 bits
        span_id = str(uuid.UUID(int=otel_span.context.span_id << 64))

        # Convert parent span_id if present
        parent_span_id = None
        if otel_span.parent and otel_span.parent.span_id:
            parent_span_id = str(uuid.UUID(int=otel_span.parent.span_id << 64))

        # Timestamps (nanoseconds to milliseconds)
        start_time_ms = otel_span.start_time // 1_000_000
        end_time_ms = otel_span.end_time // 1_000_000 if otel_span.end_time else None
        duration_ms = (end_time_ms - start_time_ms) if end_time_ms else None

        # Status
        status = "error" if otel_span.status.status_code == StatusCode.ERROR else "ok"
        status_message = otel_span.status.description if otel_span.status.status_code == StatusCode.ERROR else None

        # Extract and process attributes
        attributes = dict(otel_span.attributes) if otel_span.attributes else {}

        # Parse JSON strings back to objects
        for key in ["inputs", "outputs", "function.args", "function.result"]:
            if key in attributes and isinstance(attributes[key], str):
                try:
                    attributes[key] = json.loads(attributes[key])
                except (json.JSONDecodeError, TypeError):
                    pass

        # Extract special attributes
        token_usage = None
        if "token_usage.input" in attributes:
            token_usage = {
                "input": attributes.pop("token_usage.input"),
                "output": attributes.pop("token_usage.output", 0),
                "total": attributes.pop("token_usage.total", 0)
            }

        cost_usd = attributes.pop("cost_usd", None)
        person_id = attributes.pop("person_id", None) or state.person_id
        session_id = attributes.pop("session_id", None)
        kind = attributes.pop("span.kind", "INTERNAL")

        # Keep error information in attributes (don't extract it)
        # The database expects error info to be inside the attributes JSONB column
        if status_message:
            # Add status_message to attributes if present
            attributes["status_message"] = status_message

        span_dict = {
            "trace_id": trace_id,
            "id": span_id,
            "parent_span_id": parent_span_id,
            "name": otel_span.name,
            "kind": kind,
            "start_time": start_time_ms,
            "end_time": end_time_ms,
            "duration_ms": duration_ms,
            "status": status,
            "attributes": attributes,  # Contains error, error.type, error.message, and status_message if present
            "person_id": person_id,
            "session_id": session_id,
            "token_usage": token_usage,
            "cost_usd": cost_usd
        }

        return span_dict

    def shutdown(self) -> None:
        """Shutdown the exporter and close HTTP client."""
        try:
            self.client.close()
        except Exception:
            pass

    def force_flush(self, timeout_millis: int = 30000) -> bool:
        """Force flush any buffered spans."""
        return True


# Playgent-specific tracer (isolated from global OTel namespace)
_playgent_tracer_provider: Optional[TracerProvider] = None
_playgent_tracer: Optional[trace.Tracer] = None


def initialize_tracer(service_name: str = "playgent"):
    """Initialize the Playgent OpenTelemetry tracer with dedicated provider."""
    global _playgent_tracer, _playgent_tracer_provider

    if _playgent_tracer is not None:
        return

    # Create dedicated TracerProvider (NOT set as global)
    resource = Resource.create({"service.name": service_name})
    _playgent_tracer_provider = TracerProvider(resource=resource)

    # Add Playgent span exporter with global state credentials
    from . import state
    exporter = PlaygentSpanExporter(api_key=state.api_key, server_url=state.server_url)
    span_processor = BatchSpanProcessor(exporter)
    _playgent_tracer_provider.add_span_processor(span_processor)

    # Get tracer from OUR provider (not global)
    _playgent_tracer = _playgent_tracer_provider.get_tracer("playgent")


def get_tracer() -> trace.Tracer:
    """Get the Playgent OpenTelemetry tracer instance."""
    if _playgent_tracer is None:
        initialize_tracer()
    return _playgent_tracer


def get_current_trace_id_as_uuid() -> Optional[str]:
    """Get the current trace ID as a UUID string."""
    current_span = trace.get_current_span()
    if current_span and current_span.get_span_context().is_valid:
        trace_id_int = current_span.get_span_context().trace_id
        return str(uuid.UUID(format(trace_id_int, '032x')))
    return None


def flush_tracer():
    """Flush any pending spans without shutting down the tracer."""
    if _playgent_tracer_provider:
        _playgent_tracer_provider.force_flush(timeout_millis=5000)


def shutdown_tracer():
    """Shutdown the tracer and flush any pending spans."""
    if _playgent_tracer_provider:
        _playgent_tracer_provider.shutdown()


def create_client_tracer(api_key: Optional[str], server_url: Optional[str] = None) -> trace.Tracer:
    """Create a dedicated tracer for a specific client configuration.

    This creates an isolated tracer with its own provider and exporter,
    allowing multiple clients to have different API keys and server URLs.

    Args:
        api_key: Playgent API key for this client
        server_url: Optional Playgent server URL (defaults to production)

    Returns:
        A configured OpenTelemetry tracer for this client
    """
    # Create dedicated TracerProvider for this client
    resource = Resource.create({"service.name": "playgent-client"})
    provider = TracerProvider(resource=resource)

    # Add Playgent span exporter with client-specific credentials
    exporter = PlaygentSpanExporter(api_key=api_key, server_url=server_url)
    span_processor = BatchSpanProcessor(exporter)
    provider.add_span_processor(span_processor)

    # Return a tracer from this provider
    return provider.get_tracer("playgent")
