"""Tracing support for Cognite Functions using dependency injection.

This module provides tracing capabilities through dependency injection,
making it available as a standard parameter like client, logger, etc.

Architecture:
- TracerProvider is configured once at application startup (not per-request)
- OTLPSpanExporter sends traces to OpenTelemetry collector (e.g., LightStep)
- BatchSpanProcessor handles async export without blocking requests
- No per-request setup/teardown to avoid resource leaks
- Spans include cognite.call_id attribute for filtering/organization in backend

Note:
    Tracing support requires the optional 'tracing' dependencies:
    pip install cognite-typed-functions[tracing]
"""

import inspect
import threading
import warnings
from collections.abc import Callable, Coroutine
from contextlib import contextmanager
from functools import wraps
from typing import TYPE_CHECKING, Any, ParamSpec, TypedDict, TypeVar, cast, overload

from cognite_typed_functions.app import FunctionApp
from cognite_typed_functions.dependency_registry import DependencyRegistry
from cognite_typed_functions.models import (
    ASGIReceiveCallable,
    ASGISendCallable,
    ASGITypedFunctionResponseMessage,
    ASGITypedFunctionScope,
    DataDict,
)

# Make sure this is short enough to avoid blocking the function execution, but long enough to ensure the spans are
# exported before the function instance is recycled.
FLUSH_TIMEOUT_MS = 500

# Try to import OpenTelemetry dependencies
_has_opentelemetry = True
try:
    from opentelemetry import trace
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.sdk.trace import TracerProvider as SdkTracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor, SpanExporter
    from opentelemetry.trace import ProxyTracerProvider, Status, StatusCode
except ImportError:
    _has_opentelemetry = False
    if not TYPE_CHECKING:
        # Provide stubs for runtime when OpenTelemetry is not installed
        trace = None  # type: ignore[assignment]
        OTLPSpanExporter = Any  # type: ignore[assignment]
        Resource = Any  # type: ignore[assignment]
        SdkTracerProvider = Any  # type: ignore[assignment]
        BatchSpanProcessor = Any  # type: ignore[assignment]
        SpanExporter = Any  # type: ignore[assignment]
        ProxyTracerProvider = Any  # type: ignore[assignment]
        Status = Any  # type: ignore[assignment]
        StatusCode = Any  # type: ignore[assignment]

if TYPE_CHECKING:
    # Always import for type checking
    from opentelemetry import trace as trace
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.sdk.trace import TracerProvider as SdkTracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor, SpanExporter
    from opentelemetry.trace import ProxyTracerProvider, Status, StatusCode

_P = ParamSpec("_P")
_R = TypeVar("_R")


class _ResponseState(TypedDict):
    """Internal response state for tracing."""

    has_started: bool
    body: DataDict | None


class FunctionTracer:
    """Tracer for Cognite Functions with OpenTelemetry integration.

    Provides a simple interface for creating traced spans that are automatically
    exported to an OpenTelemetry collector (e.g., LightStep, Jaeger, etc.).
    """

    def __init__(self, tracer: "trace.Tracer") -> None:
        """Initialize the FunctionTracer.

        Args:
            tracer: OpenTelemetry Tracer instance

        Raises:
            ImportError: If OpenTelemetry is not installed
        """
        if not _has_opentelemetry:
            raise ImportError(
                "Tracing support requires OpenTelemetry. Install it with: pip install cognite-typed-functions[tracing]"
            )
        self.tracer = tracer

    @contextmanager
    def span(self, name: str):
        """Create a traced span.

        Usage:
            with tracer.span("database_query"):
                result = query_db()
        """
        with self.tracer.start_as_current_span(name) as span:
            # Explicitly set operation name as an attribute for better visibility in backends
            span.set_attribute("operation.name", name)
            try:
                yield span
                span.set_status(Status(StatusCode.OK))
            except Exception:
                # Re-raise to allow the OpenTelemetry context manager to handle it.
                # It will set the status to ERROR and record the exception with a stack trace.
                raise


# Overload: when exporter is provided
@overload
def setup_global_tracer_provider(
    *,
    service_name: str = "cognite-typed-functions",
    service_version: str = "1.0.0",
    exporter: "SpanExporter",
) -> "trace.TracerProvider": ...


