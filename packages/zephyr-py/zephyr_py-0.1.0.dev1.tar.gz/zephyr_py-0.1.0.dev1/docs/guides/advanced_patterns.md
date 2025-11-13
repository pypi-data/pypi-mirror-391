# Advanced Development Patterns

## 1. Event-Driven Architecture

### Event Publishing
```python
from zephyr.events import EventBus, event

@event.publisher
class OrderService:
    async def create_order(self, order: Order):
        # Business logic
        result = await self.db.create(order)
        
        # Publish event
        await self.events.publish(
            "order.created",
            payload=result,
            partition_key=order.user_id
        )

@event.subscriber("order.created")
async def handle_order(event: Event):
    # Process order asynchronously
    await process_order(event.payload)
```

### Event Sourcing
```python
from zephyr.events import EventSourced, event_handler

@event_sourced
class UserAggregate:
    def __init__(self):
        self.balance = 0
        self.status = "active"

    @event_handler("deposit")
    def handle_deposit(self, amount: int):
        self.balance += amount

    @event_handler("withdraw")
    def handle_withdraw(self, amount: int):
        if self.balance >= amount:
            self.balance -= amount
        else:
            raise InsufficientFunds()
```

## 2. Advanced Database Patterns

### Repository Pattern
```python
from zephyr.db import Repository, Query

class UserRepository(Repository[User]):
    async def find_active_users(
        self,
        age: int,
        country: str
    ) -> list[User]:
        return await self.find(
            Query()
            .where(User.active == True)
            .where(User.age >= age)
            .where(User.country == country)
            .order_by(User.created_at.desc())
            .limit(100)
        )

    @cached(ttl="5m")
    async def get_by_email(self, email: str) -> User:
        return await self.find_one(
            User.email == email
        )
```

### Unit of Work Pattern
```python
from zephyr.db import UnitOfWork

async with UnitOfWork() as uow:
    # All operations in a single transaction
    user = await uow.users.create(user_data)
    order = await uow.orders.create(order_data)
    
    # Commit or rollback automatically
    await uow.commit()
```

## 3. Advanced API Patterns

### API Versioning
```python
from zephyr import api, version

@api.controller("/users")
class UserAPI:
    @api.get("/", version="1")
    async def get_users_v1(self):
        return await self.service.get_users()

    @api.get("/", version="2")
    async def get_users_v2(self):
        return await self.service.get_users_extended()

# Access via /v1/users or /v2/users
```

### API Composition
```python
from zephyr.api import compose

@compose.query(
    users=UserService.get_users,
    orders=OrderService.get_orders,
    parallel=True  # Run in parallel
)
async def get_user_dashboard(user_id: UUID):
    return {
        "users": await users,  # Auto-resolved
        "orders": await orders  # Auto-resolved
    }
```

## 4. Advanced Testing Patterns

### Behavior Testing
```python
from zephyr.testing import behavior

@behavior("User Registration")
async def test_user_registration():
    # Given
    with given("a new user"):
        user = create_test_user()

    # When
    with when("registering the user"):
        result = await register_user(user)

    # Then
    with then("user should be created"):
        assert result.status == "success"
        assert await db.users.exists(user.id)
```

### Performance Testing
```python
from zephyr.testing import benchmark

@benchmark(
    iterations=1000,
    concurrency=10,
    warmup=True
)
async def test_api_performance():
    async with client.get("/api/users") as response:
        assert response.status == 200
```

## 5. Advanced Security Patterns

### Role-Based Access Control
```python
from zephyr.security import rbac, Role

@rbac.role("admin")
class AdminRole(Role):
    permissions = {
        "users": ["create", "read", "update", "delete"],
        "orders": ["read", "update"]
    }

@api.get("/users")
@rbac.require("users.read")
async def get_users():
    return await users.find()
```

### Rate Limiting
```python
from zephyr.security import rate_limit

@rate_limit(
    limit="100/minute",
    by="ip",
    burst=10,
    strategy="token_bucket"
)
async def protected_api():
    return await process_request()
```

## 6. Developer Tools

### Interactive Debug Shell
```python
from zephyr.debug import shell

# Launch interactive shell
@app.command()
async def debug():
    await shell.launch(
        context={
            "db": app.db,
            "cache": app.cache,
            "services": app.services
        }
    )
```

### API Documentation
```python
from zephyr.docs import document

@document.api(
    summary="Create user",
    description="Creates a new user in the system",
    responses={
        201: {"model": UserResponse},
        400: {"model": ErrorResponse}
    }
)
@app.post("/users")
async def create_user(data: UserCreate):
    return await create_user(data)
```

### Development Dashboard
```python
from zephyr.dev import dashboard

# Launch dev dashboard
@app.command()
async def dashboard():
    await dashboard.launch(
        features=[
            "metrics",
            "logs",
            "traces",
            "requests"
        ]
    )
```

## 7. Advanced Monitoring

### Custom Metrics
```python
from zephyr.metrics import metric

@metric.gauge("user_count")
async def track_users():
    return await db.users.count()

@metric.histogram("response_time")
async def track_response(duration: float):
    # Automatically tracked
    pass
```

### Health Checks
```python
from zephyr.health import health_check

@health_check("database")
async def check_database():
    try:
        await db.ping()
        return Health.up()
    except Exception as e:
        return Health.down(str(e))
```

## 8. Code Generation Tools

### API Client Generation
```bash
# Generate TypeScript client
zephyr generate client --lang typescript

# Generate OpenAPI spec
zephyr generate openapi
```

### Database Migration
```bash
# Generate migration
zephyr db migrate --name add_user_table

# Apply migration
zephyr db upgrade
```

## Next Steps
1. [Example Applications](examples.md)
2. [Performance Tuning](performance.md)
3. [Production Deployment](deployment.md)
