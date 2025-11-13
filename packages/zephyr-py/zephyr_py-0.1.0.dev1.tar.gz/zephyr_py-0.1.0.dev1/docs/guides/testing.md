# Testing Guide

This guide covers testing in Zephyr applications using the built-in testing framework.

## Quick Start

```python
from zephyr.testing import TestClient, async_test
from your_app import app

@async_test
async def test_hello_endpoint():
    client = TestClient(app)
    response = await client.get("/hello")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello, World!"}

@async_test
async def test_create_user():
    client = TestClient(app)
    response = await client.post(
        "/users",
        json={
            "username": "testuser",
            "email": "test@example.com"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
```

## Test Client

The `TestClient` class provides methods for making HTTP requests to your application:

```python
from zephyr.testing import TestClient

client = TestClient(app)

# GET request
response = await client.get("/api/users")

# POST request with JSON data
response = await client.post(
    "/api/users",
    json={"name": "John"}
)

# PUT request with form data
response = await client.put(
    "/api/users/1",
    data={"name": "John"}
)

# DELETE request
response = await client.delete("/api/users/1")

# Request with query parameters
response = await client.get(
    "/api/users",
    params={"role": "admin"}
)

# Request with headers
response = await client.get(
    "/api/users",
    headers={"Authorization": "Bearer token"}
)
```

## WebSocket Testing

Test WebSocket connections and messages:

```python
@async_test
async def test_websocket():
    client = TestClient(app)
    async with client.ws_connect("/ws") as ws:
        await ws.send_json({"type": "subscribe"})
        data = await ws.receive_json()
        assert data["status"] == "subscribed"
```

## Mocking

Use the built-in mocking utilities:

```python
from zephyr.testing import MockRequest, MockResponse

async def test_with_mock():
    # Mock a request
    request = MockRequest(
        method="GET",
        url="/api/users",
        headers={"Authorization": "Bearer token"}
    )
    
    # Mock a response
    response = MockResponse(
        status_code=200,
        content={"data": "test"}
    )
```

## Database Testing

Test database operations:

```python
from zephyr.testing import create_test_db

@async_test
async def test_database():
    async with create_test_db() as db:
        # Create test data
        user = await db.create_user(name="Test User")
        
        # Perform test
        response = await client.get(f"/users/{user.id}")
        assert response.status_code == 200
```

## Fixtures

Use test fixtures for common setup:

```python
from zephyr.testing import fixtures

@fixtures.use_db
async def test_with_database(db):
    # Database is automatically set up and torn down
    user = await db.users.create(name="Test")
    assert user.id is not None

@fixtures.use_auth
async def test_with_auth(auth):
    # Authentication is automatically set up
    token = await auth.create_token(user_id=1)
    assert token is not None
```

## Async Testing

Use the `async_test` decorator for async tests:

```python
from zephyr.testing import async_test

@async_test
async def test_async_operation():
    result = await perform_async_operation()
    assert result is not None
```

## Test Configuration

Configure test settings:

```python
from zephyr.testing import configure_tests

configure_tests(
    database_url="postgresql://test:test@localhost/test",
    redis_url="redis://localhost",
    email_backend="dummy"
)
