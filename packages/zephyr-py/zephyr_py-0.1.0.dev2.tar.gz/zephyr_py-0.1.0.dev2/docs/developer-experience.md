# Zephyr Developer Experience Guide

This guide covers the developer-friendly features added to Zephyr to make building applications easier and more intuitive.

## Table of Contents

1. [Simple Server Startup](#simple-server-startup)
2. [Lifecycle Hooks](#lifecycle-hooks)
3. [Exception Handlers](#exception-handlers)
4. [Router Composition](#router-composition)
5. [Dependency Overrides](#dependency-overrides)
6. [Complete Example](#complete-example)

## Simple Server Startup

No more manual `asyncio.run()` calls! Just use `app.run()`:

```python
from zephyr import Zephyr

app = Zephyr()

@app.get("/")
async def root():
    return {"message": "Hello World"}

# That's it! No asyncio needed
app.run(host="0.0.0.0", port=8000)
```

### Methods

#### `app.run(host, port, **kwargs)`

Synchronous entry point that blocks until the server shuts down. Perfect for production and development.

```python
app.run(
    host="0.0.0.0",
    port=8000,
    reload=True,  # Enable auto-reload in development
    workers=4,    # Number of worker processes
)
```

#### `await app.serve(host, port, **kwargs)`

Async entry point for embedding in existing event loops (useful for tests or orchestration):

```python
import asyncio

async def main():
    # Run alongside other async tasks
    await app.serve(host="0.0.0.0", port=8000)

asyncio.run(main())
```

#### `app.server` property

Access the underlying server instance for advanced control:

```python
server = app.server
# server.config, server.should_exit, etc.
```

## Lifecycle Hooks

Register functions to run on application startup and shutdown.

### Using Decorators

```python
@app.on_event("startup")
async def startup():
    print("Application starting...")
    # Initialize database connections
    # Load configuration
    # Warm up caches

@app.on_event("shutdown")
async def shutdown():
    print("Application shutting down...")
    # Close database connections
    # Save state
    # Clean up resources
```

### Using Methods

```python
async def init_db():
    print("Connecting to database...")

async def close_db():
    print("Closing database connection...")

app.add_event_handler("startup", init_db)
app.add_event_handler("shutdown", close_db)
```

### Sync Handlers

Both sync and async handlers are supported:

```python
@app.on_event("startup")
def sync_startup():
    # Synchronous initialization
    print("Sync startup complete")

@app.on_event("startup")
async def async_startup():
    # Asynchronous initialization
    await some_async_operation()
```

## Exception Handlers

Handle exceptions globally with custom error responses.

### Using Decorators

```python
from zephyr.app.responses import JSONResponse

@app.exception_handler(ValueError)
async def handle_value_error(request, exc):
    return JSONResponse(
        {"error": "Invalid value", "detail": str(exc)},
        status_code=400
    )

@app.exception_handler(404)
async def custom_404(request, exc):
    return JSONResponse(
        {"error": "Not found", "path": request.url.path},
        status_code=404
    )
```

### Using Methods

```python
async def handle_db_error(request, exc):
    return JSONResponse(
        {"error": "Database error"},
        status_code=500
    )

app.add_exception_handler(DatabaseError, handle_db_error)
```

### Status Code Handlers

Handle specific HTTP status codes:

```python
@app.exception_handler(500)
async def internal_error(request, exc):
    # Log the error
    logger.error(f"Internal error: {exc}")
    return JSONResponse(
        {"error": "Internal server error"},
        status_code=500
    )
```

## Router Composition

Organize your application with sub-routers and mounted apps.

### Include Router

Break your application into modules with separate routers:

```python
from zephyr import Zephyr
from zephyr.app.routing import Router

app = Zephyr()

# Create a router for user endpoints
users_router = Router()

@users_router.get("/users")
async def list_users():
    return {"users": [...]}

@users_router.get("/users/{user_id}")
async def get_user(user_id: int):
    return {"id": user_id}

# Include the router with a prefix
app.include_router(users_router, prefix="/api/v1")
# Routes available at: /api/v1/users, /api/v1/users/{user_id}
```

### Mount ASGI Apps

Mount other ASGI applications at specific paths:

```python
from some_static_files import StaticFiles

# Mount a static files server
app.mount("/static", StaticFiles(directory="static"))

# Mount another ASGI app
app.mount("/admin", admin_app)
```

### Add Routes Directly

Add routes programmatically:

```python
async def health_check():
    return {"status": "healthy"}

app.add_api_route(
    "/health",
    health_check,
    methods=["GET"],
    status_code=200
)
```

## Dependency Overrides

Override dependencies for testing or different environments.

```python
from zephyr import Zephyr

app = Zephyr()

# Original dependency
async def get_db():
    return RealDatabase()

# Override for testing
async def get_test_db():
    return MockDatabase()

# Apply override
app.dependency_overrides[get_db] = get_test_db
```

This is particularly useful in test suites:

```python
def test_endpoint():
    app.dependency_overrides[get_db] = get_test_db
    # Run tests
    app.dependency_overrides.clear()
```

## Complete Example

Here's a complete application showcasing all features:

```python
from zephyr import Zephyr
from zephyr.app.routing import Router
from zephyr.app.responses import JSONResponse

# Create app
app = Zephyr(title="My API", version="1.0.0")

# Lifecycle hooks
@app.on_event("startup")
async def startup():
    print("Starting up...")

@app.on_event("shutdown")
async def shutdown():
    print("Shutting down...")

# Exception handlers
@app.exception_handler(ValueError)
async def handle_value_error(request, exc):
    return JSONResponse({"error": str(exc)}, status_code=400)

# Main routes
@app.get("/")
async def root():
    return {"message": "Hello World"}

# Sub-router
api_router = Router()

@api_router.get("/users")
async def list_users():
    return {"users": []}

app.include_router(api_router, prefix="/api")

# Run the app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
```

## Migration Guide

### From Manual asyncio.run()

**Before:**
```python
import asyncio

app = create_app()

async def main():
    await app.run(host="0.0.0.0", port=8000)

asyncio.run(main())
```

**After:**
```python
app = create_app()
app.run(host="0.0.0.0", port=8000)
```

### From Custom Lifespan

**Before:**
```python
@asynccontextmanager
async def lifespan(app):
    # startup
    print("Starting...")
    yield
    # shutdown
    print("Stopping...")

app = Zephyr(lifespan=lifespan)
```

**After:**
```python
app = Zephyr()

@app.on_event("startup")
async def startup():
    print("Starting...")

@app.on_event("shutdown")
async def shutdown():
    print("Stopping...")
```

Both approaches still work! The new event handlers provide a simpler API for common cases.

## Best Practices

1. **Use `app.run()` for production and development** - It handles all the asyncio complexity for you.

2. **Use `app.serve()` for tests** - When you need to control the event loop yourself.

3. **Organize with routers** - Split large applications into multiple routers by feature or domain.

4. **Handle exceptions globally** - Use exception handlers instead of try/catch in every endpoint.

5. **Clean up in shutdown handlers** - Always close connections and clean up resources properly.

6. **Override dependencies for testing** - Use `app.dependency_overrides` to inject mocks and test doubles.

## Next Steps

- Check out the [examples directory](../examples/) for more complete applications
- Read the [API Reference](./api-reference.md) for detailed documentation
- Join our [community](https://github.com/bbdevs/zephyr) for support and discussions

