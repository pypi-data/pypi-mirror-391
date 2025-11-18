# Middleware Guide

This guide covers the middleware system in Zephyr applications.

## Overview

Middleware in Zephyr allows you to process requests and responses, modify them, and perform actions before or after request handling.

## Basic Middleware

Create a simple middleware:

```python
from zephyr.middleware import Middleware
from zephyr.types import Request, Response

class LoggingMiddleware(Middleware):
    async def process_request(self, request: Request) -> Request:
        print(f"Processing request: {request.method} {request.url}")
        return request
        
    async def process_response(self, response: Response) -> Response:
        print(f"Processing response: {response.status_code}")
        return response
```

## Using Middleware

Add middleware to your application:

```python
from zephyr.core.app import ZephyrApp
from .middleware import LoggingMiddleware

app = ZephyrApp()
app.add_middleware(LoggingMiddleware)
```

## Authentication Middleware

Implement authentication:

```python
class AuthMiddleware(Middleware):
    async def process_request(self, request: Request) -> Request:
        auth_header = request.headers.get("Authorization")
        if auth_header:
            token = auth_header.split(" ")[1]
            user = await verify_token(token)
            request.user = user
        return request
```

## CORS Middleware

Handle CORS requests:

```python
class CORSMiddleware(Middleware):
    def __init__(
        self,
        allow_origins: List[str] = ["*"],
        allow_methods: List[str] = ["GET", "POST", "PUT", "DELETE"],
        allow_headers: List[str] = ["*"],
        allow_credentials: bool = True
    ):
        self.allow_origins = allow_origins
        self.allow_methods = allow_methods
        self.allow_headers = allow_headers
        self.allow_credentials = allow_credentials
        
    async def process_response(self, response: Response) -> Response:
        response.headers["Access-Control-Allow-Origin"] = ",".join(self.allow_origins)
        response.headers["Access-Control-Allow-Methods"] = ",".join(self.allow_methods)
        response.headers["Access-Control-Allow-Headers"] = ",".join(self.allow_headers)
        response.headers["Access-Control-Allow-Credentials"] = str(self.allow_credentials).lower()
        return response
```

## Rate Limiting Middleware

Implement rate limiting:

```python
class RateLimitMiddleware(Middleware):
    def __init__(self, requests: int, period: int):
        self.requests = requests
        self.period = period
        self._cache = {}
        
    async def process_request(self, request: Request) -> Request:
        client_ip = request.client.host
        now = time.time()
        
        # Clean old entries
        self._clean_old_entries(now)
        
        # Check rate limit
        if client_ip in self._cache:
            requests = self._cache[client_ip]
            if len(requests) >= self.requests:
                raise TooManyRequests()
                
        # Add request
        if client_ip not in self._cache:
            self._cache[client_ip] = []
        self._cache[client_ip].append(now)
        
        return request
        
    def _clean_old_entries(self, now: float):
        for ip, requests in self._cache.items():
            self._cache[ip] = [
                req_time for req_time in requests
                if now - req_time <= self.period
            ]
```

## Error Handling Middleware

Handle exceptions:

```python
class ErrorHandlerMiddleware(Middleware):
    async def process_exception(self, request: Request, exc: Exception) -> Response:
        if isinstance(exc, NotFound):
            return JSONResponse(
                {"error": "Not found"},
                status_code=404
            )
        elif isinstance(exc, ValidationError):
            return JSONResponse(
                {"error": "Validation error", "details": exc.errors()},
                status_code=400
            )
        else:
            return JSONResponse(
                {"error": "Internal server error"},
                status_code=500
            )
```

## Compression Middleware

Compress responses:

```python
class CompressionMiddleware(Middleware):
    def __init__(self, minimum_size: int = 1000):
        self.minimum_size = minimum_size
        
    async def process_response(self, response: Response) -> Response:
        if len(response.body) < self.minimum_size:
            return response
            
        accept_encoding = request.headers.get("Accept-Encoding", "")
        
        if "gzip" in accept_encoding:
            response.body = gzip.compress(response.body)
            response.headers["Content-Encoding"] = "gzip"
        elif "deflate" in accept_encoding:
            response.body = zlib.compress(response.body)
            response.headers["Content-Encoding"] = "deflate"
            
        return response
```

## Middleware Order

The order of middleware is important:

```python
app = ZephyrApp()

# Order matters!
app.add_middleware(ErrorHandlerMiddleware)  # First to catch all errors
app.add_middleware(AuthMiddleware)          # Then authentication
app.add_middleware(RateLimitMiddleware)     # Then rate limiting
app.add_middleware(CORSMiddleware)          # Then CORS
app.add_middleware(CompressionMiddleware)   # Finally compression
```

## Custom Middleware

Create your own middleware:

```python
class CustomMiddleware(Middleware):
    async def process_request(self, request: Request) -> Request:
        # Modify request
        return request
        
    async def process_response(self, response: Response) -> Response:
        # Modify response
        return response
        
    async def process_exception(self, request: Request, exc: Exception) -> Response:
        # Handle exception
        return response
