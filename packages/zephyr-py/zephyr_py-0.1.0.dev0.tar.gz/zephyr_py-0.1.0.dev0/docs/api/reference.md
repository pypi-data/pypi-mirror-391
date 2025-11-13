# API Reference

## Core API

### Service Decorator
```python
from zephyr import service

@service
class MyService:
    """
    Base service decorator that enables:
    - Dependency injection
    - Configuration management
    - Resource management
    - Automatic monitoring
    """
    pass
```

### Endpoint Decorator
```python
from zephyr import endpoint

@endpoint("/path", methods=["GET"])
async def my_endpoint():
    """
    Endpoint decorator that provides:
    - Automatic routing
    - Request validation
    - Response serialization
    - Error handling
    """
    pass
```

## Message Queue API

### Publisher
```python
from zephyr import queue

@queue.publisher("topic")
async def publish_message(message: dict):
    """
    Message publisher that provides:
    - Automatic serialization
    - Retry handling
    - Dead letter queue
    - Message tracking
    """
    pass
```

### Subscriber
```python
@queue.subscriber("topic")
async def handle_message(message: dict):
    """
    Message subscriber that provides:
    - Automatic deserialization
    - Error handling
    - Rate limiting
    - Message acknowledgment
    """
    pass
```

## State Management API

### State Store
```python
from zephyr import state

@state_managed
class StateStore:
    """
    State management that provides:
    - Distributed state
    - Conflict resolution
    - State versioning
    - Real-time sync
    """
    pass
```

### State Operations
```python
@state.update
async def update_state(key: str, value: Any):
    """
    State update operation that provides:
    - Atomic updates
    - Validation
    - Event generation
    - History tracking
    """
    pass
```

## Security API

### Authentication
```python
from zephyr import auth

@auth.required
async def secure_operation():
    """
    Authentication decorator that provides:
    - Token validation
    - Session management
    - Role verification
    - Access logging
    """
    pass
```

### Authorization
```python
from zephyr import rbac

@rbac.role("admin")
async def admin_operation():
    """
    Role-based access control that provides:
    - Role verification
    - Permission checking
    - Access logging
    - Audit trail
    """
    pass
```

## Service Mesh API

### Service Discovery
```python
from zephyr import mesh

@mesh.discover
async def find_service(name: str):
    """
    Service discovery that provides:
    - Automatic registration
    - Health checking
    - Load balancing
    - Circuit breaking
    """
    pass
```

### Load Balancing
```python
@mesh.balanced
async def balanced_call():
    """
    Load balancing that provides:
    - Request distribution
    - Health monitoring
    - Failure handling
    - Performance tracking
    """
    pass
```

## Monitoring API

### Metrics
```python
from zephyr import metrics

@metrics.track
async def tracked_operation():
    """
    Metrics tracking that provides:
    - Performance monitoring
    - Resource usage
    - Error tracking
    - Custom metrics
    """
    pass
```

### Tracing
```python
from zephyr import tracing

@tracing.span
async def traced_operation():
    """
    Distributed tracing that provides:
    - Request tracking
    - Performance analysis
    - Error tracking
    - Dependency mapping
    """
    pass
```

## Resource Management API

### Connection Pool
```python
from zephyr import resources

@resources.pooled
async def database_operation():
    """
    Connection pooling that provides:
    - Automatic scaling
    - Resource limits
    - Connection reuse
    - Error handling
    """
    pass
```

### Rate Limiting
```python
from zephyr import limits

@limits.rate(max_requests=100)
async def limited_operation():
    """
    Rate limiting that provides:
    - Request throttling
    - Burst handling
    - Client tracking
    - Quota management
    """
    pass
```

## Configuration API

### Config Management
```python
from zephyr import config

@config.managed
class ServiceConfig:
    """
    Configuration management that provides:
    - Environment variables
    - Secret management
    - Dynamic updates
    - Validation
    """
    pass
```

### Feature Flags
```python
from zephyr import features

@features.toggle("feature_name")
async def feature_operation():
    """
    Feature flags that provide:
    - Dynamic enabling
    - A/B testing
    - Gradual rollout
    - User targeting
    """
    pass
```

## Next Steps
1. [Implementation Guide](../guides/implementation.md)
2. [Security Guide](../guides/security.md)
3. [Deployment Guide](../guides/deployment.md)
