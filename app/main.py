from opentelemetry import trace, metrics
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource
from opentelemetry.trace import Status, StatusCode
from typing import Optional, Dict, List, Any
import logging

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
        """Setup trace provider and exporters"""
        provider = TracerProvider(resource=resource)
        
        if exporters:
            for exporter_config in exporters:
                try:
                    otlp_exporter = OTLPSpanExporter(
                        endpoint=exporter_config.get("endpoint"),
                        headers=exporter_config.get("headers", {})
                    )
                    processor = BatchSpanProcessor(otlp_exporter)
                    provider.add_span_processor(processor)
                except Exception as e:
                    logging.error(f"Failed to setup trace exporter: {str(e)}")
                    if self.debug:
                        raise
        
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