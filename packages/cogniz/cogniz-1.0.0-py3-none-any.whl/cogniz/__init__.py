"""
Cogniz Memory Platform - Python SDK

Build intelligent AI applications with persistent memory.

Quick Start:
    >>> from cogniz import Client
    >>> client = Client(api_key="mp_...")
    >>> client.store("User loves Python programming", user_id="alice")
    >>> results = client.search("programming", user_id="alice")

Homepage: https://cogniz.online
Documentation: https://docs.cogniz.online
GitHub: https://github.com/cogniz-ai/cogniz-python
"""

__version__ = "1.0.0"
__author__ = "Cogniz Team"
__email__ = "support@cogniz.online"
__license__ = "MIT"

from cogniz.client import Client, AsyncClient
from cogniz.config import Config
from cogniz.errors import (
    CognizError,
    AuthenticationError,
    NotFoundError,
    RateLimitError,
    ValidationError,
    ServerError,
    NetworkError
)

__all__ = [
    # Main API
    "Client",
    "AsyncClient",
    "Config",

    # Errors
    "CognizError",
    "AuthenticationError",
    "NotFoundError",
    "RateLimitError",
    "ValidationError",
    "ServerError",
    "NetworkError",

    # Metadata
    "__version__",
]
