# Modern Development Patterns

## Quick Start

### Project Creation
```bash
# Create new project with interactive CLI
zephyr new my-api --interactive

# Or with specific template
zephyr new my-api --template microservice
```

## Modern API Patterns

### 1. Declarative APIs
```python
from zephyr import Zephyr, api, Query
from zephyr.types import UUID

app = Zephyr()

# Automatic OpenAPI docs, validation, serialization
@app.api_controller("/users")
class UserAPI:
    @app.get("/{user_id}")
    async def get_user(
        self, 
        user_id: UUID,                    # Automatic UUID validation
        include: list[str] = Query(...),  # Query parameters
        select: list[str] = ["id", "name"]  # Field selection
    ) -> UserResponse:                    # Automatic response validation
        return await self.service.get_user(
            id=user_id,
            include=include,
            select=select
        )
```

### 2. GraphQL Integration
```python
from zephyr import gql

@gql.type
class User:
    id: UUID
    name: str
    posts: list["Post"]

@gql.resolver(User)
async def resolve_posts(user: User):
    return await Post.find(author_id=user.id)

# Auto-generated GraphQL schema
"""
type User {
    id: ID!
    name: String!
    posts: [Post!]!
}
"""
```

### 3. Real-time WebSockets
```python
@app.websocket("/live")
class LiveUpdates:
    @app.on_connect
    async def handle_connect(self, socket: WebSocket):
        await self.authorize(socket)
        await self.subscribe(socket, "updates")

    @app.on_message
    async def handle_message(self, socket: WebSocket, data: dict):
        await self.process_message(data)
        await self.broadcast("updates", data)
```

### 4. Type-safe Database Queries
```python
from zephyr.db import Table, Column, ForeignKey

# Type-safe table definition
class UserTable(Table):
    id: Column[UUID]
    name: Column[str]
    email: Column[str]
    posts: ForeignKey["PostTable"]

# Type-safe queries
async def get_active_users():
    return await UserTable.select(
        UserTable.name, 
        UserTable.email
    ).where(
        UserTable.active == True
    ).limit(10)
```

### 5. Dependency Injection
```python
from zephyr import Inject, Service

class UserService(Service):
    def __init__(
        self,
        db: Inject[Database],
        cache: Inject[Cache],
        queue: Inject[MessageQueue],
        config: Inject[Config]
    ):
        self.db = db
        self.cache = cache
        self.queue = queue
        self.config = config

# Auto-injected in tests
@pytest.fixture
def user_service(mock_db, mock_cache):
    return UserService.create_test(
        db=mock_db,
        cache=mock_cache
    )
```

### 6. Advanced Validation
```python
from zephyr.validation import validate, field

@validate
class CreateUser:
    name: str = field(min_length=2)
    email: str = field(pattern=r"[^@]+@[^@]+\.[^@]+")
    age: int = field(ge=18)
    country: str = field(
        validate=lambda x: x in get_country_codes()
    )

@app.post("/users")
async def create_user(data: CreateUser):  # Automatic validation
    return await create_user(data)
```

### 7. Smart Caching
```python
from zephyr.cache import cached

class UserService:
    @cached(
        key="{user_id}",           # Dynamic key
        ttl="5m",                  # Time-based expiry
        strategy="write-through",   # Cache strategy
        invalidate_on=["update"]   # Auto invalidation
    )
    async def get_user(self, user_id: UUID):
        return await self.db.get_user(user_id)
```

### 8. Background Tasks
```python
from zephyr.tasks import task, schedule

@task(
    retry=3,                # Auto retry
    backoff="exponential",  # Exponential backoff
    timeout="30s"          # Task timeout
)
async def process_video(video_id: UUID):
    await process_video_file(video_id)

@schedule("0 0 * * *")  # Cron syntax
async def daily_cleanup():
    await cleanup_old_files()
```

### 9. Feature Flags
```python
from zephyr.features import feature

@feature("new-ui", percentage=50)  # A/B testing
async def get_user_interface(user_id: UUID):
    if feature.enabled("new-ui", user_id):
        return new_interface()
    return old_interface()
```

### 10. Middleware System
```python
from zephyr import middleware

@middleware
async def timing_middleware(request, call_next):
    start = time.time()
    response = await call_next(request)
    duration = time.time() - start
    
    # Automatic metrics
    metrics.timing("request_duration", duration)
    return response
```

### 11. Smart CLI
```python
from zephyr.cli import cli, argument

@cli.command()
@argument("--env", choices=["dev", "prod"])
@argument("--region", default="us-west")
async def deploy(env: str, region: str):
    """Deploy the application to specified environment"""
    await deployment.start(env, region)
```

### 12. Development Tools
```python
# Hot reload
zephyr dev --hot-reload

# API documentation
zephyr docs serve

# Database migrations
zephyr db migrate

# Performance profiling
zephyr profile --service user-service
```

### 13. Testing Utilities
```python
from zephyr.testing import TestClient, mock

async def test_user_api(client: TestClient):
    # Automatic mocking
    with mock.patch("email_service"):
        response = await client.post("/users", {
            "name": "Test User",
            "email": "test@example.com"
        })
        assert response.status_code == 201
```

### 14. Service Discovery
```python
from zephyr.discovery import discover

@discover
class PaymentService:
    # Automatic service registration
    name = "payment-service"
    version = "1.0.0"

    @discover.endpoint("/process")
    async def process_payment(self, amount: int):
        return await self.process(amount)
```

### 15. Observability
```python
from zephyr.telemetry import traced, metered

@traced("payment-processing")  # Distributed tracing
@metered                      # Automatic metrics
async def process_payment(payment_id: UUID):
    # Automatic trace context
    with trace.span("payment-validation"):
        await validate_payment(payment_id)
```

## Best Practices

### 1. Project Structure
```
my-api/
├── app/
│   ├── api/           # API endpoints
│   ├── services/      # Business logic
│   ├── models/        # Data models
│   └── utils/         # Utilities
├── tests/
│   ├── api/          # API tests
│   └── services/     # Service tests
└── config/
    ├── dev.yaml      # Development config
    └── prod.yaml     # Production config
```

### 2. Configuration Management
```python
from zephyr.config import config

@config.section("database")
class DatabaseConfig:
    url: str
    pool_size: int = 10
    timeout: str = "30s"

# Access config
db_config = config.get(DatabaseConfig)
```

### 3. Error Handling
```python
from zephyr.errors import HTTPError, error_handler

@error_handler(ValueError)
async def handle_validation_error(error):
    return HTTPError(
        status=400,
        code="VALIDATION_ERROR",
        message=str(error),
        details=error.details
    )
```

Next Steps:
1. [Advanced Patterns](advanced_patterns.md)
2. [Performance Optimization](performance.md)
3. [Security Best Practices](security.md)
