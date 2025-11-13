# Database & ORM Layer Proposal

## Executive Summary

Implement a comprehensive, async-first database abstraction layer for Zephyr that provides SQLAlchemy integration, automatic migrations, query building, and connection management. This addresses the framework's most critical gap and enables real-world application development.

**Priority**: 🔴 **Critical**  
**Effort**: 4 weeks  
**Impact**: High - Unlocks application development capabilities

## Current State Analysis

### ✅ What Exists
- Database configuration in settings (`DATABASE_URL`, pool settings)
- Basic database connection structure
- Configuration validation with Pydantic

### ❌ What's Missing
- SQLAlchemy integration and models
- Migration system and schema management
- Query builder and relationship handling
- Connection pooling and health checks
- Database CLI tools and utilities

### 📊 Completion Status
```mermaid
pie title Database Layer Completion
    "Configuration" : 80
    "Models & ORM" : 5
    "Migrations" : 0
    "Query Builder" : 10
    "CLI Tools" : 0
    "Testing" : 15
```

## Technical Architecture

### Database Layer Overview
```mermaid
graph TB
    subgraph "Application Layer"
        A[Zephyr App] --> B[Database Manager]
        B --> C[Session Factory]
    end
    
    subgraph "ORM Layer"
        D[Base Model] --> E[User Models]
        D --> F[System Models]
        G[Query Builder] --> H[Relationships]
        G --> I[Aggregations]
    end
    
    subgraph "Migration System"
        J[Migration Engine] --> K[Schema Changes]
        J --> L[Data Migrations]
        M[Version Control] --> N[Migration History]
    end
    
    subgraph "Connection Management"
        O[Connection Pool] --> P[Read Replicas]
        O --> Q[Write Primary]
        R[Health Checks] --> S[Failover Logic]
    end
    
    subgraph "Database Backends"
        T[PostgreSQL] --> U[AsyncPG]
        V[MySQL] --> W[AsyncMySQL]
        X[SQLite] --> Y[AIOSQLite]
    end
    
    B --> D
    B --> G
    B --> J
    B --> O
    O --> T
    O --> V
    O --> X
    
    style A fill:#f9f,stroke:#333,stroke-width:2px
    style B fill:#bbf,stroke:#333,stroke-width:2px
    style D fill:#bfb,stroke:#333,stroke-width:2px
    style J fill:#fbf,stroke:#333,stroke-width:2px
```

### Component Architecture
```mermaid
graph LR
    subgraph "zephyr/database/"
        A[__init__.py] --> B[manager.py]
        A --> C[models.py]
        A --> D[session.py]
        A --> E[query.py]
    end
    
    subgraph "zephyr/database/migrations/"
        F[engine.py] --> G[operations.py]
        F --> H[versions/]
        F --> I[alembic.ini]
    end
    
    subgraph "zephyr/database/backends/"
        J[base.py] --> K[postgresql.py]
        J --> L[mysql.py]
        J --> M[sqlite.py]
    end
    
    subgraph "zephyr/cli/database/"
        N[migrate.py] --> O[init.py]
        N --> P[seed.py]
        N --> Q[shell.py]
    end
```

## Feature Specifications

### Must Have Features

#### 1. Async SQLAlchemy Integration
```python
from zephyr.database import Base, session

class User(Base):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(unique=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

# Usage in routes
@app.get("/users/{user_id}")
async def get_user(user_id: int):
    async with session() as db:
        user = await db.get(User, user_id)
        return user
```

#### 2. Migration System
```bash
# CLI commands
zephyr db init                    # Initialize migrations
zephyr db migrate "Add users"     # Create migration
zephyr db upgrade                 # Apply migrations
zephyr db downgrade              # Rollback migrations
zephyr db current                # Show current version
zephyr db history                # Show migration history
```

