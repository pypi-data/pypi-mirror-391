# Database Guide

This guide covers database operations in the Zephyr Framework.

## Database Architecture

```mermaid
graph TD
    A[Application] --> B[Database Manager]
    B --> C[Connection Pool]
    C --> D[(Primary DB)]
    C --> E[(Replica DB)]
    B --> F[Query Builder]
    B --> G[Model Layer]
    F --> H[SQL Generator]
    G --> I[Validation]
    style A fill:#f9f,stroke:#333,stroke-width:2px
    style B fill:#bbf,stroke:#333,stroke-width:2px
    style C,F,G fill:#dfd,stroke:#333,stroke-width:2px
    style D,E fill:#ddd,stroke:#333,stroke-width:2px
    style H,I fill:#fdd,stroke:#333,stroke-width:2px
```

## Models

Define your data models with validation:

```python
from zephyr.db import Model, Field
from zephyr.validators import Length, Email

class User(Model):
    id: int = Field(primary_key=True)
    username: str = Field(
        unique=True,
        validators=[Length(min=3, max=50)]
    )
    email: str = Field(
        unique=True,
        validators=[Email()]
    )
    is_active: bool = Field(default=True)

    class Config:
        table_name = "users"
```

## Query Builder

```mermaid
graph LR
    A[Query Builder] --> B[Select]
    A --> C[Insert]
    A --> D[Update]
    A --> E[Delete]
    B --> F[Join]
    B --> G[Where]
    B --> H[Order]
    B --> I[Group]
    style A fill:#f9f,stroke:#333,stroke-width:2px
    style B,C,D,E fill:#bbf,stroke:#333,stroke-width:2px
    style F,G,H,I fill:#dfd,stroke:#333,stroke-width:2px
```

Example usage:

```python
# Select query
users = await db.query(User).where(
    User.is_active == True
).order_by(
    User.username.asc()
).limit(10).all()

# Join query
results = await db.query(Order).join(
    User, Order.user_id == User.id
).where(
    User.is_active == True
).select(
    Order, User.username
).all()
```

## Migrations

```mermaid
graph TD
    A[Migration Manager] --> B[Version Control]
    A --> C[Schema Changes]
    B --> D[Up Migration]
    B --> E[Down Migration]
    C --> F[Create Table]
    C --> G[Alter Table]
    C --> H[Drop Table]
    style A fill:#f9f,stroke:#333,stroke-width:2px
    style B,C fill:#bbf,stroke:#333,stroke-width:2px
    style D,E fill:#dfd,stroke:#333,stroke-width:2px
    style F,G,H fill:#fdd,stroke:#333,stroke-width:2px
```

Example migration:

```python
from zephyr.db import Migration

class CreateUsersTable(Migration):
    async def up(self):
        await self.create_table("users", [
            ("id", "serial", "primary key"),
            ("username", "varchar(50)", "unique not null"),
            ("email", "varchar(255)", "unique not null"),
            ("created_at", "timestamp", "default current_timestamp")
        ])

    async def down(self):
        await self.drop_table("users")
```

## Relationships

```mermaid
graph LR
    A[User] -->|One-to-Many| B[Order]
    A -->|One-to-One| C[Profile]
    A -->|Many-to-Many| D[Role]
    style A,B,C,D fill:#f9f,stroke:#333,stroke-width:2px
```

Define relationships:

```python
class User(Model):
    id: int = Field(primary_key=True)
    username: str = Field(unique=True)
    
    # Relationships
    profile = Relationship("Profile", back_populates="user")
    orders = Relationship("Order", back_populates="user")
    roles = Relationship(
        "Role",
        secondary="user_roles",
        back_populates="users"
    )

class Order(Model):
    id: int = Field(primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    amount: float = Field()
    
    # Relationship
    user = Relationship("User", back_populates="orders")
```

## Transactions

```mermaid
sequenceDiagram
    participant A as Application
    participant T as Transaction
    participant D as Database
    
    A->>T: Begin Transaction
    activate T
    T->>D: START TRANSACTION
    T-->>A: Transaction Context
    A->>D: Execute Queries
    A->>T: Commit/Rollback
    T->>D: COMMIT/ROLLBACK
    deactivate T
    T-->>A: Result
```

Example usage:

```python
async def create_order(user_id: int, items: List[dict]):
    async with db.transaction():
        # Create order
        order = await Order.create(user_id=user_id)
        
        # Create order items
        for item in items:
            await OrderItem.create(
                order_id=order.id,
                **item
            )
            
        # Update inventory
        for item in items:
            product = await Product.get(item["product_id"])
            product.stock -= item["quantity"]
            await product.save()
            
        return order
```

## Connection Management

```mermaid
graph TD
    A[Connection Pool] --> B[Primary]
    A --> C[Replica 1]
    A --> D[Replica 2]
    B --> E[Write Operations]
    C --> F[Read Operations]
    D --> F
    style A fill:#f9f,stroke:#333,stroke-width:2px
    style B,C,D fill:#bbf,stroke:#333,stroke-width:2px
    style E,F fill:#dfd,stroke:#333,stroke-width:2px
```

Configure database connections:

```python
app.config.database = {
    "primary": {
        "url": "postgresql://localhost/myapp",
        "pool_size": 10
    },
    "replicas": [{
        "url": "postgresql://replica1/myapp",
        "pool_size": 5
    }, {
        "url": "postgresql://replica2/myapp",
        "pool_size": 5
    }]
}
```
