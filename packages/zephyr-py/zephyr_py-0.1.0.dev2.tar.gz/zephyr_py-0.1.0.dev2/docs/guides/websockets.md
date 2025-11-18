# WebSocket Guide

This guide covers WebSocket implementation in the Zephyr Framework.

## WebSocket Architecture

```mermaid
graph TD
    A[WebSocket Server] --> B[Connection Manager]
    B --> C[Room Manager]
    B --> D[Event Handler]
    C --> E[Room 1]
    C --> F[Room 2]
    D --> G[Message Handler]
    D --> H[Error Handler]
    style A fill:#f9f,stroke:#333,stroke-width:2px
    style B,C,D fill:#bbf,stroke:#333,stroke-width:2px
    style E,F,G,H fill:#dfd,stroke:#333,stroke-width:2px
```

## Connection Lifecycle

```mermaid
sequenceDiagram
    participant C as Client
    participant S as Server
    participant M as Manager
    participant R as Room
    
    C->>S: WebSocket Upgrade
    S->>M: Register Connection
    M->>R: Join Room
    R-->>M: Room Joined
    M-->>S: Connection Ready
    S-->>C: Connection Established
    
    loop Message Exchange
        C->>S: Send Message
        S->>R: Broadcast Message
        R->>S: Message Broadcasted
        S-->>C: Receive Message
    end
    
    C->>S: Close Connection
    S->>M: Unregister Connection
    M->>R: Leave Room
    R-->>M: Room Left
    M-->>S: Connection Closed
    S-->>C: Connection Terminated
```

## Basic Implementation

```python
from zephyr.websockets import WebSocket, WebSocketManager

manager = WebSocketManager()

@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await manager.connect(ws)
    try:
        while True:
            data = await ws.receive_json()
            await manager.broadcast(data)
    except WebSocketDisconnect:
        await manager.disconnect(ws)
```

## Room Management

```mermaid
graph TD
    A[Room Manager] --> B[Create Room]
    A --> C[Join Room]
    A --> D[Leave Room]
    A --> E[Broadcast]
    B --> F[Room State]
    C --> F
    D --> F
    E --> G[Room Members]
    style A fill:#f9f,stroke:#333,stroke-width:2px
    style B,C,D,E fill:#bbf,stroke:#333,stroke-width:2px
    style F,G fill:#dfd,stroke:#333,stroke-width:2px
```

Example implementation:

```python
@app.websocket("/ws/{room_id}")
async def room_websocket(
    ws: WebSocket,
    room_id: str
):
    await manager.connect(ws)
    await manager.join_room(ws, room_id)
    try:
        while True:
            data = await ws.receive_json()
            await manager.broadcast_to_room(room_id, data)
    except WebSocketDisconnect:
        await manager.leave_room(ws, room_id)
        await manager.disconnect(ws)
```

## Real-time Events

```mermaid
graph LR
    A[Event Source] --> B{Event Bus}
    B --> C[WebSocket Manager]
    C --> D[Room 1]
    C --> E[Room 2]
    D --> F[Client 1]
    D --> G[Client 2]
    E --> H[Client 3]
    style A fill:#f9f,stroke:#333,stroke-width:2px
    style B fill:#bbf,stroke:#333,stroke-width:2px
    style C fill:#dfd,stroke:#333,stroke-width:2px
    style D,E fill:#fdd,stroke:#333,stroke-width:2px
    style F,G,H fill:#dff,stroke:#333,stroke-width:2px
```

## Authentication

```mermaid
sequenceDiagram
    participant C as Client
    participant S as Server
    participant A as Auth Service
    
    C->>S: WS Connection + Token
    S->>A: Validate Token
    A-->>S: User Data
    S->>S: Store User Context
    S-->>C: Connection Accepted
```

Example:

```python
@app.websocket("/ws")
async def authenticated_websocket(
    ws: WebSocket,
    token: str = Query(...),
    auth: AuthService = Depends()
):
    user = await auth.validate_token(token)
    if not user:
        await ws.close(code=4001)
        return
        
    await manager.connect(ws, user)
    try:
        while True:
            data = await ws.receive_json()
            # Add user context to message
            data["user"] = user.dict()
            await manager.broadcast(data)
    except WebSocketDisconnect:
        await manager.disconnect(ws)
```

## Message Types

```mermaid
graph TD
    A[Message] --> B[Text]
    A --> C[Binary]
    A --> D[JSON]
    B --> E[String Data]
    C --> F[Raw Bytes]
    D --> G[Structured Data]
    style A fill:#f9f,stroke:#333,stroke-width:2px
    style B,C,D fill:#bbf,stroke:#333,stroke-width:2px
    style E,F,G fill:#dfd,stroke:#333,stroke-width:2px
```

## Error Handling

```mermaid
graph TD
    A[Error Handler] --> B[Connection Error]
    A --> C[Message Error]
    A --> D[Auth Error]
    B --> E[Reconnect]
    C --> F[Error Response]
    D --> G[Close Connection]
    style A fill:#f9f,stroke:#333,stroke-width:2px
    style B,C,D fill:#bbf,stroke:#333,stroke-width:2px
    style E,F,G fill:#dfd,stroke:#333,stroke-width:2px
```

## Performance Optimization

```mermaid
graph LR
    A[Optimization] --> B[Connection Pool]
    A --> C[Message Queue]
    A --> D[Load Balancing]
    B --> E[Max Connections]
    C --> F[Message Buffer]
    D --> G[Multiple Nodes]
    style A fill:#f9f,stroke:#333,stroke-width:2px
    style B,C,D fill:#bbf,stroke:#333,stroke-width:2px
    style E,F,G fill:#dfd,stroke:#333,stroke-width:2px
```

## Client Implementation

```javascript
// Browser WebSocket client
const ws = new WebSocket('ws://localhost:8000/ws');

ws.onopen = () => {
    console.log('Connected to server');
    ws.send(JSON.stringify({
        type: 'join',
        room: 'main'
    }));
};

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log('Received:', data);
};

ws.onclose = () => {
    console.log('Disconnected from server');
};
```