#### 3. Query Builder
```python
from zephyr.database import Query

# Type-safe queries
users = await Query(User).where(
    User.email.contains("@example.com")
).order_by(User.created_at.desc()).limit(10).all()

# Relationships
posts = await Query(Post).join(User).where(
    User.active == True
).include(Post.author).all()

# Aggregations
stats = await Query(User).group_by(
    User.created_at.date()
).aggregate(
    count=func.count(),
    avg_age=func.avg(User.age)
).all()
```

#### 4. Connection Management
```python
# Automatic connection pooling
DATABASE_POOL_SIZE = 20
DATABASE_MAX_OVERFLOW = 10
DATABASE_POOL_TIMEOUT = 30

# Read/write splitting
DATABASE_READ_URLS = [
    "postgresql://read1:5432/db",
    "postgresql://read2:5432/db"
]
DATABASE_WRITE_URL = "postgresql://write:5432/db"
```

### Should Have Features

#### 1. Database Health Checks
```python
@app.get("/health/database")
async def database_health():
    return await db_manager.health_check()
    # Returns: {"status": "healthy", "connections": 15, "latency_ms": 2.3}
```

#### 2. Schema Introspection
```python
# Generate models from existing database
zephyr db introspect --output models.py

# Compare schema with models
zephyr db diff --check
```

#### 3. Database Seeding
```python
# Seed data for development
zephyr db seed --env development

# Custom seed files
# database/seeds/users.py
async def seed_users():
    users = [
        User(email="admin@example.com", role="admin"),
        User(email="user@example.com", role="user"),
    ]
    await session.add_all(users)
```

### Good to Have Features

#### 1. Database Sharding
```python
# Shard by user ID
DATABASE_SHARDS = {
    "shard1": "postgresql://shard1:5432/db",
    "shard2": "postgresql://shard2:5432/db"
}

# Automatic shard routing
user = await User.get(user_id)  # Routes to correct shard
```

#### 2. Query Caching
```python
# Automatic query result caching
@cached(ttl=300)
async def get_popular_posts():
    return await Query(Post).where(
        Post.views > 1000
    ).order_by(Post.views.desc()).limit(10).all()
```

#### 3. Database Monitoring
```python
# Query performance monitoring
DATABASE_SLOW_QUERY_THRESHOLD = 1.0  # seconds
DATABASE_QUERY_LOGGING = True

# Metrics collection
await db_metrics.record_query(query, duration, result_count)
```

## Implementation Roadmap

### Phase 1: Foundation (Week 1-2)
| Task | Priority | Effort | Dependencies |
|------|----------|--------|--------------|
| SQLAlchemy async setup | Critical | 3 days | None |
| Base model implementation | Critical | 2 days | SQLAlchemy |
| Session management | Critical | 2 days | SQLAlchemy |
| Basic query operations | Critical | 3 days | Models |

**Deliverables**:
- Working async SQLAlchemy integration
- Base model class with common fields
- Session factory and context managers
- CRUD operations for models

### Phase 2: Migrations (Week 2-3)
| Task | Priority | Effort | Dependencies |
|------|----------|--------|--------------|
| Alembic integration | Critical | 3 days | SQLAlchemy |
| Migration CLI commands | Critical | 2 days | Alembic |
| Auto-migration generation | High | 2 days | Models |
| Migration testing | High | 1 day | CLI |

**Deliverables**:
- Complete migration system
- CLI commands for database operations
- Automatic migration generation
- Migration rollback capabilities

### Phase 3: Advanced Features (Week 3-4)
| Task | Priority | Effort | Dependencies |
|------|----------|--------|--------------|
| Query builder | High | 4 days | Models |
| Connection pooling | High | 2 days | SQLAlchemy |
| Health checks | Medium | 1 day | Connection pool |
| Database seeding | Medium | 1 day | Models |

**Deliverables**:
- Type-safe query builder
- Production-ready connection management
- Database health monitoring
- Development data seeding

### Phase 4: Production Features (Week 4)
| Task | Priority | Effort | Dependencies |
|------|----------|--------|--------------|
| Read/write splitting | Medium | 2 days | Connection pool |
| Schema introspection | Medium | 2 days | SQLAlchemy |
| Performance monitoring | Low | 2 days | Query builder |
| Documentation | High | 1 day | All features |

