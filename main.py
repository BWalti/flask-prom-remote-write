from flask import Flask
from opentelemetry import metrics, trace
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource

from opentelemetry.exporter.prometheus_remote_write import (
    PrometheusRemoteWriteMetricsExporter,
)

exporter = PrometheusRemoteWriteMetricsExporter(
    endpoint="http://localhost:9090/api/v1/write",
    headers={"X-Scope-Org-ID": "5"},
)

resource = Resource.create(
    {
        "service.name": "python-prom-write",
        "service.namespace": "examples",
        "service.instance.id": "instance123",
    }
)

meter_provider = MeterProvider(
    metric_readers=[
        PeriodicExportingMetricReader(
            exporter, export_interval_millis=1000
        )
    ],
    resource=resource,
)

metrics.set_meter_provider(meter_provider)

meter = metrics.get_meter(__name__)

requests_counter = meter.create_counter(
    name="my_requests",
    description="number of requests",
    # unit="1", # gets appended to the metric name as "_1"
)

app = Flask(__name__)
FlaskInstrumentor().instrument_app(app)

@app.route("/")
def hello_world():
    requests_counter.add(1)
    return "Hello, World!"
