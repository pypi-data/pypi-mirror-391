"""Django-like settings manager."""

from .base import BaseSettings


class Settings:
    """
    Django-like settings manager.

    Provides lazy loading and module-based configuration.
    """

    _instance: BaseSettings | None = None
    _configured: bool = False

    def configure(
        self,
        settings_module: str | None = None,
        settings_class: type[BaseSettings] | None = None,
    ) -> None:
        """
        Configure settings (Django-style).

        Args:
            settings_module: Python module path (e.g., "myproject.settings")
            settings_class: Settings class to use directly

        Example:
            # Load from module
            settings.configure(settings_module="myproject.settings")

            # Or use class directly
            settings.configure(settings_class=MySettings)
        """
        if self._configured:
            return

        if settings_module:
            # Import user's settings module
            import importlib

            module = importlib.import_module(settings_module)
            settings_class = getattr(module, "Settings", BaseSettings)
            self._instance = settings_class()
        elif settings_class:
            self._instance = settings_class()
        else:
            # Use default BaseSettings
            self._instance = BaseSettings()

        self._configured = True

    def get(self, name: str, default: object = None) -> object:
        """
        Get setting value.

        Args:
            name: Setting name (e.g., "DEBUG")
            default: Default value if setting not found

        Returns:
            Setting value or default
        """
        if not self._configured:
            self.configure()

        if self._instance is None:
            return default

        return getattr(self._instance, name, default)

    def __getattr__(self, name: str) -> object:
        """Allow settings.DEBUG syntax."""
        return self.get(name)

    def to_dict(self) -> dict[str, object]:
        """Convert settings to dictionary."""
        if not self._configured:
            self.configure()

        if self._instance is None:
            return {}

        return self._instance.model_dump()

    def reload(self) -> None:
        """Reload settings (useful for testing)."""
        self._configured = False
        self._instance = None


class LazySettings:
    """
    Lazy settings loader that mimics Django's LazySettings.

    This provides a proxy to the actual settings that loads them
    only when first accessed.
    """

    def __init__(self, settings: Settings | None = None):
        self._settings = settings or Settings()

    def __getattr__(self, name: str) -> object:
        """Get setting value by name."""
        return getattr(self._settings, name)

    def __setattr__(self, name: str, value: object) -> None:
        """Set setting value by name."""
        if name.startswith("_"):
            super().__setattr__(name, value)
        else:
            setattr(self._settings, name, value)

    def configure(self, **kwargs: object) -> None:
        """Configure the underlying settings."""
        self._settings.configure(**kwargs)

    def get(self, name: str, default: object = None) -> object:
        """Get setting value with default."""
        return self._settings.get(name, default)

    def set(self, name: str, value: object) -> None:
        """Set setting value."""
        setattr(self._settings, name, value)

    def update(self, **kwargs: object) -> None:
        """Update multiple settings."""
        for name, value in kwargs.items():
            self.set(name, value)

    def to_dict(self) -> dict[str, object]:
        """Convert settings to dictionary."""
        return self._settings.to_dict() if hasattr(self._settings, "to_dict") else {}

    def reload(self) -> None:
        """Reload settings (useful for testing)."""
        self._settings.reload()


# Global settings instance
settings = LazySettings()