# Overload: when otlp_endpoint is required
@overload
def setup_global_tracer_provider(
    *,
    otlp_endpoint: str,
    service_name: str = "cognite-typed-functions",
    service_version: str = "1.0.0",
    insecure: bool = False,
) -> "trace.TracerProvider": ...


def setup_global_tracer_provider(
    *,
    otlp_endpoint: str | None = None,
    service_name: str = "cognite-typed-functions",
    service_version: str = "1.0.0",
    exporter: "SpanExporter | None" = None,
    insecure: bool = False,
) -> "trace.TracerProvider":
    """Set up global TracerProvider with OTLPSpanExporter.

    This is called once at application startup to configure OpenTelemetry
    for the lifetime of the function worker. Traces are sent to an OpenTelemetry
    collector (e.g., LightStep Developer Satellite) via OTLP/gRPC.

    This function is idempotent - calling it multiple times is safe and will
    return the existing provider if already configured.

    Args:
        otlp_endpoint: OTLP endpoint URL. Required when exporter is None.
        service_name: Service name for trace identification (default: "cognite-typed-functions")
        service_version: Service version (default: "1.0.0")
        exporter: Optional custom exporter (for testing). If not provided, uses OTLPSpanExporter.
        insecure: Use insecure connection (default: False). Only set to True for local development.

    Returns:
        The configured TracerProvider instance

    Raises:
        ImportError: If OpenTelemetry is not installed
        ValueError: If exporter is None but otlp_endpoint is not provided
    """
    if not _has_opentelemetry:
        raise ImportError(
            "Tracing support requires OpenTelemetry. Install it with: pip install cognite-typed-functions[tracing]"
        )

    # Validate that otlp_endpoint is provided when exporter is None
    if exporter is None and otlp_endpoint is None:
        raise ValueError("otlp_endpoint is required when exporter is not provided")

    # Check if already configured
    existing_provider = trace.get_tracer_provider()
    if not isinstance(existing_provider, ProxyTracerProvider):
        # Already configured, log a warning and return existing provider.
        warnings.warn("TracerProvider is already configured. Subsequent configurations will be ignored.")
        return existing_provider  # type: ignore[return-value]

    # Create resource with service identification (required by LightStep and other backends)
    # Using string literals for semantic convention keys to avoid deprecation warnings
    resource = Resource.create(
        {
            "service.name": service_name,
            "service.version": service_version,
        }
    )

    # Create and configure new provider with resource
    tracer_provider = SdkTracerProvider(resource=resource)
    trace.set_tracer_provider(tracer_provider)

    # Use provided exporter or create OTLP exporter
    if exporter is None:
        # otlp_endpoint is guaranteed to be non-None here due to validation above
        assert otlp_endpoint is not None  # For type checker
        exporter = OTLPSpanExporter(endpoint=otlp_endpoint, insecure=insecure)

    batch_processor = BatchSpanProcessor(exporter)
    tracer_provider.add_span_processor(batch_processor)

    return tracer_provider  # type: ignore[return-value]


