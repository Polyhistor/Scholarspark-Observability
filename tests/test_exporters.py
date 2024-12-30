import pytest
from opentelemetry.sdk.trace.export import SpanExporter
from scholarSparkObservability.core import ExporterFactory, ExporterType

def test_console_exporter():
    config = {"type": "console"}
    exporter = ExporterFactory.create_trace_exporter(config)
    assert isinstance(exporter, SpanExporter)

def test_otlp_http_exporter():
    config = {
        "type": "otlp_http",
        "endpoint": "http://localhost:4318/v1/traces",
        "headers": {"Content-Type": "application/x-protobuf"}
    }
    exporter = ExporterFactory.create_trace_exporter(config)
    assert isinstance(exporter, SpanExporter)

def test_otlp_http_exporter_missing_endpoint():
    config = {"type": "otlp_http"}
    with pytest.raises(ValueError, match="OTLP HTTP exporter requires endpoint"):
        ExporterFactory.create_trace_exporter(config)

def test_otlp_grpc_exporter():
    config = {
        "type": "otlp_grpc",
        "endpoint": "http://localhost:4317",
    }
    exporter = ExporterFactory.create_trace_exporter(config)
    assert isinstance(exporter, SpanExporter)

def test_otlp_grpc_exporter_missing_endpoint():
    config = {"type": "otlp_grpc"}
    with pytest.raises(ValueError, match="OTLP GRPC exporter requires endpoint"):
        ExporterFactory.create_trace_exporter(config)

def test_tempo_exporter():
    # Test with custom endpoint
    config = {
        "type": "tempo",
        "endpoint": "http://custom-tempo:4318/v1/traces",
    }
    exporter = ExporterFactory.create_trace_exporter(config)
    assert isinstance(exporter, SpanExporter)

    # Test with default endpoint
    config = {"type": "tempo"}
    exporter = ExporterFactory.create_trace_exporter(config)
    assert isinstance(exporter, SpanExporter)

def test_jaeger_exporter():
    config = {
        "type": "jaeger",
        "host": "jaeger",
        "port": 6831
    }
    
    try:
        import opentelemetry.exporter.jaeger
        exporter = ExporterFactory.create_trace_exporter(config)
        assert isinstance(exporter, SpanExporter)
    except ImportError:
        pytest.skip("Jaeger exporter not installed")

def test_zipkin_exporter():
    config = {
        "type": "zipkin",
        "endpoint": "http://zipkin:9411/api/v2/spans"
    }
    
    try:
        import opentelemetry.exporter.zipkin
        exporter = ExporterFactory.create_trace_exporter(config)
        assert isinstance(exporter, SpanExporter)
    except ImportError:
        pytest.skip("Zipkin exporter not installed")

def test_zipkin_exporter_missing_endpoint():
    config = {"type": "zipkin"}
    with pytest.raises(ValueError, match="Zipkin exporter requires endpoint"):
        ExporterFactory.create_trace_exporter(config)

def test_invalid_exporter_type():
    config = {"type": "invalid_type"}
    with pytest.raises(ValueError, match="Unsupported exporter type: invalid_type"):
        ExporterFactory.create_trace_exporter(config)

def test_default_exporter_type():
    config = {}  # No type specified
    exporter = ExporterFactory.create_trace_exporter(config)
    assert isinstance(exporter, SpanExporter)  # Should default to console exporter

@pytest.mark.parametrize("exporter_type", [
    ExporterType.CONSOLE,
    ExporterType.OTLP_HTTP,
    ExporterType.OTLP_GRPC,
    ExporterType.TEMPO,
    ExporterType.JAEGER,
    ExporterType.ZIPKIN
])
def test_exporter_type_constants(exporter_type):
    assert isinstance(exporter_type, str)
    assert exporter_type in [
        "console",
        "otlp_http",
        "otlp_grpc",
        "tempo",
        "jaeger",
        "zipkin"
    ] 