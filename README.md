# ScholarSparkObservability

A Python package for monitoring and observability in Apache Spark applications.


## Installation

You can install the package using pip:

```bash
pip install scholarSparkObservability
```

Or using Poetry:

```bash
poetry add scholarSparkObservability
```

## Usage

Here's a simple example of how to use the package:

```python
from scholarSparkObservability import ScholarSparkObservability

client = ScholarSparkObservability()
result = client.example_method()
print(result)
```

## Features

## Features

### OpenTelemetry Integration
- Full OpenTelemetry support for distributed tracing and metrics collection
- Configurable exporters for different observability backends (e.g., Jaeger, Zipkin)
- Automatic context propagation across Spark jobs and stages

### Comprehensive Monitoring
- Real-time metrics collection for Spark executors and tasks
- Custom span creation for detailed performance tracking
- Exception tracking and error reporting with detailed attributes
- Resource utilization metrics (CPU, memory, I/O)

### Flexible Configuration
- Singleton pattern for consistent telemetry setup across your application
- Environment-aware configuration (production, staging, development)
- Customizable export intervals and batch processing
- Debug mode for detailed logging and troubleshooting

### Enterprise-Ready
- Low-overhead implementation suitable for production workloads
- Batch span processing for efficient telemetry data export
- Support for multiple exporters and monitoring backends
- Robust error handling and logging capabilities

### Easy Integration
- Simple API for creating spans and recording metrics
- Automatic service name and version tracking
- Built-in support for custom attributes and tags
- Seamless integration with existing Spark applications

## Development

To contribute to this project:

1. Clone the repository:
```bash
git clone https://github.com/pouyaardehkhani/ScholarSparkObservability.git
cd ScholarSparkObservability
```

2. Install dependencies:
```bash
# Using poetry (recommended)
poetry install

# Using pip
pip install -r requirements.txt
```

3. Run tests:
```bash
# Using poetry
poetry run pytest

# Using pytest directly
pytest tests/
```

4. Set up pre-commit hooks:
```bash
pre-commit install
```

5. Create a new branch for your feature:
```bash
git checkout -b feature/your-feature-name
```

### Development Guidelines
- Follow PEP 8 style guidelines
- Write tests for new features
- Update documentation as needed
- Add type hints to all new functions
- Ensure all tests pass before submitting PR

### Building Documentation
```bash
# Generate documentation
poetry run sphinx-build -b html docs/source docs/build
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

# Authors
Pouya Ataei- Initial work