class TracingApp(FunctionApp):
    """Tracing middleware app for automatic root span creation.

    Creates a root span around every incoming request at the middleware level,
    providing comprehensive tracing coverage including error handling. Routes
    decorated with @tracing.trace() create child spans under this root span.

    This app participates in the composition lifecycle but doesn't register
    any routes of its own - it wraps downstream apps in the middleware chain
    and provides tracer dependency injection.

    Example:
        tracing = TracingApp(otlp_endpoint="http://localhost:8360")

        @app.get("/items/{id}")
        @tracing.trace()  # Creates a child span
        def get_item(tracer: FunctionTracer, id: int):
            with tracer.span("business_logic"):  # Creates a grandchild span
                return {"id": id}

        # Compose with tracing app to enable tracing middleware
        handle = create_function_service(tracing, app)
    """

    # Parameter name for tracer dependency injection
    # This must match the DI registration for consistent behavior
    # Can be overridden in subclasses for custom naming conventions
    tracer_param_name: str = "tracer"

    @overload
    def __init__(
        self,
        *,
        otlp_endpoint: str,
        exporter_provider: None = None,
        service_name: str = "cognite-typed-functions",
        service_version: str = "1.0.0",
        insecure: bool = False,
    ) -> None: ...
    @overload
    def __init__(
        self,
        *,
        otlp_endpoint: None = None,
        exporter_provider: Callable[..., "SpanExporter"],
        service_name: str = "cognite-typed-functions",
        service_version: str = "1.0.0",
        insecure: bool = False,
    ) -> None: ...
    def __init__(
        self,
        *,
        otlp_endpoint: str | None = None,
        exporter_provider: Callable[..., "SpanExporter"] | None = None,
        service_name: str = "cognite-typed-functions",
        service_version: str = "1.0.0",
        insecure: bool = False,
    ) -> None:
        """Initialize the TracingApp.

        Sets up the global TracerProvider either immediately (otlp_endpoint) or
        lazily on first request (exporter_provider with DI).

        Args:
            otlp_endpoint: OTLP endpoint URL (e.g., http://localhost:8360). Mutually exclusive with exporter_provider.
            exporter_provider: Function that creates a SpanExporter. Can use DI to request dependencies
                (secrets, client, logger, function_call_info, etc.). Called on first request. Mutually
                exclusive with otlp_endpoint.
            service_name: Service name for trace identification (default: "cognite-typed-functions")
            service_version: Service version (default: "1.0.0")
            insecure: Use insecure connection (default: False). Only applies when using otlp_endpoint.
                Only set to True for local development.

        Raises:
            ImportError: If OpenTelemetry is not installed
            ValueError: If both or neither of otlp_endpoint and exporter_provider are provided

        Example:
            Simple case (no DI needed):
                tracing = TracingApp(otlp_endpoint="http://localhost:8360", insecure=True)

            Advanced case (with DI for secrets):
                def create_lightstep_exporter(secrets: Mapping[str, str]) -> SpanExporter:
                    token = secrets.get("lightstep-token")
                    if not token:
                        raise ValueError("lightstep-token secret is required")
                    return OTLPSpanExporter(
                        endpoint="https://ingest.lightstep.com:443",
                        headers={"lightstep-access-token": token},
                    )

                tracing = TracingApp(
                    exporter_provider=create_lightstep_exporter,
                    service_name="my-function",
                )
        """
        if not _has_opentelemetry:
            raise ImportError(
                "Tracing support requires OpenTelemetry. Install it with: pip install cognite-typed-functions[tracing]"
            )

        # Validate that exactly one of otlp_endpoint or exporter_provider is provided
        if otlp_endpoint is None and exporter_provider is None:
            raise ValueError("Either otlp_endpoint or exporter_provider must be provided")
        if otlp_endpoint is not None and exporter_provider is not None:
            raise ValueError("otlp_endpoint and exporter_provider are mutually exclusive")

        super().__init__(title="Tracing", version="1.0.0")

        # Use provided service name/version, or fall back to defaults
        # Note: We set title="Tracing" above, so we use a sensible default
        self._service_name = service_name or "cognite-typed-functions"
        self._service_version = service_version or "1.0.0"
        self._insecure = insecure

        # Store exporter provider for lazy initialization
        self._exporter_provider = exporter_provider
        self._initialization_lock = threading.Lock()
        self._initialized = False

        # If otlp_endpoint provided, set up immediately
        if otlp_endpoint is not None:
            setup_global_tracer_provider(
                otlp_endpoint=otlp_endpoint,
                service_name=self._service_name,
                service_version=self._service_version,
                insecure=insecure,
            )
            self._initialized = True

        # Get tracer for use in __call__
        self._tracer = trace.get_tracer(__name__)

    def on_compose(
        self,
        next_app: FunctionApp | None,
        shared_registry: DependencyRegistry,
    ) -> None:
        """Set the context for the TracingApp.

        Registers the FunctionTracer dependency in the shared registry.
        """
        # Set registry first (call parent implementation)
        super().on_compose(next_app, shared_registry)

        # Register the tracer dependency in the shared registry
        # The tracer uses the global TracerProvider that was set up in __init__
        if self.registry is None:
            raise ValueError("Registry is not set")

        self.registry.register(
            provider=lambda ctx: FunctionTracer(trace.get_tracer(__name__)),
            target_type=FunctionTracer,
            param_name=self.tracer_param_name,
            description="OpenTelemetry function tracer with OTLP export",
        )

    def _set_span_status_from_response(
        self,
        root_span: Any,
        response_state: _ResponseState,
    ) -> None:
        """Set span status and attributes based on response state.

        Uses early returns to avoid nesting. Separates error detection
        logic from span annotation.

        Args:
            root_span: The OpenTelemetry span to annotate
            response_state: Response state dict with 'has_started' and 'body'
        """
        # No response sent - assume success
        if not response_state["has_started"]:
            root_span.set_attribute("http.status_code", 200)
            root_span.set_status(Status(StatusCode.OK))
            return

        response_body = response_state["body"]
        if not response_body:
            root_span.set_attribute("http.status_code", 200)
            root_span.set_status(Status(StatusCode.OK))
            return

        # Check if response indicates an error
        error_type = response_body.get("error_type")
        if not error_type:
            # Success response
            root_span.set_attribute("http.status_code", 200)
            root_span.set_status(Status(StatusCode.OK))
            return

        # Error response
        root_span.set_attribute("error", True)
        root_span.set_attribute("error.type", str(error_type))
        root_span.set_attribute("http.status_code", 500)
        error_message = response_body.get("message", "Error")
        root_span.set_status(Status(StatusCode.ERROR, str(error_message)))

    def _initialize_tracer_provider_if_needed(self, scope: ASGITypedFunctionScope) -> None:
        """Initialize tracer provider on first request if using exporter_provider.

        This method is called on the first request to lazily initialize the tracer
        provider when using an exporter_provider function. It resolves dependencies
        for the provider function using the DI framework and calls it to get the
        exporter.

        Thread-safe: Uses a lock to ensure initialization happens exactly once.

        Args:
            scope: ASGI scope containing request context for DI resolution
        """
        # Fast path: already initialized
        if self._initialized:
            return

        # Slow path: need to initialize
        with self._initialization_lock:
            # Double-check after acquiring lock
            if self._initialized:
                return

            if self._exporter_provider is None:
                # Should not happen, but be defensive
                self._initialized = True
                return

            # Ensure registry is available
            if self.registry is None:
                raise ValueError("Registry not initialized. App must be composed before use.")

            # Extract context for DI resolution
            client = scope["client"]
            secrets = scope.get("secrets")
            function_call_info = scope.get("function_call_info")

            # Resolve dependencies for exporter_provider
            from cognite_typed_functions.dependency_registry import resolve_dependencies

            dependencies = resolve_dependencies(
                self._exporter_provider,
                client,
                secrets,
                function_call_info,
                self.registry,
            )

            # Call exporter_provider to get the exporter
            exporter = self._exporter_provider(**dependencies)

            # Set up global tracer provider with the custom exporter
            setup_global_tracer_provider(
                service_name=self._service_name,
                service_version=self._service_version,
                exporter=exporter,
            )

            # Mark as initialized IMMEDIATELY after successful setup
            # This prevents retry attempts even if subsequent operations fail
            self._initialized = True

            # Update tracer reference (provider has changed)
            self._tracer = trace.get_tracer(__name__)

    def _force_flush_spans(self) -> None:
        """Force flush traces to ensure spans are exported before context is lost.

        This is especially important in serverless environments (e.g., Azure Functions)
        where the function instance may be recycled shortly after the response.
        Uses a short timeout to avoid blocking or impacting function lifecycle.

        The flush runs in a background daemon thread (fire-and-forget) to avoid
        blocking the handler return. This is best-effort - if the function instance
        is recycled before the flush completes, some spans may be lost.
        """

        def _flush() -> None:
            try:
                tracer_provider = trace.get_tracer_provider()
                if isinstance(tracer_provider, SdkTracerProvider):
                    # Flush with short timeout to avoid blocking response
                    # 500ms is a reasonable compromise: long enough for most spans to export,
                    # short enough to avoid Azure Functions lifecycle issues
                    tracer_provider.force_flush(timeout_millis=FLUSH_TIMEOUT_MS)
            except Exception as e:
                # Warn about flush failures but don't impact function execution
                warnings.warn(f"Failed to flush trace spans: {e}", stacklevel=3)

        # Fire and forget in daemon thread - doesn't block handler return
        thread = threading.Thread(target=_flush, daemon=True)
        thread.start()

    async def __call__(
        self,
        scope: ASGITypedFunctionScope,
        receive: ASGIReceiveCallable,
        send: ASGISendCallable,
    ) -> None:
        """ASGI interface with automatic root span creation.

        Creates a root span around the entire request lifecycle, including
        error handling. All downstream spans (from @trace() decorators or
        manual tracer.span() calls) will be children of this root span.

        If using exporter_provider, initializes the tracer provider on first request.

        Args:
            scope: ASGI scope containing request context
            receive: ASGI receive callable
            send: ASGI send callable
        """
        from opentelemetry.trace import SpanKind

        # Initialize tracer provider if using lazy initialization
        self._initialize_tracer_provider_if_needed(scope)

        # Extract request metadata from scope
        request = scope.get("request")
        function_call_info = scope.get("function_call_info")

        # Determine span name from request
        if request:
            # Start with a low-cardinality name; will be updated with the route template later.
            span_name = request.method
        else:
            span_name = "cognite.function.request"

        # Create root span with SERVER kind for HTTP request handlers
        with self._tracer.start_as_current_span(span_name, kind=SpanKind.SERVER) as root_span:
            # Set HTTP and request attributes
            root_span.set_attribute("operation.name", span_name)
            if request:
                root_span.set_attribute("http.method", request.method)
                root_span.set_attribute("http.url", request.path)
                # Note: http.route will be set after routing completes by reading
                # from scope["state"]["matched_route_path"] (set by FunctionApp during dispatch)

            # Set Cognite-specific metadata if available (skip None values)
            if function_call_info:
                if function_id := function_call_info.get("function_id"):
                    root_span.set_attribute("cognite.function_id", function_id)
                if call_id := function_call_info.get("call_id"):
                    root_span.set_attribute("cognite.call_id", call_id)
                if schedule_id := function_call_info.get("schedule_id"):
                    root_span.set_attribute("cognite.schedule_id", schedule_id)
                if scheduled_time := function_call_info.get("scheduled_time"):
                    root_span.set_attribute("cognite.scheduled_time", scheduled_time)

            # Track response state - fail on multiple sends
            response_state: _ResponseState = {
                "has_started": False,
                "body": None,
            }

            # Wrap send to capture response
            async def wrapped_send(message: ASGITypedFunctionResponseMessage) -> None:
                body = message["body"]
                # Enforce single response rule
                if response_state["has_started"]:
                    raise RuntimeError(
                        "Response has already been sent. "
                        "Multiple response sends are not allowed in the middleware chain."
                    )
                response_state["has_started"] = True
                response_state["body"] = body

                await send(message)

            try:
                # Call parent which handles dispatch_request and next_app delegation
                await super().__call__(scope, receive, wrapped_send)

                # Update http.route with matched route template from scope state (if available)
                # This is set by FunctionApp after successful routing
                state = scope.get("state", {})
                if (matched_route_path := state.get("matched_route_path")) is not None:
                    root_span.set_attribute("http.route", matched_route_path)
                    if request:
                        root_span.update_name(f"{request.method} {matched_route_path}")

                # Set span status based on response
                self._set_span_status_from_response(root_span, response_state)

            except Exception:
                # Catch any unhandled exceptions (shouldn't happen with cognite_error_handler, but be defensive)
                # Re-raise to allow the OpenTelemetry context manager to handle it.
                # It will set the status to ERROR and record the exception with a stack trace.
                root_span.set_attribute("error", True)
                root_span.set_attribute("http.status_code", 500)
                raise
            finally:
                # Force flush traces after sending response to ensure spans are exported
                # before context is lost (especially important in serverless environments).
                # Uses short timeout to avoid blocking or impacting function lifecycle.
                self._force_flush_spans()

    def trace(self, span_name: str | None = None) -> Callable[[Callable[_P, _R]], Callable[_P, _R]]:
        """Decorator to create a child span with handler metadata.

        Creates a child span under the root span created by TracingApp.__call__.
        The child span includes function and route metadata for granular tracing.

        Note:
            The root span is automatically created at the middleware level by TracingApp.
            This decorator is optional and provides additional granularity for specific
            handlers that need detailed tracing.

        Args:
            span_name: Optional custom span name. If not provided, uses function name

        Returns:
            Decorator that wraps the function with a child span

        Example:
            @app.get("/items/{id}")
            @tracing.trace()  # Creates child span named "get_item"
            def get_item(tracer: FunctionTracer, id: int):
                with tracer.span("database_query"):  # Creates grandchild span
                    return {"id": id}

            @app.post("/items")
            @tracing.trace("create_item_operation")  # Custom span name
            def create_item(tracer: FunctionTracer, name: str):
                pass
        """

        def decorator(func: Callable[_P, _R]) -> Callable[_P, _R]:
            # Get route info from function metadata if set by @app.get/post decorators
            route_path = getattr(func, "_route_path", None)
            route_method = getattr(func, "_route_method", None)

            # Determine span name
            if span_name:
                effective_span_name = span_name
            else:
                effective_span_name = func.__name__

            # Check if function declares the tracer parameter
            # Uses strict name AND type matching to align with DI semantics
            sig = inspect.signature(func)
            param = sig.parameters.get(self.tracer_param_name)

            # Early exit if tracer parameter not declared with correct type
            if not param or param.annotation != FunctionTracer:
                return func

            def _update_root_span_with_route() -> None:
                """Update root span with route template for proper http.route semantics.

                Must be called before creating child span so get_current_span()
                returns the root span, not the child span.
                """
                if route_path and _has_opentelemetry:
                    root_span = trace.get_current_span()
                    if root_span and root_span.is_recording():
                        root_span.set_attribute("http.route", route_path)

            def _setup_span_attributes(child_span: Any) -> None:
                """Set up child span attributes with function-level metadata."""
                # Add operation name to child span
                child_span.set_attribute("operation.name", effective_span_name)

                # Add function metadata to child span
                child_span.set_attribute("function.name", func.__name__)

                # Add HTTP metadata to child span if available
                if route_path:
                    child_span.set_attribute("http.route", route_path)
                if route_method:
                    child_span.set_attribute("http.method", route_method)

            @wraps(func)
            def sync_wrapper(*args: _P.args, **kwargs: _P.kwargs) -> _R:
                # Get tracer using configured parameter name
                tracer: FunctionTracer | None = cast(FunctionTracer | None, kwargs.get(self.tracer_param_name))

                if not tracer or not _has_opentelemetry:
                    # No tracer available or OpenTelemetry not installed, execute normally
                    return func(*args, **kwargs)

                # Update root span with route template before creating child span
                _update_root_span_with_route()

                # Create child span (inherits from root span created in __call__)
                with tracer.tracer.start_as_current_span(effective_span_name) as child_span:
                    _setup_span_attributes(child_span)
                    try:
                        result = func(*args, **kwargs)
                        child_span.set_status(Status(StatusCode.OK))
                        return result
                    except Exception:
                        # Re-raise to allow the OpenTelemetry context manager to handle it.
                        # It will set the status to ERROR and record the exception with a stack trace.
                        child_span.set_attribute("error", True)
                        raise

            @wraps(func)
            async def async_wrapper(*args: _P.args, **kwargs: _P.kwargs) -> _R:
                # Get tracer using configured parameter name
                tracer: FunctionTracer | None = cast(FunctionTracer | None, kwargs.get(self.tracer_param_name))
                _func = cast(Callable[..., Coroutine[Any, Any, _R]], func)

                if not tracer or not _has_opentelemetry:
                    # No tracer available or OpenTelemetry not installed, execute normally
                    return await _func(*args, **kwargs)

                # Update root span with route template before creating child span
                _update_root_span_with_route()

                # Create child span (inherits from root span created in __call__)
                with tracer.tracer.start_as_current_span(effective_span_name) as child_span:
                    _setup_span_attributes(child_span)
                    try:
                        result = await _func(*args, **kwargs)
                        child_span.set_status(Status(StatusCode.OK))
                        return result
                    except Exception:
                        # Re-raise to allow the OpenTelemetry context manager to handle it.
                        # It will set the status to ERROR and record the exception with a stack trace.
                        child_span.set_attribute("error", True)
                        raise

            # Return appropriate wrapper based on function type
            if inspect.iscoroutinefunction(func):
                return async_wrapper  # type: ignore[return-value]
            else:
                return sync_wrapper  # type: ignore[return-value]

        return decorator


