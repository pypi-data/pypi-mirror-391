# Core Concepts

This guide covers the fundamental concepts of the Zephyr Framework.

## Application Structure

```mermaid
graph TD
    A[Application] --> B[Config]
    A --> C[Router]
    A --> D[Middleware]
    C --> E[Controllers]
    C --> F[Views]
    D --> G[Auth]
    D --> H[CORS]
    D --> I[Cache]
    style A fill:#f9f,stroke:#333,stroke-width:2px
    style B,C,D fill:#bbf,stroke:#333,stroke-width:2px
    style E,F fill:#dfd,stroke:#333,stroke-width:2px
    style G,H,I fill:#fdd,stroke:#333,stroke-width:2px
```

## Dependency Injection

Zephyr uses a powerful dependency injection system:

```python
from zephyr.core import ZephyrApp
from zephyr.di import Depends, Injectable

@Injectable()
class UserService:
    def __init__(self, db: Database = Depends()):
        self.db = db

    async def get_user(self, user_id: int):
        return await self.db.users.get(id=user_id)

app = ZephyrApp()

@app.route("/users/{user_id}")
async def get_user(
    user_id: int,
    user_service: UserService = Depends()
):
    return await user_service.get_user(user_id)
```

## Request Flow

```mermaid
sequenceDiagram
    participant C as Client
    participant M as Middleware
    participant R as Router
    participant H as Handler
    participant D as Database

    C->>M: Request
    M->>R: Process
    R->>H: Route
    H->>D: Query
    D-->>H: Data
    H-->>R: Result
    R-->>M: Response
    M-->>C: Send
```

## Data Models

Define your data models with type safety:

```python
from zephyr.db import Model, Field

class User(Model):
    id: int = Field(primary_key=True)
    username: str = Field(unique=True)
    email: str = Field(unique=True)
    is_active: bool = Field(default=True)

    class Config:
        table_name = "users"
```

## Middleware Pipeline

```mermaid
graph LR
    A[Request] --> B[Auth]
    B --> C[CORS]
    C --> D[Rate Limit]
    D --> E[Cache]
    E --> F[Handler]
    F --> G[Response]
    style A,G fill:#f9f,stroke:#333,stroke-width:2px
    style B,C,D,E fill:#bbf,stroke:#333,stroke-width:2px
    style F fill:#dfd,stroke:#333,stroke-width:2px
```

## Service Layer

The service layer handles business logic:

```python
@Injectable()
class OrderService:
    def __init__(
        self,
        db: Database = Depends(),
        cache: Cache = Depends(),
        queue: Queue = Depends()
    ):
        self.db = db
        self.cache = cache
        self.queue = queue

    async def create_order(self, order_data: dict):
        # Transaction management
        async with self.db.transaction():
            # Create order
            order = await self.db.orders.create(**order_data)
            
            # Invalidate cache
            await self.cache.delete(f"user_orders:{order.user_id}")
            
            # Queue notification
            await self.queue.push("notifications", {
                "type": "order_created",
                "order_id": order.id
            })
            
            return order
```

## WebSocket Handling

```mermaid
graph TD
    A[WebSocket Connection] --> B[Connection Manager]
    B --> C{Room Manager}
    C --> D[Room 1]
    C --> E[Room 2]
    C --> F[Room 3]
    D --> G[Clients]
    E --> G
    F --> G
    style A fill:#f9f,stroke:#333,stroke-width:2px
    style B,C fill:#bbf,stroke:#333,stroke-width:2px
    style D,E,F fill:#dfd,stroke:#333,stroke-width:2px
    style G fill:#fdd,stroke:#333,stroke-width:2px
```

## Event System

```mermaid
graph LR
    A[Event Emitter] --> B{Event Bus}
    B --> C[Handler 1]
    B --> D[Handler 2]
    B --> E[Handler 3]
    style A fill:#f9f,stroke:#333,stroke-width:2px
    style B fill:#bbf,stroke:#333,stroke-width:2px
    style C,D,E fill:#dfd,stroke:#333,stroke-width:2px
```

## Configuration Management

```python
from zephyr.config import Config

config = Config({
    "app": {
        "name": "MyApp",
        "debug": True
    },
    "database": {
        "url": "postgresql://localhost/myapp",
        "pool_size": 10
    },
    "cache": {
        "url": "redis://localhost",
        "ttl": 3600
    }
})

app = ZephyrApp(config)
```

## Error Handling

```mermaid
graph TD
    A[Exception] --> B{Error Handler}
    B -->|HTTP Error| C[HTTP Response]
    B -->|Validation Error| D[Validation Response]
    B -->|Database Error| E[Error Response]
    B -->|Unknown Error| F[500 Response]
    style A fill:#f9f,stroke:#333,stroke-width:2px
    style B fill:#bbf,stroke:#333,stroke-width:2px
    style C,D,E,F fill:#fdd,stroke:#333,stroke-width:2px
```
