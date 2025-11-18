"""
WebSocket Example Application

This example demonstrates WebSocket support in Zephyr with:
- WebSocket endpoint decorator
- Message receiving and sending
- Proper connection management
- Graceful disconnection handling
"""

from zephyr import Zephyr
from zephyr.app.websockets import WebSocketDisconnect

app = Zephyr(title="WebSocket Example", version="1.0.0", description="Demonstrates WebSocket functionality")

# Keep track of connected clients
connected_clients = set()

# ========== Regular HTTP Routes ==========


@app.get("/")
async def root():
    """Root endpoint with WebSocket info."""
    return {
        "message": "Welcome to Zephyr WebSocket Example",
        "websocket_endpoint": "/ws",
        "connected_clients": len(connected_clients),
    }


@app.get("/status")
async def status():
    """Check number of connected WebSocket clients."""
    return {
        "connected_clients": len(connected_clients),
        "status": "active" if connected_clients else "no clients",
    }


# ========== WebSocket Routes ==========


@app.websocket("/ws")
async def websocket_endpoint(websocket):
    """
    WebSocket endpoint for real-time communication.

    Accepts connections, echoes back messages, and broadcasts to all clients.
    """
    await websocket.accept()
    client_id = id(websocket)
    connected_clients.add(websocket)

    app.logger.info("Client connected: %s (total: %d)", client_id, len(connected_clients))

    try:
        while True:
            # Receive text message from client
            data = await websocket.receive_text()
            app.logger.debug("Received from %s: %s", client_id, data)

            # Echo back to sender
            await websocket.send_text(f"Echo: {data}")

            # Broadcast to all clients
            app.logger.debug("Broadcasting to %d clients", len(connected_clients))
            for client in connected_clients:
                if client != websocket:  # Don't send to the sender again
                    try:
                        await client.send_text(f"Broadcast from {client_id}: {data}")
                    except Exception as e:
                        app.logger.warning("Failed to broadcast to client: %s", e)

    except WebSocketDisconnect as exc:
        connected_clients.discard(websocket)
        app.logger.info(
            "Client disconnected: %s (code: %d, total: %d)",
            client_id,
            exc.code,
            len(connected_clients),
        )
    except Exception as exc:
        app.logger.error("WebSocket error for %s: %s", client_id, exc, exc_info=True)
        connected_clients.discard(websocket)


@app.websocket("/chat")
async def chat_endpoint(websocket):
    """
    Chat-like WebSocket endpoint with room support.

    Simple chat implementation with message broadcasting.
    """
    await websocket.accept()
    client_id = id(websocket)

    app.logger.info("Chat client connected: %s", client_id)

    try:
        # Send welcome message
        await websocket.send_json(
            {
                "type": "connection",
                "message": f"You are connected as {client_id}",
                "total_clients": len(connected_clients),
            }
        )

        while True:
            # Receive JSON message
            message = await websocket.receive_json()
            app.logger.debug("Chat message from %s: %s", client_id, message)

            # Echo back with metadata
            response = {
                "type": "echo",
                "original_message": message,
                "client_id": client_id,
                "timestamp": "2025-11-13T10:59:00Z",
            }
            await websocket.send_json(response)

    except WebSocketDisconnect as exc:
        app.logger.info("Chat client disconnected: %s (code: %d)", client_id, exc.code)
    except Exception as exc:
        app.logger.error("Chat error for %s: %s", client_id, exc, exc_info=True)


# ========== Lifecycle Hooks ==========


@app.register_hook("after_startup")
async def startup():
    """Initialize on startup."""
    app.logger.info("WebSocket server starting up...")
    app.logger.info("WebSocket endpoints available:")
    app.logger.info("  - ws://localhost:8000/ws (Echo service)")
    app.logger.info("  - ws://localhost:8000/chat (Chat service)")


@app.register_hook("before_shutdown")
async def shutdown():
    """Cleanup on shutdown."""
    app.logger.info("WebSocket server shutting down...")
    app.logger.info("Closing %d connected clients", len(connected_clients))
    connected_clients.clear()


# ========== Run the Application ==========

if __name__ == "__main__":
    app.logger.info("Starting WebSocket Example Application")
    app.run(host="0.0.0.0", port=8000)
