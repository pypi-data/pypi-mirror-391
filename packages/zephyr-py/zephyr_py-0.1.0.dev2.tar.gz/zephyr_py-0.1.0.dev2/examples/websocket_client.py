"""
WebSocket Client Example

This script demonstrates how to connect to Zephyr WebSocket endpoints
and send/receive messages.

Usage:
    # Test echo service
    python3 websocket_client.py --endpoint /ws

    # Test chat service
    python3 websocket_client.py --endpoint /chat --mode json

    # Interactive mode
    python3 websocket_client.py --interactive
"""

import asyncio
import json
import sys
import argparse
import logging
from typing import Optional

try:
    import websockets
    from websockets.client import WebSocketClientProtocol
except ImportError:
    print("Error: websockets library not installed")
    print("Install it with: pip install websockets")
    sys.exit(1)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("WebSocketClient")


class WebSocketClient:
    """WebSocket client for testing Zephyr WebSocket endpoints."""

    def __init__(
        self,
        url: str = "ws://localhost:8000/ws",
        mode: str = "text",
    ):
        """Initialize WebSocket client.

        Args:
            url: WebSocket URL to connect to
            mode: Message mode - "text" or "json"
        """
        self.url = url
        self.mode = mode
        self.websocket: Optional[WebSocketClientProtocol] = None
        self.running = False

    async def connect(self) -> None:
        """Connect to WebSocket server."""
        try:
            logger.info(f"Connecting to {self.url}...")
            self.websocket = await websockets.connect(self.url)
            logger.info("Connected successfully!")
            self.running = True
        except Exception as exc:
            logger.error(f"Failed to connect: {exc}")
            raise

    async def disconnect(self) -> None:
        """Disconnect from WebSocket server."""
        if self.websocket:
            await self.websocket.close()
            self.running = False
            logger.info("Disconnected")

    async def send_message(self, message: str) -> None:
        """Send message to server.

        Args:
            message: Message to send (text or JSON)
        """
        if not self.websocket:
            logger.error("Not connected")
            return

        try:
            if self.mode == "json":
                # Parse as JSON if possible
                try:
                    data = json.loads(message)
                except json.JSONDecodeError:
                    data = {"message": message}
                await self.websocket.send(json.dumps(data))
                logger.info(f"Sent JSON: {data}")
            else:
                # Send as text
                await self.websocket.send(message)
                logger.info(f"Sent: {message}")
        except Exception as exc:
            logger.error(f"Failed to send message: {exc}")

    async def receive_message(self) -> Optional[str]:
        """Receive message from server.

        Returns:
            Received message or None if disconnected
        """
        if not self.websocket:
            return None

        try:
            message = await self.websocket.recv()
            if self.mode == "json":
                try:
                    data = json.loads(message)
                    logger.info(f"Received JSON: {json.dumps(data, indent=2)}")
                except json.JSONDecodeError:
                    logger.info(f"Received: {message}")
            else:
                logger.info(f"Received: {message}")
            return message
        except websockets.exceptions.ConnectionClosed:
            logger.info("Connection closed by server")
            self.running = False
            return None
        except Exception as exc:
            logger.error(f"Failed to receive message: {exc}")
            return None

    async def echo_test(self, message: str = "Hello, Zephyr!") -> None:
        """Test echo endpoint.

        Args:
            message: Message to echo
        """
        await self.connect()
        try:
            await self.send_message(message)
            response = await self.receive_message()
            if response:
                logger.info(f"Echo test passed!")
        finally:
            await self.disconnect()

    async def interactive_mode(self) -> None:
        """Interactive mode - send/receive messages."""
        await self.connect()

        logger.info("Interactive mode started. Type messages to send (quit to exit)")
        loop = asyncio.get_event_loop()

        def read_input_blocking():
            """Read input from stdin in a non-blocking way."""
            data = input(">:")
            logger.info("Read input: %s", data)
            return data

        async def read_input():
            """Read input from stdin in a non-blocking way."""
            input_text = await loop.run_in_executor(None, read_input_blocking)
            input_text = input_text.strip()
            print(f">:{input_text}")
            logger.info("Input text: %s", input_text)
            return input_text

        async def receive_loop():
            """Receive messages in background."""
            while self.running:
                await self.receive_message()

        # Start receive loop
        receive_task = asyncio.create_task(receive_loop())

        try:
            while self.running:
                try:
                    message = await asyncio.wait_for(read_input(), timeout=1.0)
                    logger.info("Received message: %s", message)
                    if message.lower() == "quit":
                        break
                    if message.strip():
                        logger.info("Sending message: %s", message)
                        await self.send_message(message)
                except asyncio.TimeoutError:
                    continue
        except (KeyboardInterrupt, EOFError):
            logger.info("\nExiting...")
        finally:
            receive_task.cancel()
            await self.disconnect()

    async def multiple_messages(self, messages: list[str]) -> None:
        """Send multiple messages and receive responses.

        Args:
            messages: List of messages to send
        """
        await self.connect()

        try:
            for message in messages:
                await self.send_message(message)
                response = await self.receive_message()
                await asyncio.sleep(0.5)  # Small delay between messages
        finally:
            await self.disconnect()


async def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="WebSocket client for testing Zephyr endpoints")
    parser.add_argument(
        "--url",
        default="ws://localhost:8000/ws",
        help="WebSocket URL (default: ws://localhost:8000/ws)",
    )
    parser.add_argument(
        "--endpoint",
        default="/ws",
        help="Endpoint path (default: /ws)",
    )
    parser.add_argument(
        "--host",
        default="localhost",
        help="Server host (default: localhost)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Server port (default: 8000)",
    )
    parser.add_argument(
        "--mode",
        choices=["text", "json"],
        default="text",
        help="Message mode (default: text)",
    )
    parser.add_argument(
        "--message",
        help="Single message to send (default: interactive mode)",
    )
    parser.add_argument(
        "--messages",
        nargs="+",
        help="Multiple messages to send",
    )
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Start in interactive mode",
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Run echo test",
    )

    args = parser.parse_args()

    # Build WebSocket URL
    if args.url == parser.get_default("url"):
        # Use host/port/endpoint if URL not explicitly provided
        ws_url = f"ws://{args.host}:{args.port}{args.endpoint}"
    else:
        ws_url = args.url

    logger.info(f"WebSocket Client")
    logger.info(f"URL: {ws_url}")
    logger.info(f"Mode: {args.mode}")

    client = WebSocketClient(url=ws_url, mode=args.mode)

    try:
        if args.test:
            # Echo test
            logger.info("Running echo test...")
            await client.echo_test("Test message from client")
        elif args.messages:
            # Multiple messages
            logger.info(f"Sending {len(args.messages)} messages...")
            await client.multiple_messages(args.messages)
        elif args.message:
            # Single message
            await client.connect()
            try:
                await client.send_message(args.message)
                response = await client.receive_message()
            finally:
                await client.disconnect()
        else:
            # Interactive mode (default)
            await client.interactive_mode()
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    except Exception as exc:
        logger.error(f"Error: {exc}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
