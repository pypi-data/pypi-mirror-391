"""
Nexus AI API - Python Client Library
A comprehensive Python wrapper for the Nexus AI API
"""

from .client import NexusAI
from .exceptions import (
    NexusAPIError,
    AuthenticationError,
    RateLimitError,
    BadRequestError,
    ServerError,
    NotFoundError
)

__version__ = "5.0.3"
__author__ = "Nexus API"
__all__ = [
    "NexusAI",
    "NexusAPIError",
    "AuthenticationError",
    "RateLimitError",
    "BadRequestError",
    "ServerError",
    "NotFoundError"
]
