# LightStep Cloud Tracing Example

This example demonstrates how to use LightStep Cloud for distributed tracing with Cognite Typed Functions, including secure secret management using the dependency injection framework.

## What This Example Shows

- **Custom Tracing Exporter**: Create a custom OTLP exporter for LightStep Cloud
- **Secrets via DI**: Use the dependency injection framework to securely access secrets
- **Lazy Initialization**: Exporter is created on first request when secrets are available
- **Local Testing**: Test with secrets from `.env` file using the dev server
- **Production Ready**: Same code works in production with CDF secret management
- **Automatic Tracing**: TracingApp middleware creates root spans for every request
- **Manual Child Spans**: `tracer: FunctionTracer` parameter for business logic tracing
- **Optional Decorator**: `@tracing.trace()` adds extra function-level span (not required)

## Setup

### 1. Configure Authentication

**CDF Authentication** (environment variables):

Set these in your shell to connect to Cognite Data Fusion:

```bash
export COGNITE_CLIENT_ID=your-client-id
export COGNITE_CLIENT_SECRET=your-client-secret
export COGNITE_TENANT_ID=your-tenant-id
export COGNITE_PROJECT=your-project
```

**Function Secrets** (secrets file):

Create a secrets file (e.g., `secrets.env`) for secrets that get injected into your function:

```bash
# Create a secrets file
cat > secrets.env << EOF
lightstep-token=YOUR_ACTUAL_LIGHTSTEP_TOKEN
EOF
```

Your secrets file should contain key-value pairs directly (no prefix):

```bash
# Function secrets (injected into your function's secrets parameter)
lightstep-token=YOUR_ACTUAL_LIGHTSTEP_TOKEN
```

**Important:** 
- Never commit your secrets file! Add it to `.gitignore`.
- CDF auth goes in environment variables, NOT in the secrets file
- The secrets file contains only function secrets (keys match the secret names used in code)

### 2. Install Dependencies

```bash
# Install with tracing support
pip install cognite-typed-functions[cli,tracing]
# or with uv
uv add cognite-typed-functions --extra cli --extra tracing
```

## Running Locally

### Start the Development Server

```bash
# From the repository root
ctf serve examples/tracing --secrets secrets.env

# Or with uv
uv run ctf serve examples/tracing --secrets secrets.env
```

The server will:
1. Load authentication from environment variables
2. Load secrets from the specified secrets file
3. Start on http://localhost:8000
4. Initialize LightStep tracing on the first request

### Test the Endpoints

```bash
# GET request (with tracing)
curl http://localhost:8000/items/123

# POST request (with tracing)
curl -X POST http://localhost:8000/items \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Item", "description": "A test item with tracing"}'
```

### View Traces in LightStep

1. Open https://app.lightstep.com
2. Navigate to "Explorer" or "Traces"
3. You should see traces from your function with:
   - Service name: `lightstep-example-function`
   - Root span with HTTP metadata
   - Child spans for business logic
   - Custom attributes (item.id, operation.type, etc.)

## How It Works

### How Tracing Works

**Important:** TracingApp middleware automatically creates root spans for every request. The decorator is optional.

**1. TracingApp Middleware (Automatic - Always Active):**
```python
handle = create_function_service(tracing, app)

# Now EVERY request gets a root span automatically:
# - http.method, http.route, http.status_code
# - cognite.call_id, cognite.function_id
```

**2. `tracer: FunctionTracer` (DI Parameter - For Child Spans):**
```python
@app.get("/items/{id}")
def get_item(tracer: FunctionTracer, id: int):  # ← Injected by DI
    # Root span already exists from TracingApp middleware!
    
    # Create child spans for business logic
    with tracer.span("fetch_from_database"):  # ← Child of root
        data = db.query(id)
    
    with tracer.span("transform"):  # ← Child of root
        result = transform(data)
    
    return result
```

**Span hierarchy:**
```
GET /items/{id}              ← Root (TracingApp middleware - automatic)
  ├─ fetch_from_database     ← Child (tracer.span())
  └─ transform               ← Child (tracer.span())
```