**Deliverables**:
- Read replica support
- Schema comparison tools
- Query performance metrics
- Complete documentation

## File Structure

```
zephyr/
├── database/
│   ├── __init__.py              # Main exports and session factory
│   ├── manager.py               # Database manager and configuration
│   ├── models.py                # Base model and common mixins
│   ├── session.py               # Session management and context
│   ├── query.py                 # Query builder and utilities
│   ├── health.py                # Health checks and monitoring
│   ├── migrations/
│   │   ├── __init__.py
│   │   ├── engine.py            # Migration engine and operations
│   │   ├── env.py               # Alembic environment
│   │   ├── script.py.mako       # Migration template
│   │   └── versions/            # Migration files
│   └── backends/
│       ├── __init__.py
│       ├── base.py              # Abstract backend interface
│       ├── postgresql.py        # PostgreSQL backend
│       ├── mysql.py             # MySQL backend
│       └── sqlite.py            # SQLite backend
├── cli/
│   └── database/
│       ├── __init__.py
│       ├── migrate.py           # Migration commands
│       ├── seed.py              # Seeding commands
│       └── introspect.py        # Schema introspection
└── tests/
    └── database/
        ├── __init__.py
        ├── conftest.py          # Database test fixtures
        ├── test_models.py       # Model testing
        ├── test_queries.py      # Query builder testing
        ├── test_migrations.py   # Migration testing
        └── test_backends.py     # Backend testing
```

## Configuration Specifications

### Database Settings
```python
# zephyr/conf/base.py additions
class BaseSettings(PydanticBaseSettings):
    # Database Configuration
    DATABASE_URL: str = "sqlite:///./app.db"
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 10
    DATABASE_POOL_TIMEOUT: int = 30
    DATABASE_POOL_RECYCLE: int = 3600
    
    # Read/Write Splitting
    DATABASE_READ_URLS: list[str] = []
    DATABASE_WRITE_URL: str | None = None
    
    # Migration Settings
    DATABASE_MIGRATION_DIR: str = "migrations"
    DATABASE_AUTO_MIGRATE: bool = False
    
    # Development Settings
    DATABASE_ECHO: bool = False
    DATABASE_ECHO_POOL: bool = False
    
    # Performance Settings
    DATABASE_SLOW_QUERY_THRESHOLD: float = 1.0
    DATABASE_QUERY_LOGGING: bool = False
```

### Environment Configuration
```bash
# .env file
DATABASE_URL=postgresql+asyncpg://user:pass@localhost/zephyr
DATABASE_POOL_SIZE=20
DATABASE_ECHO=false

# Production with read replicas
DATABASE_WRITE_URL=postgresql+asyncpg://user:pass@primary/zephyr
DATABASE_READ_URLS=postgresql+asyncpg://user:pass@replica1/zephyr,postgresql+asyncpg://user:pass@replica2/zephyr
```

## Testing Strategy

### Test Coverage Requirements
| Component | Target Coverage | Test Types |
|-----------|----------------|------------|
| Models | 95% | Unit, Integration |
| Query Builder | 90% | Unit, Integration |
| Migrations | 85% | Integration, E2E |
| Session Management | 95% | Unit, Integration |
| Connection Pooling | 80% | Integration, Load |

### Test Implementation
```python
# tests/database/conftest.py
@pytest.fixture
async def db_session():
    """Provide clean database session for tests."""
    async with test_session() as session:
        yield session
        await session.rollback()

@pytest.fixture
async def sample_user(db_session):
    """Create sample user for testing."""
    user = User(email="test@example.com")
    db_session.add(user)
    await db_session.commit()
    return user

# tests/database/test_models.py
class TestUserModel:
    async def test_create_user(self, db_session):
        user = User(email="new@example.com")
        db_session.add(user)
        await db_session.commit()
        
        assert user.id is not None
        assert user.created_at is not None
    
    async def test_unique_email_constraint(self, db_session, sample_user):
        duplicate_user = User(email=sample_user.email)
        db_session.add(duplicate_user)
        
        with pytest.raises(IntegrityError):
            await db_session.commit()
```

