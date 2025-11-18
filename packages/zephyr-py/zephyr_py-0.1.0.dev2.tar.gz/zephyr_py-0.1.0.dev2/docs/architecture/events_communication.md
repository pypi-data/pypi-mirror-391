# Events and Communication

## Event System Architecture

```mermaid
graph TD
    subgraph "Event Sources"
        A[Services]
        B[System]
        C[External]
    end

    subgraph "Event Bus"
        D[Event Router]
        E[Queue Manager]
        F[Dead Letter]
    end

    subgraph "Consumers"
        G[Services]
        H[Monitors]
        I[Loggers]
    end

    A --> D
    B --> D
    C --> D
    D --> E
    E --> G
    E --> H
    E --> I
    E --> F
```

## Event Flow

```mermaid
sequenceDiagram
    participant S as Service
    participant B as Event Bus
    participant Q as Queue
    participant C as Consumer

    S->>B: Emit Event
    B->>Q: Queue Event
    Q->>C: Process Event
    C->>B: Acknowledge
    
    alt Failed Processing
        C->>B: Retry
        B->>Q: Requeue
        Q->>C: Retry Process
    end
```

## Communication Patterns

```mermaid
mindmap
    root((Patterns))
        Pub/Sub
            Topic Based
            Content Based
        Request/Reply
            Sync
            Async
        Broadcast
            All Services
            Group Based
        Point to Point
            Direct
            Routed
```

## Service Communication

```mermaid
graph LR
    subgraph "Service A"
        A1[API]
        A2[Events]
    end

    subgraph "Event Bus"
        B1[Router]
        B2[Queue]
    end

    subgraph "Service B"
        C1[Handler]
        C2[Processor]
    end

    A1 --> B1
    A2 --> B1
    B1 --> B2
    B2 --> C1
    C1 --> C2
```

## Example: Event-Driven Service

```python
@service
class OrderService:
    @on_event("payment.completed")
    async def process_order(self, event):
        # Framework handles:
        # - Event subscription
        # - Message routing
        # - Retry logic
        # - Error handling
        await self.fulfill_order(event.order_id)

    @emit_event("order.fulfilled")
    async def fulfill_order(self, order_id):
        # Business logic only
        # Framework manages event emission
        return await self.orders.fulfill(order_id)
```

## Event Types

```mermaid
graph TD
    subgraph "System Events"
        A[Service Lifecycle]
        B[Health Status]
        C[Resource Usage]
    end

    subgraph "Business Events"
        D[Domain Events]
        E[Integration Events]
        F[User Events]
    end

    subgraph "Framework Events"
        G[Scaling Events]
        H[Config Changes]
        I[Deployments]
    end

    A --> D
    B --> E
    C --> F
    D --> G
    E --> H
    F --> I
```

## Event Reliability

```mermaid
stateDiagram-v2
    [*] --> Emitted
    Emitted --> Queued
    Queued --> Processing
    Processing --> Completed
    Processing --> Failed
    Failed --> Retry
    Retry --> Processing
    Failed --> DeadLetter
    Completed --> [*]
```
