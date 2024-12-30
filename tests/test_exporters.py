import pytest
from scholarSparkObservability.core import ExporterFactory

def test_jaeger_exporter_missing():
    config = {"type": "jaeger", "host": "localhost", "port": 6831}
    
    try:
        import opentelemetry.exporter.jaeger
        ExporterFactory.create_trace_exporter(config)
    except ImportError:
        pytest.skip("Jaeger exporter not installed")

def test_zipkin_exporter_missing():
    config = {"type": "zipkin", "endpoint": "http://localhost:9411"}
    
    try:
        import opentelemetry.exporter.zipkin
        ExporterFactory.create_trace_exporter(config)
    except ImportError:
        pytest.skip("Zipkin exporter not installed") 