# Zephyr vs FastAPI - API Comparison

This guide helps FastAPI developers transition to Zephyr by showing equivalent patterns.

## Basic Application

### FastAPI
```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### Zephyr
```python
from zephyr import Zephyr

app = Zephyr()

@app.get("/")
async def root():
    return {"message": "Hello World"}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
```

**Key Difference:** Zephyr has built-in server, no need for uvicorn import.

## Lifecycle Events

### FastAPI
```python
@app.on_event("startup")
async def startup():
    print("Starting up...")

@app.on_event("shutdown")
async def shutdown():
    print("Shutting down...")
```

### Zephyr
```python
@app.on_event("startup")
async def startup():
    print("Starting up...")

@app.on_event("shutdown")
async def shutdown():
    print("Shutting down...")
```

**Identical!** ✅

## Exception Handlers

### FastAPI
```python
from fastapi import Request
from fastapi.responses import JSONResponse

@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    return JSONResponse(
        status_code=400,
        content={"error": str(exc)}
    )
```

### Zephyr
```python
from zephyr.app.requests import Request
from zephyr.app.responses import JSONResponse

@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    return JSONResponse(
        {"error": str(exc)},
        status_code=400
    )
```

**Nearly Identical!** Minor differences in JSONResponse signature.

## Router Composition

### FastAPI
```python
from fastapi import APIRouter

router = APIRouter()

@router.get("/users")
async def list_users():
    return {"users": []}

app.include_router(router, prefix="/api/v1")
```

### Zephyr
```python
from zephyr.app.routing import Router

router = Router()

@router.get("/users")
async def list_users():
    return {"users": []}

app.include_router(router, prefix="/api/v1")
```

**Nearly Identical!** Just different import paths.

## Path Parameters

### FastAPI
```python
@app.get("/users/{user_id}")
async def get_user(user_id: int):
    return {"user_id": user_id}
```

### Zephyr
```python
@app.get("/users/{user_id}")
async def get_user(user_id: int):
    return {"user_id": user_id}
```

**Identical!** ✅

## Request Body

### FastAPI
```python
from pydantic import BaseModel

class User(BaseModel):
    name: str
    email: str

@app.post("/users")
async def create_user(user: User):
    return user
```

### Zephyr
```python
from pydantic import BaseModel

class User(BaseModel):
    name: str
    email: str

@app.post("/users")
async def create_user(user: User):
    return user
```

**Identical!** ✅ (Zephyr uses Pydantic too)

## Manual Request Access

### FastAPI
```python
from fastapi import Request

@app.post("/echo")
async def echo(request: Request):
    body = await request.json()
    return body
```

### Zephyr
```python
from zephyr.app.requests import Request

@app.post("/echo")
async def echo(request: Request):
    body = await request.json()
    return body
```

**Nearly Identical!** Just different import path.

## Mounting Sub-Applications

### FastAPI
```python
from fastapi.staticfiles import StaticFiles

app.mount("/static", StaticFiles(directory="static"))
```

### Zephyr
```python
# Use any ASGI static files middleware
app.mount("/static", static_files_app)
```

**Similar!** Zephyr accepts any ASGI app.

## Dependency Injection

### FastAPI
```python
from fastapi import Depends

def get_db():
    return Database()

@app.get("/users")
async def list_users(db = Depends(get_db)):
    return db.get_users()

# Override for testing
app.dependency_overrides[get_db] = get_test_db
```

### Zephyr
```python
# Dependency injection coming soon
# For now, use manual dependency management

# Override for testing
app.dependency_overrides[get_db] = get_test_db  # ✅ Available
```

**Partial Support:** Override mechanism exists, full DI coming soon.

## Response Models

### FastAPI
```python
from pydantic import BaseModel

class UserOut(BaseModel):
    id: int
    name: str

@app.get("/users/{user_id}", response_model=UserOut)
async def get_user(user_id: int):
    return {"id": user_id, "name": "Alice", "password": "secret"}
    # password field automatically excluded
```

### Zephyr
```python
from pydantic import BaseModel

class UserOut(BaseModel):
    id: int
    name: str

