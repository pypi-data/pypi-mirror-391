"""
Huitzo SDK - Developer SDK for Huitzo WebCLI Platform Tools.

This package provides a Python SDK for:

1. **HTTP Clients** (External API Access):
   - CRON Scheduling Service: Schedule and manage recurring command executions
   - Email Service: Send emails and manage templates
   - LLM Completions Service: Generate text completions using various LLM providers
   - Static Site Hosting Service: Deploy temporary static sites from .zip archives

2. **Plugin Development** (Command Implementation):
   - Command Protocol: Interface for creating executable commands
   - Database Access: ORM and session management
   - Shared Enums: UserRole, ConfigScope, ExecutionStatus
   - Model Base: SQLAlchemy declarative base for plugin models

HTTP Client Usage:
    ```python
    from huitzo_sdk import HuitzoTools

    async with HuitzoTools(api_token="your_token") as sdk:
        # Schedule a CRON job
        job = await sdk.cron.schedule(
            name="daily_report",
            command="finance.report.generate",
            schedule="0 9 * * *",
            timezone="UTC"
        )

        # Send an email
        await sdk.email.send(
            recipient_user_id="user-uuid",
            subject="Report Ready",
            html_body="<p>Your report is ready!</p>"
        )
    ```

Plugin Development Usage:
    ```python
    from huitzo_sdk import CommandProtocol, CommandContext, CommandResult
    from huitzo_sdk.database import get_async_session_context
    from huitzo_sdk.orm import Base

    class MyCommand:
        @property
        def name(self) -> str:
            return "mycommand"

        async def execute(
            self, args: dict, context: CommandContext
        ) -> CommandResult:
            async with get_async_session_context() as db:
                # Database operations...
                pass
            return CommandResult(exit_code=0, stdout="Success!\\n")
    ```

Main Classes:
    HTTP Clients:
    - HuitzoTools: Main SDK client with async context manager support
    - CronClient: CRON Scheduling Service client
    - EmailClient: Email Service client
    - LLMClient: LLM Completions Service client
    - SitesClient: Static Site Hosting Service client

    Plugin Development:
    - CommandProtocol: Protocol for command implementations
    - CommandContext: Execution context passed to commands
    - CommandResult: Result returned by command execution
    - Base: SQLAlchemy declarative base for plugin models

Exceptions:
    - HuitzoAPIError: Base exception for all API errors
    - AuthenticationError: 401/403 authentication failures
    - NotFoundError: 404 resource not found
    - RateLimitError: 429 rate limit exceeded
    - ValidationError: 400 validation errors
    - QuotaExceededError: 403 quota limits exceeded
"""

__version__ = "2.0.0"

# HTTP Clients (for external API consumers)
from .client import HuitzoTools
from .cron import CronClient
from .email import EmailClient
from .llm import LLMClient
from .sites import SitesClient

# Plugin Development Interfaces
from .protocols.command import CommandContext, CommandProtocol, CommandResult
from .enums import ConfigScope, ExecutionStatus, UserRole
from .orm import Base
from .database import get_async_session_context, register_session_factory

# Exceptions
from .exceptions import (
    AuthenticationError,
    HuitzoAPIError,
    NotFoundError,
    QuotaExceededError,
    RateLimitError,
    ValidationError,
)

__all__ = [
    # HTTP Clients
    "HuitzoTools",
    "CronClient",
    "EmailClient",
    "LLMClient",
    "SitesClient",
    # Plugin Development - Protocols
    "CommandProtocol",
    "CommandContext",
    "CommandResult",
    # Plugin Development - Enums
    "UserRole",
    "ConfigScope",
    "ExecutionStatus",
    # Plugin Development - ORM
    "Base",
    # Plugin Development - Database
    "get_async_session_context",
    "register_session_factory",
    # Exceptions
    "HuitzoAPIError",
    "AuthenticationError",
    "NotFoundError",
    "QuotaExceededError",
    "RateLimitError",
    "ValidationError",
    # Version
    "__version__",
]
