# Distributed Tracing

## Request Flow Tracing

```mermaid
sequenceDiagram
    participant C as Client
    participant A as API Gateway
    participant S1 as OrderService
    participant Q as Message Queue
    participant S2 as PaymentService
    participant S3 as NotificationService
    participant DB as Database

    C->>+A: POST /orders
    Note over A: Trace ID: xyz-123
    A->>+S1: Create Order
    S1->>DB: Save Order
    S1->>Q: Publish PaymentNeeded
    S1-->>-A: Order Created
    A-->>-C: 202 Accepted

    Q->>+S2: Process Payment
    S2->>DB: Update Payment
    S2->>Q: Publish PaymentComplete
    S2-->>-Q: Ack

    Q->>+S3: Send Notification
    S3->>DB: Log Notification
    S3-->>-Q: Ack
```

## Implementation Example

```python
@service
class OrderService:
    @traced
    async def create_order(self, order_data: dict) -> Order:
        with TraceContext() as trace:
            # Automatically captures the trace context
            trace.add_tag("order_type", order_data["type"])
            
            # Database operation is traced
            order = await self.db.create_order(order_data)
            
            # Message queue operation is traced
            await self.queue.publish(
                "payment_needed",
                {"order_id": order.id},
                trace_context=trace.context
            )
            
            return order

@service
class PaymentService:
    @traced
    async def handle_payment(self, message: Message) -> None:
        # Trace context is automatically extracted from message
        with TraceContext.from_message(message) as trace:
            trace.add_tag("payment_provider", self.provider)
            
            # Process payment
            payment = await self.process_payment(message.order_id)
            
            # Publish result with trace context
            await self.queue.publish(
                "payment_complete",
                {"payment_id": payment.id},
                trace_context=trace.context
            )

@service
class NotificationService:
    @traced
    async def notify_payment_complete(self, message: Message) -> None:
        with TraceContext.from_message(message) as trace:
            # Send notification
            await self.send_notification(message.payment_id)
```

## Trace Visualization

```mermaid
graph TD
    subgraph "Request Timeline"
        A[API Request<br/>0ms]
        B[Order Created<br/>50ms]
        C[Payment Started<br/>150ms]
        D[Payment Complete<br/>350ms]
        E[Notification Sent<br/>400ms]
    end

    A -->|50ms| B
    B -->|100ms| C
    C -->|200ms| D
    D -->|50ms| E

    style A fill:#f9f,stroke:#333
    style B fill:#bbf,stroke:#333
    style C fill:#bfb,stroke:#333
    style D fill:#fbf,stroke:#333
    style E fill:#ff9,stroke:#333
```

## Trace Context Propagation

```mermaid
graph TD
    subgraph "HTTP Headers"
        A[X-Trace-ID]
        B[X-Span-ID]
        C[X-Parent-ID]
    end

    subgraph "Message Properties"
        D[trace_id]
        E[span_id]
        F[parent_id]
    end

    subgraph "Database Query"
        G[comment: /*trace_id=xyz*/]
    end

    A --> D
    B --> E
    C --> F
    D --> G
```

## Configuration

```python
TRACING_CONFIG = {
    'service_name': 'order-service',
    'sampler': {
        'type': 'probabilistic',
        'rate': 0.1  # Sample 10% of requests
    },
    'propagation': {
        'http': True,
        'grpc': True,
        'messaging': True,
        'database': True
    },
    'exporters': [{
        'type': 'jaeger',
        'endpoint': 'http://jaeger:14268/api/traces'
    }]
}

@service(tracing=TRACING_CONFIG)
class TracedService:
    pass
```

## Performance Impact Analysis

```mermaid
pie title "Tracing Overhead Distribution"
    "Trace Context Creation" : 5
    "Context Propagation" : 3
    "Span Recording" : 7
    "Tag Management" : 2
    "Export" : 3
```

## Best Practices

1. **Sampling Strategy**
   - Use adaptive sampling
   - Sample more for errors
   - Keep important traces
   - Configure by endpoint

2. **Context Management**
   - Propagate full context
   - Preserve parent relations
   - Handle async operations
   - Clean up resources

3. **Performance**
   - Use sampling appropriately
   - Minimize tag count
   - Batch trace exports
   - Monitor overhead

4. **Integration**
   - Consistent service names
   - Meaningful operation names
   - Useful tags
   - Error tracking

## Error Tracing Example

```python
@service
class ResilientService:
    @traced
    async def critical_operation(self, data: dict) -> Result:
        with TraceContext() as trace:
            try:
                result = await self.process(data)
                trace.add_tag("status", "success")
                return result
            except Exception as e:
                trace.add_tag("status", "error")
                trace.add_tag("error_type", type(e).__name__)
                trace.add_tag("error_message", str(e))
                trace.mark_as_error()
                raise
```
