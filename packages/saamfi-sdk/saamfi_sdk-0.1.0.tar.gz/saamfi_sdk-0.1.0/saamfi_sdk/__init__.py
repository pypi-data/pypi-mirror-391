"""
Saamfi SDK for Python

Python SDK to connect to SAAMFI services - Authentication and Authorization.

This SDK is equivalent to saamfi-security (Java SDK) and provides the same
functionality for systems that require integration with the Saamfi service.

Basic usage:
    >>> from saamfi_sdk import SaamfiClient
    >>> client = SaamfiClient("https://saamfi.example.com", system_id=123)
    >>> # Client is ready for authentication and token validation

Equivalent to: co.edu.icesi.dev.saamfi.saamfisecurity (Java package)
"""

__version__ = "0.1.0"

from .client import SaamfiClient
from .exceptions import (
    SaamfiAuthenticationError,
    SaamfiConnectionError,
    SaamfiException,
    SaamfiInvalidSystemError,
    SaamfiNotFoundError,
    SaamfiTokenValidationError,
    SaamfiUnauthorizedError,
)
from .models import LoginBody, LoginResponse, UserDetailToken, UserInfo

__all__ = [
    # Main client
    "SaamfiClient",
    # Models
    "LoginBody",
    "LoginResponse",
    "UserInfo",
    "UserDetailToken",
    # Exceptions
    "SaamfiException",
    "SaamfiAuthenticationError",
    "SaamfiTokenValidationError",
    "SaamfiConnectionError",
    "SaamfiInvalidSystemError",
    "SaamfiUnauthorizedError",
    "SaamfiNotFoundError",
    # Metadata
    "__version__",
]
