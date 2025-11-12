"""
dgsender - Unified sender package for email, telegram, slack and zabbix
"""

import importlib
from typing import Any

__version__ = "1.0.0"

# Lazy import function
def _lazy_import(name: str) -> Any:
    """Lazy import to avoid dependency issues when only specific extras are installed"""
    if name == "Mailer":
        from .mailer import Mailer
        return Mailer
    elif name == "AsyncMailer":
        from .mailer import AsyncMailer
        return AsyncMailer
    elif name == "Message":
        from .mailer import Message
        return Message
    elif name == "Manager":
        from .mailer import Manager
        return Manager
    elif name == "EmailSender":
        from .email_sender import EmailSender
        return EmailSender
    elif name == "MailerContinius":
        from .email_sender import MailerContinius
        return MailerContinius
    elif name == "TelegramSender":
        from .telegram_sender import TelegramSender
        return TelegramSender
    elif name == "SlackSender":
        from .slack_sender import SlackSender
        return SlackSender
    elif name == "ZabbixSender":
        from .zabbix_sender import ZabbixSender
        return ZabbixSender
    elif name == "AsyncEmailSender":
        from .async_email_sender import AsyncEmailSender
        return AsyncEmailSender
    elif name == "AsyncTelegramSender":
        from .async_telegram_sender import AsyncTelegramSender
        return AsyncTelegramSender
    elif name == "AsyncSlackSender":
        from .async_slack_sender import AsyncSlackSender
        return AsyncSlackSender
    elif name == "CompositeSender":
        from .composite_sender import CompositeSender
        return CompositeSender
    else:
        raise ImportError(f"Cannot import {name}")

# Lazy loader class
class _LazyLoader:
    def __getattr__(self, name: str) -> Any:
        return _lazy_import(name)

# Create lazy loader instance
_lazy_loader = _LazyLoader()

# Define __all__ for public API
__all__ = [
    'Mailer',
    'AsyncMailer',
    'Message',
    'Manager',
    'EmailSender',
    'MailerContinius',
    'TelegramSender',
    'SlackSender',
    'ZabbixSender',
    'AsyncEmailSender',
    'AsyncTelegramSender',
    'AsyncSlackSender',
    'CompositeSender',
    'DGSenderError',
    'EmailSendError',
    'TelegramSendError',
    'SlackSendError',
    'ZabbixSendError'
]

# Import exceptions directly (they have no dependencies)
from .exceptions import (
    DGSenderError, EmailSendError, TelegramSendError,
    SlackSendError, ZabbixSendError
)

# Override module's __getattr__ for lazy imports
def __getattr__(name: str) -> Any:
    if name in __all__:
        return _lazy_import(name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
