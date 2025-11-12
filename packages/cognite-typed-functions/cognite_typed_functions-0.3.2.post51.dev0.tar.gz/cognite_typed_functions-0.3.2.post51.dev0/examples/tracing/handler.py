"""LightStep Cloud tracing example for Cognite Typed Functions.

This example demonstrates comprehensive distributed tracing with LightStep Cloud,
showing how to:

1. Configure a custom OTLP exporter with secure secret management
2. Use TracingApp middleware for automatic root span creation
3. Create child spans with the FunctionTracer DI parameter
4. Apply @tracing.trace() decorator to helper functions for organized trace hierarchies
5. Test locally with .env file secrets and deploy to production with CDF secrets

Key Components:
    - create_lightstep_exporter(): Custom exporter provider using DI for secrets
    - fetch_item_data(): Helper function demonstrating @tracing.trace() with child spans
    - validate_item_name(): Simple helper demonstrating @tracing.trace() for single span
    - get_item(): Route handler showing helper function integration (no decorator)
    - create_item(): Route handler with @tracing.trace() decorator and helpers

Trace Hierarchies:
    GET /items/{id}:
        ├─ fetch_item_data (@tracing.trace() on helper)
        │   └─ database_query (tracer.span() inside helper)
        └─ process_data (tracer.span() in route handler)

    POST /items:
        └─ create_item (@tracing.trace() on route handler)
            ├─ validate_input (tracer.span())
            │   └─ validate_item_name (@tracing.trace() on helper)
            └─ save_to_cdf (tracer.span())

See README.md for complete setup instructions and deployment guide.
"""

from collections.abc import Mapping

from cognite.client import CogniteClient
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from pydantic import BaseModel

from cognite_typed_functions import (
    FunctionApp,
    FunctionTracer,
    create_function_service,
    create_introspection_app,
    create_tracing_app,
)


# Define response model
class Item(BaseModel):
    """Item response model."""

    id: int
    name: str
    description: str


# Custom LightStep Cloud exporter provider
def create_lightstep_exporter(secrets: Mapping[str, str]):
    """Create OTLP exporter for LightStep Cloud.

    The secrets parameter is automatically injected by the DI framework.
    This function is called once on the first request to initialize tracing.

    Args:
        secrets: Secrets mapping injected by DI framework. Must contain lightstep-token.

    Returns:
        Configured OTLPSpanExporter for LightStep Cloud

    Raises:
        ValueError: If lightstep-token is not provided in secrets
    """
    token = secrets.get("lightstep-token")
    if not token:
        raise ValueError(
            "lightstep-token secret is required for LightStep Cloud tracing. "
            "Use --secrets flag with a file containing lightstep-token=your-token for local testing."
        )

    return OTLPSpanExporter(
        endpoint="https://ingest.lightstep.com:443",
        headers={"lightstep-access-token": token},
    )


# Create tracing app with custom exporter provider
tracing = create_tracing_app(
    exporter_provider=create_lightstep_exporter,
    service_name="lightstep-example-function",
    service_version="1.0.0",
)

# Create introspection app for API documentation
introspection = create_introspection_app()

# Create main application
app = FunctionApp(title="LightStep Example API", version="1.0.0")


# Helper functions with @tracing.trace() decorator
# These are not route handlers, but business logic functions
@tracing.trace()
def fetch_item_data(tracer: FunctionTracer, item_id: int) -> tuple[str, str]:
    """Fetch item data from external source.

    This helper function uses @tracing.trace() to create a span for the
    entire function execution. Any tracer.span() calls inside will be
    children of this function span.

    Args:
        tracer: Function tracer (injected by DI)
        item_id: ID of the item to fetch

    Returns:
        Tuple of (name, description)
    """
    with tracer.span("database_query") as span:
        span.set_attribute("query.type", "select")
        span.set_attribute("query.item_id", item_id)
        # Simulate database query
        name = f"Asset_{item_id}"
        description = f"Description for asset {item_id}"

    return name, description


