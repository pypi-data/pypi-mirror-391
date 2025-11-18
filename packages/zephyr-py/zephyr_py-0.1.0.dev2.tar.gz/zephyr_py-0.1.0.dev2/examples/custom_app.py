"""App with custom settings (Django-style)."""

from zephyr import Zephyr
from zephyr.conf import settings
from zephyr.core.zserver.server import Server
from zephyr.core.zserver.config import ServerConfig

# Configure to use custom settings
settings.configure(settings_module="examples.settings")

# Create app - reads from examples/settings.py
app = Zephyr()


@app.get("/")
async def hello():
    return {
        "message": "Custom settings!",
        "debug": settings.get("DEBUG"),
        "cors_origins": settings.get("CORS_ORIGINS"),
    }


@app.get("/metrics")
async def metrics():
    # Access metrics from middleware
    from zephyr.app.middleware.metrics import MetricsMiddleware

    # This would need to be implemented to access middleware instance
    return {"message": "Metrics endpoint"}


if __name__ == "__main__":
    # Use Zephyr's own server (zserver)
    server_config = ServerConfig(app, host="0.0.0.0", port=8000)
    server = Server(server_config)
    server.run()
