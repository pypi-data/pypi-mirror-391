# Zephyr Hooks System Guide

The Hooks system in Zephyr provides a clean, sophisticated way to handle application lifecycle events with proper logging and error handling.

## Overview

Zephyr supports two lifecycle hooks:
- **`after_startup`** - Runs after the application starts up
- **`before_shutdown`** - Runs before the application shuts down

## Basic Usage

### Registering Hooks with Decorators

```python
from zephyr import Zephyr

app = Zephyr(title="MyApp")

@app.register_hook("after_startup")
async def startup():
    app.logger.info("Application starting up...")
    # Initialize database
    # Load configuration
    # Warm up caches

@app.register_hook("before_shutdown")
async def shutdown():
    app.logger.info("Application shutting down...")
    # Close database connections
    # Save state
    # Clean up resources
```

### Programmatic Registration

```python
async def init_db():
    app.logger.info("Initializing database...")

async def close_db():
    app.logger.info("Closing database...")

app.register_hook("after_startup")(init_db)
app.register_hook("before_shutdown")(close_db)
```

### Running Hooks Manually

```python
# Run a specific hook
await app.run_hook("after_startup")

# Or use convenience methods
await app.run_after_startup_hook()
await app.run_before_shutdown_hook()
```

## Sync and Async Hooks

Zephyr automatically handles both sync and async functions:

```python
@app.register_hook("after_startup")
def sync_startup():
    # This runs in a threadpool
    app.logger.info("Sync startup")
    db = connect_to_database()  # Blocking operation

@app.register_hook("after_startup")
async def async_startup():
    # This runs directly in the event loop
    app.logger.info("Async startup")
    await async_db.connect()
```

## Error Handling

Errors in hooks are caught, logged, and re-raised:

```python
@app.register_hook("after_startup")
async def startup():
    app.logger.info("Starting up...")
    try:
        await initialize_resources()
    except Exception as exc:
        app.logger.error("Failed to initialize: %s", exc)
        raise

# Output on error:
# ERROR: Error in hook MyApp@after_startup: Failed to initialize: Connection refused
```

## Logger Access

The logger is attached to the app and accessible within hooks:

```python
@app.register_hook("after_startup")
async def startup():
    app.logger.debug("Starting debug initialization")
    app.logger.info("Starting initialization")
    await some_operation()
    app.logger.debug("Initialization complete")

@app.get("/")
async def root():
    app.logger.debug("Root endpoint called")
    return {"message": "Hello"}
```

## Common Patterns

### Database Initialization

```python
class DatabasePool:
    _instance = None
    
    @classmethod
    async def get_pool(cls):
        if cls._instance is None:
            cls._instance = await create_pool()
        return cls._instance

@app.register_hook("after_startup")
async def init_db():
    pool = await DatabasePool.get_pool()
    app.logger.info("Database pool initialized")

@app.register_hook("before_shutdown")
async def close_db():
    pool = await DatabasePool.get_pool()
    await pool.close()
    app.logger.info("Database pool closed")

@app.get("/users")
async def list_users():
    pool = await DatabasePool.get_pool()
    users = await pool.fetch("SELECT * FROM users")
    return {"users": users}
```

### Cache Warming

```python
@app.register_hook("after_startup")
async def warm_cache():
    app.logger.info("Warming up caches...")
    app.state.config = await load_configuration()
    app.state.templates = await compile_templates()
    app.logger.info("Cache warming complete")

@app.get("/config")
async def get_config():
    return app.state.config
```

### Resource Management

```python
import aiohttp

@app.register_hook("after_startup")
async def create_session():
    app.state.http_session = aiohttp.ClientSession()
    app.logger.info("HTTP session created")

@app.register_hook("before_shutdown")
async def close_session():
    await app.state.http_session.close()
    app.logger.info("HTTP session closed")

@app.get("/fetch")
async def fetch_data(url: str):
    async with app.state.http_session.get(url) as resp:
        return await resp.json()
```

## Hook Ordering

Currently, hooks execute in the order they are registered:

```python
@app.register_hook("after_startup")
async def first():
    app.logger.info("First")  # Runs first

@app.register_hook("after_startup")
async def second():
    app.logger.info("Second")  # Runs second

# Output:
# INFO: First
# INFO: Second
```

**Note:** Only one hook per name can be registered at a time. Registering a new hook with the same name overwrites the previous one:

```python
@app.register_hook("after_startup")
async def startup_v1():
    app.logger.info("Version 1")

@app.register_hook("after_startup")
async def startup_v2():
    app.logger.info("Version 2")  # This overwrites startup_v1

# Output on startup:
# INFO: Version 2
```

## Backward Compatibility

The old event-based API still works and maps to hooks:

```python
# Old way (still works)
@app.on_event("startup")
async def old_startup():
    app.logger.info("Old way")

# New way (recommended)
@app.register_hook("after_startup")
async def new_startup():
    app.logger.info("New way")

# Both will execute
```