@overload
def create_tracing_app(
    *,
    otlp_endpoint: str,
    exporter_provider: None = None,
    service_name: str = "cognite-typed-functions",
    service_version: str = "1.0.0",
    insecure: bool = False,
) -> TracingApp: ...


@overload
def create_tracing_app(
    *,
    otlp_endpoint: None = None,
    exporter_provider: Callable[..., "SpanExporter"],
    service_name: str = "cognite-typed-functions",
    service_version: str = "1.0.0",
    insecure: bool = False,
) -> TracingApp: ...


def create_tracing_app(
    *,
    otlp_endpoint: str | None = None,
    exporter_provider: Callable[..., "SpanExporter"] | None = None,
    service_name: str = "cognite-typed-functions",
    service_version: str = "1.0.0",
    insecure: bool = False,
) -> TracingApp:
    """Create a TracingApp for decorator-based automatic root spans.

    Supports two modes:
    1. Simple mode: Pass otlp_endpoint for immediate setup (no DI needed)
    2. Advanced mode: Pass exporter_provider for lazy setup with DI (called on first request)

    Args:
        otlp_endpoint: OTLP endpoint URL (e.g., http://localhost:8360). Mutually exclusive with exporter_provider.
        exporter_provider: Function that creates a SpanExporter. Can use DI to request any dependency
            (secrets, client, logger, function_call_info, or custom deps). Called on first request.
            Mutually exclusive with otlp_endpoint.
        service_name: Service name for trace identification (default: "cognite-typed-functions")
        service_version: Service version (default: "1.0.0")
        insecure: Use insecure connection (default: False). Only applies when using otlp_endpoint.
            Only set to True for local development.

    Returns:
        TracingApp instance

    Raises:
        ValueError: If both or neither of otlp_endpoint and exporter_provider are provided

    Examples:
        Simple case (local development):
            tracing = create_tracing_app(
                otlp_endpoint="http://localhost:8360",
                service_name="my-function",
                insecure=True
            )

        Advanced case (production with secrets):
            from collections.abc import Mapping
            from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
            from opentelemetry.sdk.trace.export import SpanExporter

            def create_lightstep_exporter(secrets: Mapping[str, str]) -> SpanExporter:
                token = secrets.get("lightstep-token")
                if not token:
                    raise ValueError("lightstep-token secret is required")
                return OTLPSpanExporter(
                    endpoint="https://ingest.lightstep.com:443",
                    headers={"lightstep-access-token": token},
                )

            tracing = create_tracing_app(
                exporter_provider=create_lightstep_exporter,
                service_name="my-function",
                service_version="1.0.0",
            )

        Using the tracing app:
            @app.get("/items/{id}")
            @tracing.trace()
            def get_item(tracer: FunctionTracer, id: int):
                with tracer.span("database_query"):
                    return {"id": id}

            handle = create_function_service(tracing, app)
    """
    # Type narrowing: exactly one of otlp_endpoint or exporter_provider must be provided
    # This matches the overload signatures and allows proper type checking
    if otlp_endpoint is not None:
        return TracingApp(
            otlp_endpoint=otlp_endpoint,
            exporter_provider=None,
            service_name=service_name,
            service_version=service_version,
            insecure=insecure,
        )
    else:
        # exporter_provider is guaranteed to be non-None here due to validation in __init__
        assert exporter_provider is not None
        return TracingApp(
            otlp_endpoint=None,
            exporter_provider=exporter_provider,
            service_name=service_name,
            service_version=service_version,
            insecure=insecure,
        )
