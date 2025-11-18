# Zephyr Quick Start Guide

Get started with Zephyr in 5 minutes!

## Installation

```bash
pip install zephyr-framework
```

## Hello World

```python
from zephyr import Zephyr

app = Zephyr()

@app.get("/")
async def root():
    return {"message": "Hello World"}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
```

Run it:
```bash
python app.py
```

Visit: http://localhost:8000

## Common Patterns

### Path Parameters

```python
@app.get("/users/{user_id}")
async def get_user(user_id: int):
    return {"user_id": user_id}
```

### Request Body

```python
from zephyr.app.requests import Request

@app.post("/users")
async def create_user(request: Request):
    body = await request.json()
    return {"created": body}
```

### Startup/Shutdown

```python
@app.on_event("startup")
async def startup():
    print("App starting...")

@app.on_event("shutdown")
async def shutdown():
    print("App stopping...")
```

### Error Handling

```python
from zephyr.app.responses import JSONResponse

@app.exception_handler(ValueError)
async def handle_error(request, exc):
    return JSONResponse(
        {"error": str(exc)},
        status_code=400
    )
```

### Organize with Routers

```python
from zephyr.app.routing import Router

# Create sub-router
api = Router()

@api.get("/items")
async def list_items():
    return {"items": []}

# Include in main app
app.include_router(api, prefix="/api/v1")
# Available at: /api/v1/items
```

## HTTP Methods

```python
@app.get("/items")
async def read_items():
    return []

@app.post("/items")
async def create_item(request: Request):
    return {}

@app.put("/items/{item_id}")
async def update_item(item_id: int):
    return {}

@app.delete("/items/{item_id}")
async def delete_item(item_id: int):
    return {}
```

## Response Types

```python
from zephyr.app.responses import JSONResponse, PlainTextResponse

@app.get("/json")
async def json_response():
    return {"key": "value"}  # Auto JSON

@app.get("/text")
async def text_response():
    return PlainTextResponse("Hello")

@app.get("/custom")
async def custom_response():
    return JSONResponse(
        {"message": "Created"},
        status_code=201,
        headers={"X-Custom": "Header"}
    )
```

## Built-in Endpoints

Zephyr automatically provides:

- `/health` - Health check
- `/health/ready` - Readiness probe
- `/health/live` - Liveness probe
- `/openapi.json` - OpenAPI schema

## Configuration

```python
app = Zephyr(
    title="My API",
    version="1.0.0",
    description="API description",
    debug=True  # Enable debug mode
)
```

## Running Options

```python
# Development
app.run(host="127.0.0.1", port=8000)

# Production
app.run(
    host="0.0.0.0",
    port=8000,
    workers=4  # Multiple workers
)

# With auto-reload
app.run(
    host="0.0.0.0",
    port=8000,
    reload=True  # Auto-reload on code changes
)
```

## Next Steps

- Read the [Developer Experience Guide](./developer-experience.md) for advanced features
- Check out [examples/simple_app.py](../examples/simple_app.py) for a complete example
- Explore the [API Reference](./api-reference.md) for detailed documentation

## Need Help?

- GitHub: https://github.com/bbdevs/zephyr
- Documentation: https://zephyr.bbdevs.com
- Issues: https://github.com/bbdevs/zephyr/issues

