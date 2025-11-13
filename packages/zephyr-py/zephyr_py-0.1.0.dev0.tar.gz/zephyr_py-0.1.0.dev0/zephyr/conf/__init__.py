"""
Zephyr Configuration Module

Usage:
    # In your project, create settings.py:
    from zephyr.conf import BaseSettings

    class Settings(BaseSettings):
        DEBUG = True
        ENABLE_CORS = True

    # In your app.py:
    from zephyr import Zephyr
    from zephyr.conf import settings

    settings.configure(settings_module="myproject.settings")
    app = Zephyr()
"""

from .base import BaseSettings
from .manager import Settings, LazySettings, settings

__all__ = ["BaseSettings", "Settings", "LazySettings", "settings"]