@tracing.trace()
def validate_item_name(name: str) -> None:
    """Validate item name meets requirements.

    This helper function is traced as a single span since it doesn't
    use tracer.span() internally. The @tracing.trace() decorator creates
    a span that captures the entire function execution.

    Args:
        name: Name to validate

    Raises:
        ValueError: If name is invalid
    """
    if not name or len(name) < 3:
        raise ValueError("Name must be at least 3 characters")
    if len(name) > 100:
        raise ValueError("Name must be less than 100 characters")


@app.get("/items/{item_id}")
def get_item(
    client: CogniteClient,
    tracer: FunctionTracer,  # ← Injected by DI for creating child spans
    item_id: int,
) -> Item:
    """Get an item by ID with distributed tracing.

    This endpoint demonstrates how tracing works:

    1. TracingApp middleware (automatic):
       - Creates root span "GET /items/{item_id}" for EVERY request
       - Includes http.method, http.route, cognite.call_id, etc.
       - No code needed - happens when you compose with TracingApp

    2. tracer: FunctionTracer parameter:
       - Injected via DI (like client, logger)
       - Used to create child spans with tracer.span()
       - Works WITHOUT needing @tracing.trace() decorator

    3. Helper functions with @tracing.trace():
       - fetch_item_data() uses @tracing.trace() decorator
       - Creates a span for the helper function
       - Helper's tracer.span() calls become children of the helper's span

    Span hierarchy:
        GET /items/{item_id}           ← Root (TracingApp middleware)
          ├─ fetch_item_data           ← Helper function (@tracing.trace())
          │   └─ database_query        ← Child of helper (tracer.span())
          └─ process_data              ← Child (tracer.span())

    Args:
        client: Cognite client (injected by DI)
        tracer: Function tracer for creating child spans (injected by DI)
        item_id: ID of the item to retrieve

    Returns:
        Item details
    """
    # Call helper function - it will create its own traced span
    # The @tracing.trace() decorator on fetch_item_data creates a span
    item_name, item_description = fetch_item_data(tracer, item_id)

    # Create a child span for processing
    with tracer.span("process_data") as span:
        span.set_attribute("processing.step", "transform")
        span.set_attribute("item.id", item_id)

        # Create the response
        result = Item(
            id=item_id,
            name=item_name,
            description=item_description,
        )

    return result


@app.post("/items")
@tracing.trace()  # ← OPTIONAL: Adds extra "create_item" function-level span
def create_item(
    client: CogniteClient,
    tracer: FunctionTracer,
    name: str,
    description: str,
) -> Item:
    """Create a new item with distributed tracing.

    This endpoint uses the @tracing.trace() decorator on the route handler
    AND calls a helper function (validate_item_name) that also uses
    @tracing.trace(). This demonstrates nested traced functions.

    Span hierarchy WITH decorator and helper functions:
        POST /items                    ← Root (TracingApp middleware)
          └─ create_item               ← Function span (@tracing.trace())
              ├─ validate_input        ← Child (tracer.span())
              │   └─ validate_item_name← Helper function (@tracing.trace())
              └─ save_to_cdf           ← Child (tracer.span())

    Args:
        client: Cognite client (injected by DI)
        tracer: Function tracer (injected by DI)
        name: Name of the item
        description: Description of the item

    Returns:
        Created item details
    """
    with tracer.span("validate_input") as span:
        span.set_attribute("validation.name_length", len(name))
        span.set_attribute("validation.desc_length", len(description))

        # Call helper function - creates a child span due to @tracing.trace()
        validate_item_name(name)

    with tracer.span("save_to_cdf") as span:
        # In a real function:
        # asset = client.assets.create(Asset(name=name, description=description))
        # item_id = asset.id

        # For this example:
        item_id = 999
        span.set_attribute("item.id", item_id)

    return Item(id=item_id, name=name, description=description)


# Compose the apps
# Order matters: introspection first so it can see all apps, then tracing middleware, then main app
handle = create_function_service(introspection, tracing, app)
