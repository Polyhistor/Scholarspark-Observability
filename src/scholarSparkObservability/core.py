from opentelemetry import trace, metrics
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter as OTLPGRPCSpanExporter
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.exporter.zipkin.json import ZipkinExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource
from opentelemetry.trace import Status, StatusCode
from typing import Optional, Dict, List, Any, Union
import logging

class ExporterType:
    """Supported exporter types"""
    OTLP_HTTP = "otlp_http"
    OTLP_GRPC = "otlp_grpc"
    JAEGER = "jaeger"
    ZIPKIN = "zipkin"
    TEMPO = "tempo"
    CONSOLE = "console"

class ExporterFactory:
    """Factory for creating different types of exporters"""
    @staticmethod
    def create_trace_exporter(exporter_config: Dict[str, Any]):
        """
        Create a trace exporter based on configuration
        
        Args:
            exporter_config: Dictionary containing exporter configuration
                Required keys vary by exporter type:
                - type: The type of exporter (from ExporterType)
                - endpoint: URL for OTLP/Zipkin/Tempo exporters
                - headers: Optional headers for HTTP-based exporters
                - host/port: Required for Jaeger
        """
        exporter_type = exporter_config.get("type", ExporterType.CONSOLE).lower()
        endpoint = exporter_config.get("endpoint")
        headers = exporter_config.get("headers", {})

        if exporter_type == ExporterType.OTLP_HTTP:
            if not endpoint:
                raise ValueError("OTLP HTTP exporter requires endpoint")
            return OTLPSpanExporter(endpoint=endpoint, headers=headers)
            
        elif exporter_type == ExporterType.OTLP_GRPC:
            if not endpoint:
                raise ValueError("OTLP GRPC exporter requires endpoint")
            return OTLPGRPCSpanExporter(endpoint=endpoint, headers=headers)
            
        elif exporter_type == ExporterType.JAEGER:
            return JaegerExporter(
                agent_host_name=exporter_config.get("host", "localhost"),
                agent_port=exporter_config.get("port", 6831),
            )
            
        elif exporter_type == ExporterType.ZIPKIN:
            if not endpoint:
                raise ValueError("Zipkin exporter requires endpoint")
            return ZipkinExporter(
                endpoint=endpoint,
                local_node_ipv4=exporter_config.get("local_node_ipv4"),
                local_node_ipv6=exporter_config.get("local_node_ipv6"),
            )
            
        elif exporter_type == ExporterType.TEMPO:
            if not endpoint:
                endpoint = "http://tempo:4318/v1/traces"
            return OTLPSpanExporter(
                endpoint=endpoint,
                headers=headers or {"Content-Type": "application/x-protobuf"}
            )
            
        elif exporter_type == ExporterType.CONSOLE:
            return ConsoleSpanExporter()
            
        else:
            raise ValueError(f"Unsupported exporter type: {exporter_type}")