Mapping:
- `@app.on_event("startup")` → `@app.register_hook("after_startup")`
- `@app.on_event("shutdown")` → `@app.register_hook("before_shutdown")`

## Debugging

### Hook Registration

All hook registrations are logged at debug level:

```python
@app.register_hook("after_startup")
async def my_hook():
    pass

# Output:
# DEBUG: Hook registered: after_startup -> my_hook
# DEBUG: Zephyr app initialized: MyApp v1.0.0
```

### Hook Execution

Hook execution is logged at debug level:

```python
# During startup:
# DEBUG: Running hook: after_startup
# ... your hook code runs ...
# DEBUG: Hook completed: after_startup
```

### Hook Errors

Errors are logged at error level with full traceback:

```python
# If hook raises exception:
# ERROR: Error in hook MyApp@after_startup: Some error message
# <full traceback>
```

Enable debug logging to see all hook activity:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

app = Zephyr(title="MyApp", debug=True)
```

## Accessing Hooks

### Check Registered Hooks

```python
# Get all registered hooks
hooks = app._hooks
# {'after_startup': <function my_startup>, 'before_shutdown': <function my_shutdown>}

# Check if a hook is registered
if "after_startup" in app._hooks:
    func = app._hooks["after_startup"]
    print(f"Hook: {func.__name__}")
```

### Get Hook Class Definition

```python
# See supported hooks
print(Zephyr.HOOKS)
# ['after_startup', 'before_shutdown']
```

## Advanced Patterns

### Conditional Hook Execution

```python
@app.register_hook("after_startup")
async def startup():
    if app.debug:
        app.logger.info("Debug mode - skipping prod initialization")
        return
    
    app.logger.info("Production mode - initializing...")
    await initialize_production_resources()
```

### Hook with Configuration

```python
@app.register_hook("after_startup")
async def startup():
    config = await load_config(app.title)
    app.state.config = config
    app.logger.info(f"Loaded config: {config}")
```

### Testing with Hooks

```python
@pytest.fixture
async def app_with_db():
    app = Zephyr(title="TestApp")
    
    @app.register_hook("after_startup")
    async def startup():
        app.state.db = MockDatabase()
    
    @app.register_hook("before_shutdown")
    async def shutdown():
        app.state.db.close()
    
    await app.run_after_startup_hook()
    yield app
    await app.run_before_shutdown_hook()
```

## Performance Considerations

1. **Hooks run during startup/shutdown** - Not in request path
2. **Keep hooks fast** - Long-running operations impact startup time
3. **Use threadpool for sync** - Sync functions automatically run in threadpool
4. **Log appropriately** - Use debug logs for verbose output

## Complete Example

```python
import asyncio
from zephyr import Zephyr

app = Zephyr(
    title="Complete Example",
    version="1.0.0",
    description="Demonstrates all hook features"
)

# Simulate a database
class Database:
    def __init__(self):
        self.connected = False
    
    async def connect(self):
        self.connected = True
        await asyncio.sleep(0.1)
    
    async def close(self):
        self.connected = False

@app.register_hook("after_startup")
async def startup():
    app.logger.info("=== STARTUP ===")
    
    # Initialize database
    app.state.db = Database()
    await app.state.db.connect()
    app.logger.info("Database connected")
    
    # Load config
    app.state.config = {"debug": True}
    app.logger.info("Configuration loaded")
    
    app.logger.info("=== STARTUP COMPLETE ===")

@app.register_hook("before_shutdown")
async def shutdown():
    app.logger.info("=== SHUTDOWN ===")
    
    # Close database
    await app.state.db.close()
    app.logger.info("Database closed")
    
    app.logger.info("=== SHUTDOWN COMPLETE ===")

@app.get("/status")
async def status():
    return {
        "db_connected": app.state.db.connected,
        "config": app.state.config
    }

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
```

## Troubleshooting

### Hook Not Running

**Problem:** Hook is registered but not executing

**Solution:** Check hook name is correct:
```python
# Check supported hooks
print(Zephyr.HOOKS)  # ['after_startup', 'before_shutdown']

# Use correct name
@app.register_hook("after_startup")  # ✓ Correct
```

### Error in Hook

**Problem:** Application exits after hook error

**Solution:** Add error handling in hook:
```python
@app.register_hook("after_startup")
async def startup():
    try:
        await initialize()
    except Exception as exc:
        app.logger.error("Initialization failed: %s", exc)
        # Either handle gracefully or re-raise
        raise
```

### Logger Not Working

**Problem:** Can't access app.logger in hook

**Solution:** Logger is always available on app instance:
```python
@app.register_hook("after_startup")
async def startup():
    app.logger.info("This always works")
```

## See Also

- [Developer Experience Guide](./developer-experience.md)
- [Quick Start](./QUICK_START.md)
- [API Reference](./api-reference.md)