**3. `@tracing.trace()` Decorator (Optional - Adds Function-Level Span):**
```python
@app.get("/items/{id}")
@tracing.trace()  # ← OPTIONAL: Adds extra "get_item" span
def get_item(tracer: FunctionTracer, id: int):
    with tracer.span("fetch"):
        data = fetch(id)
    return data
```

**With decorator:**
```
GET /items/{id}              ← Root (TracingApp middleware)
  └─ get_item                ← Function span (@tracing.trace())
      └─ fetch               ← Child (tracer.span())
```

**Key Takeaway:** The middleware handles root spans. Use `tracer` for child spans. The decorator is optional.

### Using `@tracing.trace()` on Helper Functions

The `@tracing.trace()` decorator is especially useful for tracing business logic functions that are called by your route handlers. This creates clean, organized trace hierarchies.

**Helper Function Pattern:**

```python
@tracing.trace()
def fetch_item_data(tracer: FunctionTracer, item_id: int) -> tuple[str, str]:
    """Fetch item data with tracing.
    
    The @tracing.trace() decorator creates a span for the entire function.
    Any tracer.span() calls inside become children of this function span.
    """
    with tracer.span("database_query") as span:
        span.set_attribute("query.item_id", item_id)
        # ... fetch data ...
        return name, description

@tracing.trace()
def validate_item_name(name: str) -> None:
    """Validate item name.
    
    Simple helper without internal spans - the decorator creates
    a single span capturing the entire validation logic.
    """
    if not name or len(name) < 3:
        raise ValueError("Name must be at least 3 characters")
```

**Calling from Route Handlers:**

```python
@app.get("/items/{id}")
def get_item(tracer: FunctionTracer, id: int) -> Item:
    # Helper function creates its own span
    name, desc = fetch_item_data(tracer, id)
    
    # Manual span in route handler
    with tracer.span("process_data"):
        result = process(name, desc)
    
    return result
```

**Resulting Trace Hierarchy:**

```
GET /items/{id}              ← Root (TracingApp middleware - automatic)
  ├─ fetch_item_data         ← Helper function (@tracing.trace())
  │   └─ database_query      ← Child span inside helper (tracer.span())
  └─ process_data            ← Route handler span (tracer.span())
```

**Key Points:**

1. **Helper functions can use DI**: Pass `tracer: FunctionTracer` as a parameter just like in route handlers
2. **Decorator creates parent span**: The `@tracing.trace()` decorator automatically creates a span named after the function
3. **Nested spans work naturally**: Any `tracer.span()` calls inside become children of the decorator's span
4. **No tracer needed for simple functions**: If your helper doesn't need child spans, omit the `tracer` parameter
5. **Works with any function**: Use on business logic, validators, transformers, database queries, etc.

**When to Use `@tracing.trace()` on Helpers:**

✅ **DO use it for:**
- Business logic functions called by route handlers
- Functions with complex internal operations
- Functions you want to monitor individually in traces
- Functions that make external API/database calls

❌ **DON'T use it for:**
- Simple utility functions (string formatting, math calculations)
- Functions called thousands of times per request (too noisy)
- Pure data transformations without I/O

### Custom Exporter with Secrets

The key part is the exporter provider function that uses DI:

```python
def create_lightstep_exporter(secrets: Mapping[str, str]):
    """Create OTLP exporter for LightStep Cloud.
    
    Secrets are automatically injected by the DI framework.
    """
    # Get the token from secrets (key matches the secret name in your secrets file)
    token = secrets.get("lightstep-token")
    if not token:
        raise ValueError("lightstep-token secret is required")
    
    return OTLPSpanExporter(
        endpoint="https://ingest.lightstep.com:443",
        headers={"lightstep-access-token": token},
    )

# Pass the provider to create_tracing_app
tracing = create_tracing_app(
    exporter_provider=create_lightstep_exporter,
    service_name="lightstep-example-function",
)
```

### Local vs Production

**Local Development:**
- **CDF Authentication**: Set via environment variables (`COGNITE_CLIENT_ID`, etc.)
- **Function Secrets**: Loaded from secrets file specified with `--secrets` flag
  - Create a file (e.g., `secrets.env`) with `lightstep-token=your-token`
  - Use `ctf serve examples/tracing --secrets secrets.env`
  - Keys in the file match the secret names used in code