class OTelSetup:
    """
    Singleton class for OpenTelemetry setup handling both tracing and metrics.
    Supports multiple exporters and provides comprehensive observability setup.
    """
    _instance = None
      
    def _init_(self, 
                 service_name: str,
                 service_version: str,
                 environment: Optional[str] = None,
                 debug: bool = False,
                 exporters: List[Dict[str, str]] = None):
        """
        Initialize OpenTelemetry setup with both tracing and metrics support.
        
        Args:
            service_name: Name of the service
            service_version: Version of the service
            environment: Deployment environment (e.g., 'production', 'staging')
            debug: Enable debug mode for more verbose logging
            exporters: List of exporter configurations with endpoints and headers
        """
        self.service_name = service_name
        self.service_version = service_version
        self.debug = debug
        
        if debug:
            logging.basicConfig(level=logging.DEBUG)
        
        # Create resource with service information
        resource = Resource.create({
            "service.name": service_name,
            "service.version": service_version,
            **({"deployment.environment": environment} if environment else {}),
            "telemetry.sdk.name": "opentelemetry",
            "telemetry.sdk.language": "python"
        })

        # Setup trace provider
        self._setup_tracing(resource, exporters)
        
        # Setup metrics provider
        self._setup_metrics(resource, exporters)

    def _setup_tracing(self, resource: Resource, exporters: List[Dict[str, str]]) -> None:
        """
        Setup trace provider and exporters
        
        Args:
            resource: OpenTelemetry resource with service information
            exporters: List of exporter configurations. If empty, defaults to console exporter.
        """
        provider = TracerProvider(resource=resource)
        
        if not exporters:
            # Default to console exporter
            console_processor = BatchSpanProcessor(ConsoleSpanExporter())
            provider.add_span_processor(console_processor)
            logging.info("No exporters configured. Using console exporter for development.")
        else:
            success = False
            for exporter_config in exporters:
                try:
                    exporter = ExporterFactory.create_trace_exporter(exporter_config)
                    processor = BatchSpanProcessor(exporter)
                    provider.add_span_processor(processor)
                    logging.info(f"Successfully configured {exporter_config.get('type')} exporter")
                    success = True
                except Exception as e:
                    logging.error(f"Failed to setup exporter {exporter_config.get('type')}: {str(e)}")
                    if self.debug:
                        raise
            
            # If all exporters failed, fall back to console exporter
            if not success:
                console_processor = BatchSpanProcessor(ConsoleSpanExporter())
                provider.add_span_processor(console_processor)
                logging.warning("All exporters failed. Falling back to console exporter.")
        
        trace.set_tracer_provider(provider)
        self.provider = provider

    def _setup_metrics(self, resource: Resource, exporters: List[Dict[str, str]]) -> None:
        """Setup metrics provider and exporters"""
        if not exporters:
            logging.warning("No exporters configured for metrics")
            return

        try:
            # Use the first exporter configuration for metrics
            metric_exporter = OTLPMetricExporter(
                endpoint=exporters[0].get("endpoint"),
                headers=exporters[0].get("headers", {})
            )
            
            reader = PeriodicExportingMetricReader(
                metric_exporter,
                export_interval_millis=10000  # Export every 10 seconds
            )
            
            metric_provider = MeterProvider(resource=resource)
            metric_provider.add_metric_reader(reader)
            metrics.set_meter_provider(metric_provider)
            self.metric_provider = metric_provider
            
        except Exception as e:
            logging.error(f"Failed to setup metrics: {str(e)}")
            if self.debug:
                raise

    @classmethod
    def initialize(cls, **kwargs) -> 'OTelSetup':
        """
        Initialize the singleton instance with the provided configuration.
        
        Returns:
            OTelSetup: The singleton instance
        """
        if cls._instance is None:
            cls._instance = cls(**kwargs)
        return cls._instance

    @classmethod
    def get_instance(cls) -> 'OTelSetup':
        """
        Get the singleton instance. Must be initialized first.
        
        Returns:
            OTelSetup: The singleton instance
        
        Raises:
            RuntimeError: If instance hasn't been initialized
        """
        if cls._instance is None:
            raise RuntimeError("OTelSetup not initialized. Call initialize() first.")
        return cls._instance

    def get_tracer(self) -> trace.Tracer:
        """
        Get a tracer instance for the service.
        
        Returns:
            Tracer: OpenTelemetry tracer instance
        """
        return trace.get_tracer(self.service_name, self.service_version)

    def get_meter(self) -> metrics.Meter:
        """
        Get a meter instance for metrics collection.
        
        Returns:
            Meter: OpenTelemetry meter instance
        """
        return metrics.get_meter(self.service_name, self.service_version)

    def create_span(self, name: str, attributes: Dict[str, Any] = None) -> trace.Span:
        """
        Create a new span with the given name and attributes.
        
        Args:
            name: Name of the span
            attributes: Optional attributes to add to the span
            
        Returns:
            Span: The created span
        """
        tracer = self.get_tracer()
        span = tracer.start_span(name)
        
        if attributes:
            span.set_attributes(attributes)
            
        return span

    def record_exception(self, span: trace.Span, exception: Exception, attributes: Dict[str, Any] = None):
        """
        Record an exception in the given span.
        
        Args:
            span: The span to record the exception in
            exception: The exception to record
            attributes: Optional additional attributes for the exception
        """
        span.set_status(Status(StatusCode.ERROR))
        span.record_exception(exception, attributes=attributes)