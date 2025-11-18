"""
Simple Zephyr Application Example

This example demonstrates the new developer-friendly features:
- Simple app.run() without manual asyncio handling
- Lifecycle hooks with @app.register_hook()
- Exception handlers
- Router composition with include_router()
"""

from zephyr import Zephyr
from zephyr.app.routing import Router
from zephyr.app.responses import JSONResponse
from zephyr.app.requests import Request

# Create the main application
app = Zephyr(title="Simple Zephyr App", version="1.0.0", description="A simple example application")

# ========== Lifecycle Hooks ==========


@app.register_hook("after_startup")
async def startup():
    """Called when the application starts."""
    app.logger.info("Application starting up...")
    app.logger.info("   - Initializing database connections")
    app.logger.info("   - Loading configuration")
    app.logger.info("   - Ready to serve requests!")


@app.register_hook("before_shutdown")
async def shutdown():
    """Called when the application shuts down."""
    app.logger.info("Application shutting down...")
    app.logger.info("   - Closing database connections")
    app.logger.info("   - Cleaning up resources")
    app.logger.info("   - Goodbye!")


# ========== Exception Handlers ==========


@app.exception_handler(ValueError)
async def handle_value_error(request: Request, exc: ValueError):
    """Handle ValueError exceptions."""
    return JSONResponse({"error": "Invalid value", "detail": str(exc)}, status_code=400)


@app.exception_handler(404)
async def custom_404_handler(request: Request, exc):
    """Custom 404 handler."""
    return JSONResponse({"error": "Not found", "path": request.url.path}, status_code=404)


# ========== Main Routes ==========


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to Zephyr!",
        "version": "1.0.0",
        "endpoints": {"health": "/health", "users": "/api/users", "docs": "/openapi.json"},
    }


@app.get("/hello/{name}")
async def hello(name: str):
    """Greet a user by name."""
    return {"message": f"Hello, {name}!"}


@app.post("/echo")
async def echo(request: Request):
    """Echo back the request body."""
    body = await request.json()
    return {"echo": body}


# ========== Sub-Router Example ==========

# Create a sub-router for user-related endpoints
users_router = Router()


@users_router.get("/users")
async def list_users():
    """List all users."""
    return {"users": [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}, {"id": 3, "name": "Charlie"}]}


@users_router.get("/users/{user_id}")
async def get_user(user_id: int):
    """Get a specific user."""
    return {"id": user_id, "name": f"User {user_id}"}


@users_router.post("/users")
async def create_user(request: Request):
    """Create a new user."""
    body = await request.json()
    return {"id": 999, "name": body.get("name", "Unknown")}


# Include the users router with a prefix
app.include_router(users_router, prefix="/api")

# ========== Test Error Endpoint ==========


@app.get("/error")
async def trigger_error():
    """Endpoint that triggers an error (for testing exception handlers)."""
    raise ValueError("This is a test error!")


# ========== Run the Application ==========

if __name__ == "__main__":
    # That's it! No asyncio.run(), no complex setup
    # Just call app.run() and you're done!
    app.logger.info("=" * 60)
    app.logger.info("Starting Simple Zephyr Application")
    app.logger.info("=" * 60)

    app.run(host="0.0.0.0", port=8000)