**Production Deployment:**
- **CDF Authentication**: Managed by Cognite Functions platform automatically
- **Function Secrets**: Configure in CDF Function settings:
  - Key: `lightstep-token`
  - Value: Your actual token
- CDF injects secrets into your function
- Same code works without changes!

## Trace Examples

### GET /items/{id} (Without Decorator, With Helper Functions)

The `get_item` handler does NOT use `@tracing.trace()` on the route handler - it relies on automatic root spans. However, it calls helper functions that DO use `@tracing.trace()`:

```
GET /items/{id}              ← Root span (TracingApp middleware - automatic)
  ├─ fetch_item_data         ← Helper function (@tracing.trace())
  │   └─ database_query      ← Child of helper (tracer.span())
  └─ process_data            ← Child span (tracer.span())
```

Root span includes: `http.method`, `http.route`, `cognite.call_id`, `cognite.function_id`

### POST /items (With Decorator and Helper Functions)

The `create_item` handler DOES use `@tracing.trace()` on the route handler AND calls a helper function that also uses `@tracing.trace()`:

```
POST /items                  ← Root span (TracingApp middleware - automatic)
  └─ create_item             ← Function span (@tracing.trace() - optional)
      ├─ validate_input      ← Child span (tracer.span())
      │   └─ validate_item_name ← Helper function (@tracing.trace())
      └─ save_to_cdf         ← Child span (tracer.span())
```

**Comparison:** Both approaches work. The decorator on the route handler adds an extra layer but isn't required. Using `@tracing.trace()` on helper functions is recommended for organizing trace hierarchies.

## Deploying to Production

### 1. Configure Function Secret in CDF

In the Cognite Data Fusion console:

1. Navigate to your Function
2. Go to "Secrets" section
3. Add a new secret:
   - **Name**: `lightstep-token`
   - **Value**: Your LightStep access token
4. Save and deploy

### 2. Deploy Your Function

The same code works in production! The only difference is where secrets come from:
- **Local**: Secrets file specified with `--secrets` flag
- **Production**: CDF secret management

### 3. Verify in LightStep

After deployment:
1. Trigger your function in CDF
2. Check LightStep Cloud for traces
3. Traces will include `cognite.function_id` and `cognite.call_id` attributes

## Troubleshooting

### No traces appearing in LightStep

1. **Check token**: Verify your LightStep access token is correct
2. **Check secrets file**: Ensure your secrets file has `lightstep-token=your-token` (no prefix)
3. **Check CLI flag**: Make sure you're using `--secrets <path>` flag when starting the server
4. **Check logs**: Look for "Loaded N secrets" message on startup
5. **Check connectivity**: Ensure you can reach https://ingest.lightstep.com:443

### Secret not found error

```
ValueError: lightstep-token secret is required
```

**Solution**: Make sure your secrets file has:
```bash
lightstep-token=your-actual-token
```

And start the server with the `--secrets` flag:
```bash
ctf serve examples/tracing --secrets secrets.env
```

### Traces work locally but not in production

1. Verify the secret is configured in CDF Function settings
2. Check the secret name is `lightstep-token` (matches the key used in your secrets file)
3. Review function logs for initialization errors

## Security Best Practices

✅ **DO:**
- Add `.env` to `.gitignore` (already done)
- Use `.env.example` or `.env.lightstep.example` for documentation
- Configure real tokens only in `.env` (never in code)
- Use different tokens for dev/staging/production

❌ **DON'T:**
- Commit `.env` files with real tokens
- Hardcode tokens in source code
- Share tokens in documentation or examples
- Use production tokens for local development

## Next Steps

- Explore the [full tracing documentation](../docs/tracing.md)
- Learn about [custom exporters with other backends](../docs/tracing.md#custom-exporters-with-secrets)
- Try adding more custom spans and attributes to your code
- Set up alerts and dashboards in LightStep Cloud

## Need Help?

- LightStep Documentation: https://docs.lightstep.com
- Cognite Typed Functions: See main [README](../README.md)
- Issues: Open an issue on GitHub

