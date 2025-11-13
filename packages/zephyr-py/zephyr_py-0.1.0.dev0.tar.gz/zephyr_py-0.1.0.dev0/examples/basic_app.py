"""Basic Zephyr app using default settings."""

from zephyr import Zephyr
from zephyr.core.zserver.server import Server
from zephyr.core.zserver.config import ServerConfig

# Uses default settings + .env
app = Zephyr()


@app.get("/")
async def hello():
    return {"message": "Hello from Zephyr!"}


@app.get("/health")
async def health():
    return {"status": "healthy"}


if __name__ == "__main__":
    # Use Zephyr's own server (zserver)
    server_config = ServerConfig(app, host="0.0.0.0", port=8000)
    server = Server(server_config)
    server.run()
