from __future__ import annotations

"""
Custom exceptions for the Saamfi SDK.

This module defines exceptions that can be raised by the SDK
during interaction with the Saamfi service.
"""


class SaamfiException(Exception):
    """
    Base exception for all Saamfi SDK exceptions.

    Parameters
    ----------
    message:
        Optional custom error message. When omitted, a class-specific default
        message is used.
    details:
        Optional dictionary with extra information to aid debugging or error
        handling.
    """

    default_message = "An unexpected Saamfi SDK error occurred."

    def __init__(self, message: str | None = None, *, details: dict | None = None):
        if message is None:
            message = self.default_message
        super().__init__(message)
        self.details = details or {}

    def __repr__(self) -> str:  # pragma: no cover - debugging helper
        return f"{self.__class__.__name__}({self.args[0]!r}, details={self.details!r})"


class SaamfiAuthenticationError(SaamfiException):
    """Exception raised when authentication with Saamfi fails."""

    default_message = "Authentication with Saamfi failed due to invalid credentials."


class SaamfiTokenValidationError(SaamfiException):
    """Exception raised when JWT token validation fails."""

    default_message = "The provided Saamfi token is invalid or has expired."


class SaamfiConnectionError(SaamfiException):
    """Exception raised when there are connection issues with the Saamfi server."""

    default_message = "Unable to connect or communicate with the Saamfi service."


class SaamfiUnauthorizedError(SaamfiException):
    """Exception raised when the caller lacks permissions for a Saamfi operation."""

    default_message = "Operation not permitted: insufficient Saamfi permissions."


class SaamfiNotFoundError(SaamfiException):
    """Exception raised when a requested Saamfi resource cannot be found."""

    default_message = "The requested Saamfi resource could not be found."


class SaamfiInvalidSystemError(SaamfiException):
    """Exception raised when the system_id in the token doesn't match the expected one."""

    default_message = "The Saamfi token belongs to a different system than expected."
