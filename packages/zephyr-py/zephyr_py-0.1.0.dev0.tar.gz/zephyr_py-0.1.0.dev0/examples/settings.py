"""Custom settings file (Django-style)."""

from zephyr.conf import BaseSettings


class Settings(BaseSettings):
    """My custom settings."""

    DEBUG = True
    ENABLE_CORS = True
    CORS_ORIGINS = ["http://localhost:3000"]
    RATE_LIMIT_REQUESTS = 100
    ENABLE_METRICS = True
    ENABLE_TRACING = True