## Performance Benchmarks

### Target Performance Metrics
| Operation | Target | Measurement |
|-----------|--------|-------------|
| Simple SELECT | < 5ms | 95th percentile |
| Complex JOIN | < 50ms | 95th percentile |
| INSERT/UPDATE | < 10ms | 95th percentile |
| Migration | < 30s | Per migration |
| Connection Pool | < 1ms | Connection acquisition |

### Load Testing Scenarios
```python
# Performance test scenarios
async def test_concurrent_reads():
    """Test 100 concurrent read operations."""
    tasks = [get_user(i) for i in range(100)]
    results = await asyncio.gather(*tasks)
    assert len(results) == 100

async def test_connection_pool_exhaustion():
    """Test behavior when pool is exhausted."""
    # Create more connections than pool size
    # Verify graceful handling and queuing
```

## Dependencies

### Required Dependencies
```toml
# pyproject.toml additions
dependencies = [
    # Existing dependencies...
    "sqlalchemy[asyncio]>=2.0.0",
    "alembic>=1.12.0",
    "asyncpg>=0.28.0",        # PostgreSQL
    "aiomysql>=0.2.0",        # MySQL
    "aiosqlite>=0.19.0",      # SQLite
]
```

### Optional Dependencies
```toml
[project.optional-dependencies]
database = [
    "psycopg2-binary>=2.9.0",  # Sync PostgreSQL (for migrations)
    "pymysql>=1.1.0",          # Sync MySQL (for migrations)
    "python-magic>=0.4.27",    # File type detection
]
```

## Risk Assessment

### High Risk Items
| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| SQLAlchemy 2.0 breaking changes | High | Low | Pin versions, extensive testing |
| Migration data loss | Critical | Low | Backup requirements, rollback testing |
| Connection pool exhaustion | High | Medium | Pool monitoring, circuit breakers |

### Medium Risk Items
| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Performance regression | Medium | Medium | Benchmarking, performance tests |
| Database backend compatibility | Medium | Low | Multi-backend testing |
| Complex query optimization | Medium | High | Query analysis tools |

## Success Metrics

### Functional Metrics
- ✅ All CRUD operations working with async/await
- ✅ Migration system with rollback capabilities
- ✅ Connection pooling with health checks
- ✅ Query builder with type safety
- ✅ CLI tools for database management

### Performance Metrics
- ✅ < 5ms for simple queries (95th percentile)
- ✅ < 50ms for complex queries (95th percentile)
- ✅ > 1000 concurrent connections supported
- ✅ < 30s migration execution time

### Developer Experience Metrics
- ✅ < 5 minutes to set up new project with database
- ✅ < 2 minutes to create and apply migration
- ✅ Type hints and IDE autocompletion working
- ✅ Comprehensive error messages and debugging

## Next Steps

### Immediate Actions (Week 1)
1. **Set up SQLAlchemy async configuration**
2. **Create base model class and session factory**
3. **Implement basic CRUD operations**
4. **Set up Alembic for migrations**

### Short-term Goals (Month 1)
1. **Complete migration system with CLI**
2. **Implement query builder with relationships**
3. **Add connection pooling and health checks**
4. **Create comprehensive test suite**

### Integration Points
- **Settings System**: Database configuration integration
- **CLI Framework**: Database management commands
- **Testing Framework**: Database test utilities
- **Monitoring**: Database performance metrics

---

**Related Proposals**:
- [Universal Storage](./universal-storage.md) - File storage abstraction
- [Observability & Monitoring](./observability-monitoring.md) - Database monitoring
- [Developer Experience](./developer-experience.md) - CLI tools and testing

---

*Last Updated: January 2024*  
*Version: 1.0*  
*Status: Ready for Implementation*