@app.get("/users/{user_id}")
async def get_user(user_id: int) -> UserOut:
    return UserOut(id=user_id, name="Alice")
```

**Different Approach:** Use return type hints instead of response_model parameter.

## Status Codes

### FastAPI
```python
@app.post("/users", status_code=201)
async def create_user(user: User):
    return user
```

### Zephyr
```python
@app.post("/users", status_code=201)
async def create_user(user: User):
    return user
```

**Identical!** ✅

## Middleware

### FastAPI
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"]
)
```

### Zephyr
```python
app.use_cors(
    allow_origins=["*"],
    allow_methods=["*"]
)

# Or use add_middleware
from zephyr.app.middleware.cors import CORSMiddleware
app.add_middleware(CORSMiddleware, allow_origins=["*"])
```

**Similar!** Zephyr provides convenience method `use_cors()`.

## Background Tasks

### FastAPI
```python
from fastapi import BackgroundTasks

@app.post("/send-email")
async def send_email(background_tasks: BackgroundTasks):
    background_tasks.add_task(send_email_task, "user@example.com")
    return {"message": "Email queued"}
```

### Zephyr
```python
# Background tasks coming soon
# For now, use asyncio.create_task() or similar
```

**Not Yet Implemented** in Zephyr.

## OpenAPI/Swagger Docs

### FastAPI
```python
# Automatic at /docs and /redoc
app = FastAPI(
    title="My API",
    version="1.0.0",
    description="API description"
)
```

### Zephyr
```python
# OpenAPI schema at /openapi.json
# Full docs UI coming soon
app = Zephyr(
    title="My API",
    version="1.0.0",
    description="API description"
)
```

**Partial Support:** Schema generation exists, UI coming soon.

## Key Differences Summary

| Feature | FastAPI | Zephyr | Status |
|---------|---------|--------|--------|
| Basic routing | ✅ | ✅ | Identical |
| Path parameters | ✅ | ✅ | Identical |
| Request body | ✅ | ✅ | Identical |
| Lifecycle events | ✅ | ✅ | Identical |
| Exception handlers | ✅ | ✅ | Nearly identical |
| Router composition | ✅ | ✅ | Nearly identical |
| Built-in server | ❌ (needs uvicorn) | ✅ | Zephyr advantage |
| Dependency injection | ✅ Full | ⚠️ Partial | FastAPI advantage |
| Response models | ✅ | ⚠️ Manual | FastAPI advantage |
| Background tasks | ✅ | ❌ | FastAPI advantage |
| OpenAPI UI | ✅ | ⚠️ Schema only | FastAPI advantage |
| WebSockets | ✅ | ✅ | Both supported |
| Middleware | ✅ | ✅ | Both supported |

## Migration Checklist

When migrating from FastAPI to Zephyr:

- [x] Change imports: `fastapi` → `zephyr`
- [x] Change `FastAPI()` → `Zephyr()`
- [x] Change `uvicorn.run()` → `app.run()`
- [x] Update Request imports
- [x] Update Response imports
- [x] Update Router imports
- [ ] Refactor dependency injection (if used heavily)
- [ ] Refactor response models (use return types)
- [ ] Refactor background tasks (use asyncio)
- [ ] Update OpenAPI docs expectations

## Why Choose Zephyr?

1. **Built-in Server** - No external server dependency
2. **Simpler API** - Less magic, more explicit
3. **Performance** - Custom server optimized for speed
4. **Flexibility** - Lower-level control when needed
5. **Modern Python** - Built for Python 3.11+

## Why Choose FastAPI?

1. **Mature Ecosystem** - More third-party integrations
2. **Full Dependency Injection** - More sophisticated DI system
3. **Automatic Docs** - Beautiful interactive documentation
4. **Larger Community** - More tutorials and examples
5. **Battle-tested** - Used in production by many companies

## Conclusion

Zephyr provides a FastAPI-like developer experience with a simpler, more explicit API. If you're comfortable with FastAPI's patterns, you'll feel right at home with Zephyr. The main differences are in advanced features like dependency injection and automatic documentation, which are planned for future releases.

For most CRUD APIs and microservices, Zephyr provides everything you need with less complexity.

