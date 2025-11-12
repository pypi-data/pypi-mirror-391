# Error Handling

The framework provides structured error handling with detailed information for debugging.

## Error Types

The framework defines several error types for different failure scenarios:

- **RouteNotFound** - No matching route found for the request
- **ValidationError** - Input validation failed (Pydantic validation errors)
- **TypeConversionError** - Parameter type conversion failed
- **ExecutionError** - Function execution failed (unhandled exceptions)

## Response Format

All responses follow a consistent structure for both success and error cases.

### Success Response

```python
{
    "success": true,
    "data": {...}  # Your actual response data
}
```

### Error Response

```python
{
    "success": false,
    "error_type": "ValidationError",
    "message": "Input validation failed: 1 error(s)",
    "details": {"errors": [...]}
}
```

## Error Examples

### Validation Error

When input data fails Pydantic validation:

```python
# Request
{
    "path": "/items/",
    "method": "POST",
    "body": {
        "name": "Widget",
        "price": "not-a-number"  # Invalid price
    }
}

# Response
{
    "success": false,
    "error_type": "ValidationError",
    "message": "Input validation failed: 1 error(s)",
    "details": {
        "errors": [
            {
                "loc": ["price"],
                "msg": "value is not a valid float",
                "type": "type_error.float"
            }
        ]
    }
}
```

### Route Not Found

When no route matches the request:

```python
# Request
{
    "path": "/nonexistent",
    "method": "GET"
}

# Response
{
    "success": false,
    "error_type": "RouteNotFound",
    "message": "No route found for GET /nonexistent",
    "details": {}
}
```

### Type Conversion Error

When a path or query parameter cannot be converted to the expected type:

```python
# Request
{
    "path": "/items/not-a-number",  # item_id should be int
    "method": "GET"
}

# Response
{
    "success": false,
    "error_type": "TypeConversionError",
    "message": "Failed to convert parameter 'item_id' to type <class 'int'>",
    "details": {
        "parameter": "item_id",
        "expected_type": "int",
        "value": "not-a-number"
    }
}
```

### Execution Error

When an unhandled exception occurs during handler execution:

```python
# Response
{
    "success": false,
    "error_type": "ExecutionError",
    "message": "Function execution failed: division by zero",
    "details": {
        "exception_type": "ZeroDivisionError",
        "traceback": "..."
    }
}
```

## Error Handling in Handlers

You can raise exceptions in your handlers, and the framework will catch them and return structured error responses:

```python
from cognite_typed_functions import FunctionApp

app = FunctionApp(title="My API", version="1.0.0")

@app.get("/items/{item_id}")
def get_item(client: CogniteClient, item_id: int) -> dict:
    """Retrieve an item by ID"""
    
    # Validation errors are handled automatically
    if item_id < 0:
        raise ValueError("Item ID must be positive")
    
    # The framework catches exceptions and returns structured errors
    item = fetch_item(item_id)  # May raise exception
    
    return {"id": item_id, "data": item}
```

## Custom Error Handling

For more control over error responses, you can catch exceptions and return custom error data:

```python
@app.post("/items/")
def create_item(client: CogniteClient, item: Item) -> dict:
    """Create a new item"""
    try:
        result = create_in_database(item)
        return {"success": True, "id": result.id}
    except DatabaseError as e:
        # Return custom error information
        return {
            "success": False,
            "error": "Database operation failed",
            "details": str(e)
        }
```

## Best Practices

1. **Use Pydantic models** - Let the framework handle input validation automatically
2. **Raise descriptive exceptions** - Error messages are included in the response
3. **Log errors** - Use the [injected logger](logging.md) to log errors for debugging
4. **Don't catch everything** - Let the framework handle unexpected errors with proper structure
5. **Return structured data** - Even for success cases, return consistent data structures

## See Also

- [Type Safety](type-safety.md) - Understanding type validation and conversion
- [Logging](logging.md) - Logging errors for debugging
- [API Reference](api-reference.md) - Complete API documentation

