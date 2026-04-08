import os
import logging

from opentelemetry import trace, metrics
from opentelemetry.sdk.resources import Resource, SERVICE_NAME
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
from opentelemetry.instrumentation.requests import RequestsInstrumentor

logger = logging.getLogger(__name__)


def setup_telemetry() -> None:
    """
    Initialise OpenTelemetry traces and metrics.
    Exporters point to the OTLP HTTP endpoint (default: localhost:4318),
    which is what grafana/otel-lgtm exposes out of the box.
    """
    endpoint    = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4318")
    service     = os.getenv("OTEL_SERVICE_NAME", "voyage-api")
    environment = os.getenv("ENVIRONMENT", "development")

    resource = Resource(attributes={
        SERVICE_NAME:          service,
        "deployment.environment": environment,
    })

    # ── Traces ────────────────────────────────────────────────────────────────
    tracer_provider = TracerProvider(resource=resource)
    tracer_provider.add_span_processor(
        BatchSpanProcessor(
            OTLPSpanExporter(endpoint=f"{endpoint}/v1/traces")
        )
    )
    trace.set_tracer_provider(tracer_provider)

    # ── Metrics ───────────────────────────────────────────────────────────────
    metric_reader = PeriodicExportingMetricReader(
        OTLPMetricExporter(endpoint=f"{endpoint}/v1/metrics"),
        export_interval_millis=15_000,   # push every 15 s
    )
    meter_provider = MeterProvider(resource=resource, metric_readers=[metric_reader])
    metrics.set_meter_provider(meter_provider)

    # ── Auto-instrument outbound HTTP (Google Maps / OpenWeather calls) ───────
    RequestsInstrumentor().instrument()

    logger.info("OpenTelemetry initialised → %s  (service=%s)", endpoint, service)


# ── Custom business meters ─────────────────────────────────────────────────────
# Import these wherever you want to record business events.

_meter = metrics.get_meter("voyage")

trips_counter = _meter.create_counter(
    name="voyage.trips.total",
    description="Number of trip planning requests",
    unit="1",
)

pdf_downloads_counter = _meter.create_counter(
    name="voyage.pdf.downloads.total",
    description="Number of PDF downloads",
    unit="1",
)

agent_errors_counter = _meter.create_counter(
    name="voyage.agent.errors.total",
    description="Number of agent-level errors",
    unit="1",
)

agent_duration_histogram = _meter.create_histogram(
    name="voyage.agent.duration",
    description="Time spent inside each agent (seconds)",
    unit="s",
)
