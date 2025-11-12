# API Reference

Complete API documentation for the Cognite Typed Functions framework.

## Quick Reference

### Basic Usage Pattern

```python
from cognite_typed_functions import FunctionApp, create_function_service
from cognite.client import CogniteClient
from pydantic import BaseModel

# Create app
app = FunctionApp(title="My API", version="1.0.0")

# Define models
class Item(BaseModel):
    name: str
    price: float

# Define endpoints
@app.get("/items/{item_id}")
def get_item(client: CogniteClient, item_id: int) -> dict:
    """Retrieve an item by ID"""
    return {"id": item_id}

@app.post("/items/")
def create_item(client: CogniteClient, item: Item) -> dict:
    """Create a new item"""
    return {"id": 123, "item": item.model_dump()}

# Create service
handle = create_function_service(app)
```

### Common Patterns

#### Route Decorators

```python
@app.get(path)      # Retrieve data
@app.post(path)     # Create or process data
@app.put(path)      # Update resources
@app.delete(path)   # Delete resources
```

#### Handler Parameters

```python
@app.post("/categories/{category_id}/items")
def create_item(
    client: CogniteClient,              # Framework dependency (required)
    logger: logging.Logger,             # Framework dependency (optional)
    category_id: int,                   # Path parameter
    item: Item,                         # Request body
    notify: bool = False                # Query parameter
) -> dict:
    return {"category_id": category_id, "item": item.model_dump()}
```

#### Service Creation

```python
# Single app
handle = create_function_service(app)

# Multiple apps (composition)
handle = create_function_service(introspection, main_app)

# With custom dependencies
handle = create_function_service(app, registry=custom_registry)
```

### Request/Response Format

**Request:**
```python
{
    "path": "/items/123?include_tax=true",
    "method": "GET",
    "body": {...}  # Optional
}
```

**Success Response:**
```python
{
    "success": true,
    "data": {...}
}
```

**Error Response:**
```python
{
    "success": false,
    "error_type": "ValidationError",
    "message": "Input validation failed",
    "details": {...}
}
```

See [Error Handling](error-handling.md) for complete error documentation.

## Detailed API Reference

The following sections provide complete API documentation auto-generated from the source code.

### Core Classes

#### FunctionApp

::: cognite_typed_functions.FunctionApp
    options:
      show_root_heading: true
      show_source: false
      members_order: source
      show_signature_annotations: true

### Service Creation

#### create_function_service

::: cognite_typed_functions.create_function_service
    options:
      show_root_heading: true
      show_source: false
      show_signature_annotations: true

### Dependency Injection

#### DependencyRegistry

::: cognite_typed_functions.dependency_registry.DependencyRegistry
    options:
      show_root_heading: true
      show_source: false
      members_order: source

#### create_default_registry

::: cognite_typed_functions.create_default_registry
    options:
      show_root_heading: true
      show_source: false

### Introspection

#### create_introspection_app

::: cognite_typed_functions.introspection.create_introspection_app
    options:
      show_root_heading: true
      show_source: false

### Model Context Protocol

#### create_mcp_app

::: cognite_typed_functions.mcp.create_mcp_app
    options:
      show_root_heading: true
      show_source: false

#### MCPApp

::: cognite_typed_functions.mcp.MCPApp
    options:
      show_root_heading: true
      show_source: false
      members:
        - tool

### Distributed Tracing

#### create_tracing_app

::: cognite_typed_functions.tracer.create_tracing_app
    options:
      show_root_heading: true
      show_source: false

#### FunctionTracer

::: cognite_typed_functions.tracer.FunctionTracer
    options:
      show_root_heading: true
      show_source: false
      members:
        - span

### Function Client

#### FunctionClient

::: cognite_typed_functions.FunctionClient
    options:
      show_root_heading: true
      show_source: false
      members_order: source
      members:
        - discover
        - describe
        - materialize

### Development Server

#### create_asgi_app

::: cognite_typed_functions.devserver.create_asgi_app
    options:
      show_root_heading: true
      show_source: false

### Models and Types

#### FunctionCallInfo

Type alias for function execution metadata:

```python
from cognite_typed_functions.models import FunctionCallInfo

# FunctionCallInfo is dict[str, Any] with these keys:
{
    "function_id": int,           # Function ID in CDF
    "call_id": int,               # Unique call identifier
    "schedule_id": int | None,    # Schedule ID if scheduled execution
    "scheduled_time": str | None  # Scheduled execution time
}
```

#### Handler

Type alias for the service handler function:

```python
from cognite_typed_functions.models import Handler

# Handler signature:
def handle(
    client: CogniteClient,
    data: dict,
    secrets: dict[str, str] | None = None,
    function_call_info: dict | None = None
) -> dict:
    """
    Compatible with Cognite Functions platform.
    
    Args:
        client: Authenticated CogniteClient
        data: Request data (path, method, body)
        secrets: Function secrets
        function_call_info: Execution metadata
    
    Returns:
        Structured response dict
    """
```

## See Also

- [Type Safety](type-safety.md) - Type validation and conversion
- [Error Handling](error-handling.md) - Structured error responses
- [Dependency Injection](dependency-injection.md) - Custom dependencies
- [App Composition](app-composition.md) - Composing multiple apps
- [Introspection](introspection.md) - Built-in introspection endpoints
- [Model Context Protocol](mcp.md) - MCP integration

