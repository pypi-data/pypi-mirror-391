"""Synq Python SDK - Multi-Agent AI Interaction System.

This package provides a Python client for interacting with the Synq API,
enabling easy creation and management of AI agent interactions.
"""

from .client import SynqClient
from .models import (
    Agent,
    Sandbox,
    Message,
    OutputFormat,
    OutputFormatType,
)
from .exceptions import (
    SynqError,
    SynqAPIError,
    SynqConnectionError,
    SynqValidationError,
)

__version__ = "0.1.0"
__all__ = [
    "SynqClient",
    "Agent",
    "Sandbox",
    "Message",
    "OutputFormat",
    "OutputFormatType",
    "SynqError",
    "SynqAPIError",
    "SynqConnectionError",
    "SynqValidationError",
]

