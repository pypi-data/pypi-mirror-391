# Distributed Tracing

The Cognite Typed Functions framework provides built-in distributed tracing support through OpenTelemetry, making it easy to understand execution flow, identify performance bottlenecks, and debug issues in production. Traces are sent to an OpenTelemetry collector like LightStep, Jaeger, or any OTLP-compatible backend.

## Table of Contents

- [Why Use Tracing?](#why-use-tracing)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Architecture Overview](#architecture-overview)
- [Core Concepts](#core-concepts)
- [Usage Patterns](#usage-patterns)
- [Span Metadata](#span-metadata)
- [Advanced Patterns](#advanced-patterns)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

## Why Use Tracing?

Tracing helps you:

- **Understand execution flow** - See how requests flow through your code
- **Identify performance bottlenecks** - Find slow operations in your function
- **Debug production issues** - Trace exactly what happened during a specific execution
- **Monitor system behavior** - Analyze patterns across function executions
- **Track dependencies** - See how different services interact

Unlike logging, which gives you discrete events, tracing provides a hierarchical view of operations with timing information, making it perfect for understanding complex workflows.

## Quick Start

### 1. Start Your OpenTelemetry Collector

For local development with LightStep Developer Satellite:

```bash
# Start LightStep Developer Satellite on port 8360
docker run -p 8360:8360 lightstep/lightstep-satellite-dev:latest
```

Or use any OTLP-compatible backend (Jaeger, Zipkin, etc.).

### 2. Add TracingApp to Your Composition

```python
from cognite_typed_functions import (
    FunctionApp,
    FunctionTracer,
    create_function_service,
    create_tracing_app,
)

app = FunctionApp(title="My API", version="1.0.0")

# Configure OTLP endpoint for local development
tracing = create_tracing_app(
    otlp_endpoint="http://localhost:8360",
    insecure=True  # For local development
)

@app.get("/items/{item_id}")
def get_item(
    client: CogniteClient,
    tracer: FunctionTracer,  # Injected by TracingApp
    item_id: int
) -> dict:
    """Retrieve an item with tracing"""

    with tracer.span("fetch_from_cdf"):
        item = client.assets.retrieve(id=item_id)

    with tracer.span("process_data"):
        result = {"id": item.id, "name": item.name}

    return result

# Compose with tracing app
handle = create_function_service(tracing, app)
```

### 3. Use Automatic Root Spans

The `@tracing.trace()` decorator automatically creates a root span for your entire request:

```python
@app.get("/items/{item_id}")
@tracing.trace()  # Creates root span automatically
def get_item(
    client: CogniteClient,
    tracer: FunctionTracer,
    item_id: int
) -> dict:
    # Root span is automatically created with HTTP metadata
    # Just add child spans for your business logic

    with tracer.span("fetch_item"):
        item = client.assets.retrieve(id=item_id)

    return {"id": item.id, "name": item.name}

handle = create_function_service(tracing, app)
```

### 4. View Your Traces

Traces are automatically sent to your OpenTelemetry collector. Access them through:

- **LightStep UI**: View traces in the LightStep Developer Satellite UI
- **Jaeger UI**: Access at <http://localhost:16686> (if using Jaeger)
- **Backend-specific UI**: Use your collector's native interface

Each trace includes:

- Trace ID: Unique identifier for the entire request
- Span hierarchy: Parent-child relationships showing execution flow
- Timing information: Duration of each operation
- Attributes: HTTP metadata, Cognite metadata (function_id, call_id), custom attributes
- Events: Exceptions and custom events

## Configuration

### TracingApp Parameters

`create_tracing_app()` accepts the following configuration parameters:

```python
tracing = create_tracing_app(
    otlp_endpoint="http://localhost:8360",  # Required: OTLP collector endpoint
    service_name="my-cognite-function",      # Optional: Service identifier (default: "cognite-typed-functions")
    service_version="1.0.0",                 # Optional: Service version (default: "1.0.0")
    insecure=True                            # Optional: Use insecure connection (default: False)
)
```

#### Parameters

- **`otlp_endpoint`** (required): URL of your OpenTelemetry collector
  - Example: `"http://localhost:8360"` for LightStep Satellite
  - Example: `"http://jaeger:4317"` for Jaeger
  - Must be accessible from your Cognite Function

- **`service_name`** (optional): Name used to identify your service in traces
  - Default: `"cognite-typed-functions"`
  - Use this to distinguish between different functions/services
  - Example: `"data-pipeline-extractor"`

- **`service_version`** (optional): Version of your service
  - Default: `"1.0.0"`
  - Useful for tracking behavior across deployments
  - Example: `"2.1.3"`

- **`insecure`** (optional): Whether to use an insecure (non-TLS) connection
  - Default: `False` (uses TLS)
  - ****Warning:** Security Warning**: Only set to `True` for local development
  - For production, ensure your OTLP endpoint uses TLS and keep this as `False`

#### Example: Local Development Configuration

```python
# For local development with LightStep Satellite
tracing = create_tracing_app(
    otlp_endpoint="http://localhost:8360",
    service_name="my-dev-function",
    insecure=True  # OK for local development
)
```

#### Example: Production Configuration

```python
# For production with TLS-enabled collector
tracing = create_tracing_app(
    otlp_endpoint="https://collector.example.com:4317",
    service_name="production-data-pipeline",
    service_version="2.1.0",
    insecure=False  # TLS enabled (default)
)
```

## Architecture Overview

### Design Philosophy

The tracing system follows OpenTelemetry best practices:

1. **One-time setup**: TracerProvider is configured once at application startup
2. **No per-request overhead**: No setup/teardown on each request
3. **Standard OTLP export**: Uses OpenTelemetry Protocol (OTLP) over gRPC
4. **Production-safe**: No resource leaks, proper thread management
5. **Backend agnostic**: Works with any OTLP-compatible collector

### How It Works

```
Application Startup:
  TracingApp.__init__(otlp_endpoint="http://localhost:8360", insecure=True)
    └─> setup_global_tracer_provider()
          ├─> Create TracerProvider (global, singleton)
          ├─> Create BatchSpanProcessor (single background thread)
          └─> Create OTLPSpanExporter
                └─> Sends spans to OTLP endpoint via gRPC

Per Request:
  1. Handler requests tracer: FunctionTracer
  2. Framework injects FunctionTracer via DI (no setup needed)
  3. @tracing.trace() creates root span with cognite.call_id attribute
  4. Child spans inherit context through OpenTelemetry
  5. BatchSpanProcessor exports spans asynchronously
  6. OTLPSpanExporter sends to collector
  7. Collector/backend organizes traces by trace_id
```

### Key Components

- **TracingApp**: Composable app that sets up tracing infrastructure
- **FunctionTracer**: Wrapper around OpenTelemetry tracer for easy span creation
- **OTLPSpanExporter**: Standard OTLP exporter for gRPC transport
- **BatchSpanProcessor**: Asynchronous span export (non-blocking)
- **setup_global_tracer_provider()**: One-time OpenTelemetry configuration

### Supported Backends

Any OpenTelemetry-compatible backend works:

- **LightStep** (Developer Satellite or Cloud)
- **Jaeger**
- **Zipkin**
- **New Relic**
- **Honeycomb**
- **Datadog**
- **AWS X-Ray** (via OTLP collector)
- **Google Cloud Trace** (via OTLP collector)

## Core Concepts

### Spans

A span represents a single operation in your application. Spans have:

- **Name**: Descriptive name like "fetch_user_data" or "GET /items/123"
- **Start/End Time**: Precise timing information
- **Attributes**: Key-value metadata (e.g., `http.method: "GET"`)
- **Status**: Success or error state
- **Events**: Timestamped events within the span (e.g., exceptions)
- **Parent Span**: Creates hierarchical trace structure

### Traces

A trace is a collection of spans that represent a single request/execution. All spans in a trace share the same `trace_id` and are connected through parent-child relationships.

### Context Propagation

OpenTelemetry automatically propagates trace context, so child spans know their parent. When you create a span inside another span's context, the parent-child relationship is automatic:

```python
with tracer.span("parent"):  # Root span
    with tracer.span("child1"):  # Automatically becomes child of "parent"
        with tracer.span("grandchild"):  # Child of "child1"
            pass
    with tracer.span("child2"):  # Also child of "parent"
        pass
```

## Usage Patterns

### Manual Span Creation

Create spans for specific operations:

```python
@app.post("/process")
def process_data(tracer: FunctionTracer, data: list[dict]) -> dict:
    with tracer.span("validate_input"):
        # Validation logic
        if not data:
            raise ValueError("Data required")

    with tracer.span("transform_data"):
        processed = [transform(item) for item in data]

    with tracer.span("save_to_cdf"):
        # Save to CDF
        pass

    return {"processed": len(processed)}
```

### Automatic Root Spans with Decorator

Use `@tracing.trace()` to automatically add a root span:

```python
@app.get("/items/{item_id}")
@tracing.trace()  # Root span with HTTP metadata
def get_item(
    client: CogniteClient,
    tracer: FunctionTracer,
    item_id: int
) -> dict:
    # Root span includes:
    # - http.method: "GET"
    # - http.route: "/items/{item_id}"
    # - function.name: "get_item"
    # - cognite.call_id, cognite.function_id, etc.

    with tracer.span("business_logic"):
        pass

    return {"id": item_id}
```

### Custom Span Names

Override the automatic span name:

```python
@app.post("/batch")
@tracing.trace("batch_processing_operation")  # Custom name
def process_batch(tracer: FunctionTracer, items: list[dict]) -> dict:
    with tracer.span("validate_batch"):
        pass
    return {"processed": len(items)}
```

### Async Handlers

Tracing works seamlessly with async handlers:

```python
@app.get("/items/{item_id}")
@tracing.trace()
async def get_item_async(
    client: CogniteClient,
    tracer: FunctionTracer,
    item_id: int
) -> dict:
    async def fetch_details():
        with tracer.span("fetch_details"):
            await asyncio.sleep(0.1)
            return {"extra": "data"}

    async def fetch_reviews():
        with tracer.span("fetch_reviews"):
            await asyncio.sleep(0.1)
            return {"reviews": []}

    # Fetch concurrently with tracing
    details, reviews = await asyncio.gather(
        fetch_details(),
        fetch_reviews()
    )

    return {"id": item_id, "details": details, "reviews": reviews}
```

### Adding Span Attributes

Add custom metadata to spans:

```python
with tracer.span("process_batch") as span:
    span.set_attribute("batch_size", len(items))
    span.set_attribute("processing_mode", "fast")

    for item in items:
        process_item(item)

    span.set_attribute("items_processed", len(items))
```

### Recording Events

Add timestamped events within spans:

```python
with tracer.span("complex_operation") as span:
    span.add_event("started_phase_1")

    # Phase 1
    do_phase_1()

    span.add_event("started_phase_2", {
        "phase_1_results": 42,
        "config": "optimized"
    })

    # Phase 2
    do_phase_2()
```

### Exception Handling

Exceptions are automatically recorded in spans:

```python
with tracer.span("risky_operation"):
    try:
        result = might_fail()
    except Exception as e:
        # Exception is automatically added to span with:
        # - exception.type
        # - exception.message
        # - Status set to ERROR
        raise
```

### Tracing Without the Decorator

If you don't use `@tracing.trace()`, you can still create manual root spans:

```python
@app.get("/items/{item_id}")
def get_item(
    tracer: FunctionTracer,
    function_call_info: FunctionCallInfo,
    item_id: int
) -> dict:
    # Manual root span with metadata
    with tracer.span("get_item_operation") as root_span:
        root_span.set_attribute("cognite.call_id", function_call_info["call_id"])
        root_span.set_attribute("item_id", item_id)

        with tracer.span("fetch"):
            # Child operations
            pass

        return {"id": item_id}
```

## Span Metadata

### Automatic Metadata (with `@tracing.trace()`)

The decorator automatically adds:

**HTTP Metadata:**

- `http.method`: HTTP method (GET, POST, etc.)
- `http.route`: Route pattern (e.g., `/items/{item_id}`)
- `http.url`: Full request path
- `http.status_code`: Response status (200, 500, etc.)

**Function Metadata:**

- `function.name`: Handler function name

**Cognite Metadata:**

- `cognite.call_id`: Unique call identifier (required for routing)
- `cognite.function_id`: Function ID in CDF
- `cognite.schedule_id`: Schedule ID (if scheduled)
- `cognite.scheduled_time`: Scheduled execution time

**Error Metadata (on exception):**

- `error`: `true`
- `exception.type`: Exception class name
- `exception.message`: Exception message

### Custom Metadata

Add your own attributes for business context:

```python
with tracer.span("process_order") as span:
    span.set_attribute("customer_id", customer_id)
    span.set_attribute("order_total", order.total)
    span.set_attribute("payment_method", "credit_card")
    span.set_attribute("region", "europe-west1")
```

## Advanced Patterns

### Conditional Tracing

Only create spans when needed:

```python
def process_item(tracer: FunctionTracer | None, item: dict, detailed: bool = False):
    if tracer and detailed:
        with tracer.span("detailed_processing"):
            return detailed_process(item)
    else:
        return simple_process(item)
```

### Tracing Helper Functions

Create reusable traced operations:

```python
def fetch_with_tracing(tracer: FunctionTracer, url: str) -> dict:
    """Fetch data with automatic tracing"""
    with tracer.span("http_request") as span:
        span.set_attribute("http.url", url)
        response = requests.get(url)
        span.set_attribute("http.status_code", response.status_code)
        return response.json()

@app.get("/data")
@tracing.trace()
def get_data(tracer: FunctionTracer) -> dict:
    data1 = fetch_with_tracing(tracer, "https://api1.example.com")
    data2 = fetch_with_tracing(tracer, "https://api2.example.com")
    return {"data1": data1, "data2": data2}
```

### Nested Operations with Context

Pass tracer through your application layers:

```python
class DataService:
    def __init__(self, tracer: FunctionTracer | None = None):
        self.tracer = tracer

    def fetch_data(self, id: int) -> dict:
        if self.tracer:
            with self.tracer.span("DataService.fetch_data"):
                return self._fetch_from_db(id)
        return self._fetch_from_db(id)

    def _fetch_from_db(self, id: int) -> dict:
        # Actual implementation
        return {"id": id}

@app.get("/items/{id}")
@tracing.trace()
def get_item(tracer: FunctionTracer, id: int) -> dict:
    service = DataService(tracer)
    return service.fetch_data(id)
```

### Batch Processing

Trace individual items in a batch:

```python
@app.post("/batch")
@tracing.trace()
def process_batch(tracer: FunctionTracer, items: list[dict]) -> dict:
    results = []

    with tracer.span("batch_processing") as batch_span:
        batch_span.set_attribute("batch_size", len(items))

        for i, item in enumerate(items):
            with tracer.span(f"process_item_{i}") as item_span:
                item_span.set_attribute("item_id", item.get("id"))
                try:
                    result = process_item(item)
                    results.append(result)
                except Exception as e:
                    item_span.set_attribute("failed", True)
                    # Continue processing other items

        batch_span.set_attribute("success_count", len(results))

    return {"processed": len(results)}
```

### Tracing Across MCP Tools

Tracer is available in MCP tools too:

```python
mcp = create_mcp_app()
tracing = create_tracing_app()

@mcp.tool(description="Fetch item with tracing")
def fetch_item_tool(
    client: CogniteClient,
    tracer: FunctionTracer,
    item_id: int
) -> dict:
    with tracer.span("mcp_fetch_item"):
        with tracer.span("validate_permissions"):
            # Check permissions
            pass

        with tracer.span("fetch_from_cdf"):
            return client.assets.retrieve(id=item_id).dump()

handle = create_function_service(tracing, mcp, app)
```

## Best Practices

### Span Naming

**Yes** **Good span names:**

- `fetch_user_profile`
- `validate_order_items`
- `calculate_shipping_cost`
- `save_to_database`

**Avoid:** **Avoid:**

- `step1`, `step2`, `step3` (not descriptive)
- `do_stuff`, `process` (too vague)
- `line_42_function` (implementation detail)

### Span Granularity

**Yes** **Create spans for:**

- External API calls
- Database queries
- Complex calculations
- Business logic boundaries
- I/O operations

**Avoid:** **Don't over-trace:**

- Simple variable assignments
- Logging statements
- Every function call
- Trivial operations

### Attribute Naming

Use OpenTelemetry semantic conventions where applicable:

```python
# Good: Follow semantic conventions
span.set_attribute("http.method", "POST")
span.set_attribute("http.status_code", 200)
span.set_attribute("db.system", "postgresql")

# Good: Custom attributes with namespaces
span.set_attribute("myapp.customer_id", customer_id)
span.set_attribute("myapp.order_total", 99.99)
```

### Performance Considerations

- Spans have minimal overhead (~microseconds per span)
- BatchSpanProcessor exports asynchronously (non-blocking)
- Reasonable span count: 10-100 spans per request
- Avoid creating thousands of spans per request

### Error Handling

Always let exceptions propagate through spans:

```python
# Good: Exception is automatically recorded
with tracer.span("operation"):
    might_fail()  # Exception propagates and is recorded

# Avoid: Silent failure
with tracer.span("operation"):
    try:
        might_fail()
    except Exception:
        pass  # Error is hidden from traces
```

### Attribute Values

Keep attribute values reasonable:

```python
# Good: Scalar values
span.set_attribute("user_id", "12345")
span.set_attribute("count", 42)
span.set_attribute("is_premium", True)

# Avoid: Large objects (they'll be stringified)
span.set_attribute("full_request", large_dict)  # Bad: too large
span.set_attribute("request_size", len(str(large_dict)))  # Good: summary
```

## Troubleshooting

### Traces Not Appearing in Backend

**Problem**: No traces visible in LightStep/Jaeger/backend UI

**Solutions**:

1. **Verify collector is running**:

   ```bash
   # For LightStep Satellite
   curl http://localhost:8360/health

   # For Jaeger
   curl http://localhost:16686/
   ```

2. **Check OTLP endpoint configuration**:

   ```python
   # Ensure correct endpoint
   tracing = create_tracing_app(
       otlp_endpoint="http://localhost:8360",
       insecure=True  # For local development
   )
   ```

3. **Ensure `TracingApp` is included in composition**:

   ```python
   handle = create_function_service(tracing, app)  # tracing must be included
   ```

4. **Verify network connectivity**: Ensure your function can reach the OTLP endpoint (check firewall, network policies)

5. **Check collector logs**: Look for connection errors or rejected spans

### Spans Missing Metadata

**Problem**: Traces don't have `cognite.call_id` or other expected attributes

**Solution**: Ensure you're using `@tracing.trace()` decorator for automatic metadata:

```python
# With decorator - automatic metadata
@tracing.trace()
def handler(tracer: FunctionTracer): ...

# Without decorator - manual metadata
def handler(tracer: FunctionTracer, function_call_info: FunctionCallInfo):
    with tracer.span("root") as span:
        span.set_attribute("cognite.call_id", function_call_info["call_id"])
```

### Missing Parent-Child Relationships

**Problem**: Spans appear as siblings instead of parent-child

**Solution**: Create child spans within parent span's context:

```python
# Correct: Child spans inside parent
with tracer.span("parent"):
    with tracer.span("child1"):  # Child of parent
        pass
    with tracer.span("child2"):  # Also child of parent
        pass

# Wrong: Spans as siblings
with tracer.span("span1"):
    pass
with tracer.span("span2"):  # Sibling, not child
    pass
```

### High Memory Usage

**Problem**: Memory grows during long-running function

**Solution**: This shouldn't happen with the current architecture (single TracerProvider). If you see this:

1. Verify you're on the latest version
2. Check that you're not calling `setup_global_tracer_provider()` repeatedly
3. Ensure reasonable span count per request (< 1000)

### Traces Not Appearing Immediately

**Problem**: Spans don't appear immediately in backend

**Expected Behavior**: `BatchSpanProcessor` exports spans in batches every few seconds. This is normal and intentional for performance.

**For immediate flush** (testing only):

```python
from opentelemetry import trace

tracer_provider = trace.get_tracer_provider()
tracer_provider.force_flush()  # Force immediate export
```

### Connection Refused / OTLP Export Errors

**Problem**: Errors about connection refused or OTLP export failures

**Solutions**:

1. **Verify collector is running**:

   ```bash
   docker ps | grep lightstep
   # or
   docker ps | grep jaeger
   ```

2. **Check endpoint URL**: Ensure it matches your collector:
   - LightStep Satellite: `http://localhost:8360`
   - Jaeger OTLP: `http://localhost:4317`

3. **Use correct protocol**: OTLP/gRPC typically uses different ports than HTTP
   - gRPC: 4317 (Jaeger), 8360 (LightStep Satellite)
   - HTTP: 4318 (Jaeger OTLP/HTTP)

4. **Check firewall rules**: Ensure the collector port is accessible

## Viewing Traces

### LightStep Developer Satellite

Access the LightStep UI at the web port (typically configured when starting the satellite):

```bash
# Start with web UI on port 9411
docker run -p 8360:8360 -p 9411:9411 lightstep/lightstep-satellite-dev:latest
```

Then browse to `http://localhost:9411` to view traces.

### Jaeger

Access Jaeger UI at `http://localhost:16686`:

```bash
# Start Jaeger all-in-one
docker run -d --name jaeger \
  -p 4317:4317 \
  -p 16686:16686 \
  jaegertracing/all-in-one:latest
```

### Querying Traces

Use your backend's UI to:

- Search traces by `trace_id`
- Filter by attributes (e.g., `cognite.call_id`, `cognite.function_id`)
- Analyze latency distributions
- Find error traces
- Compare traces across time

Example queries:

- Find all traces for a specific function: `cognite.function_id=<id>`
- Find failed requests: `http.status_code>=500`
- Find slow operations: duration > 1s

## Next Steps

- Check out the [main documentation](index.md) for overall framework documentation
- Learn about [Dependency Injection](dependency-injection.md) to understand how tracer is provided
- Explore [Model Context Protocol (MCP)](mcp.md) for AI tool integration with tracing
