"""SQLAlchemy declarative base for plugin models.

This module provides the declarative base class that plugins use to define
their database models. The actual Base instance is registered by the backend
during startup to ensure Alembic can discover all models.
"""

import logging
from typing import Any

from sqlalchemy.orm import DeclarativeBase

logger = logging.getLogger(__name__)

# Global Base reference (injected by backend)
_backend_base: type[DeclarativeBase] | None = None


def register_base(base_class: type[DeclarativeBase]) -> None:
    """
    Register the backend's declarative base.

    This function is called by the backend during application startup
    to inject its DeclarativeBase into the SDK. This ensures plugin models
    and backend models share the same base, allowing Alembic to discover
    all models during migration generation.

    Args:
        base_class: The backend's DeclarativeBase class

    Note:
        This is an internal function used by the backend infrastructure.
        Plugin developers should not call this function.
    """
    global _backend_base
    _backend_base = base_class
    logger.debug("SQLAlchemy Base registered in SDK")


def get_base() -> type[DeclarativeBase]:
    """
    Get the registered declarative base.

    Returns:
        The DeclarativeBase class registered by the backend

    Raises:
        RuntimeError: If base has not been registered by backend

    Note:
        Plugin developers should use the `Base` class directly instead
        of calling this function.
    """
    if _backend_base is None:
        raise RuntimeError(
            "SQLAlchemy Base not registered. "
            "This indicates the backend did not properly initialize the SDK bridge. "
            "Contact your administrator or check backend startup logs."
        )
    return _backend_base


class _BaseProxy:
    """
    Proxy class that forwards attribute access to the registered Base.

    This allows plugins to inherit from `Base` directly while the actual
    Base instance is injected at runtime by the backend.
    """

    def __getattribute__(self, name: str) -> Any:
        # Don't proxy special methods used by Python internals
        if name.startswith("_BaseProxy"):
            return object.__getattribute__(self, name)

        # Get the registered base and forward attribute access
        base = get_base()
        return getattr(base, name)

    def __class_getitem__(cls, item: Any) -> Any:
        """Support generic type hints."""
        base = get_base()
        return base[item]  # type: ignore


# Export Base as the proxy
# Plugins will write: class MyModel(Base):
# At runtime, this resolves to the backend's actual Base class
Base = get_base  # type: ignore


# NOTE: The above approach using get_base() won't work for inheritance.
# We need a different strategy. Let's use a module-level replacement pattern instead.


class Base(DeclarativeBase):
    """
    Declarative base class for plugin models.

    Plugin models should inherit from this class to be discoverable
    by SQLAlchemy and Alembic migrations.

    Example:
        ```python
        from huitzo_sdk.orm import Base
        from sqlalchemy import String
        from sqlalchemy.orm import Mapped, mapped_column
        from uuid import UUID, uuid4

        class MyPluginModel(Base):
            __tablename__ = "my_plugin_table"

            id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
            name: Mapped[str] = mapped_column(String(255))
        ```

    Important:
        - This Base is shared with the backend's Base for Alembic discovery
        - All plugin models are included in the same migration system
        - Use appropriate table naming to avoid conflicts (prefix with plugin name)
        - Follow backend naming conventions for consistency

    Table Naming Convention:
        - Use snake_case
        - Prefix with plugin namespace: `{plugin}_tablename`
        - Examples: `duck_conversations`, `finance_watchlist_items`
    """

    pass
