"""
Main client entry point for the Saamfi SDK.

This module now composes several service classes to keep responsibilities
focused and the public API unchanged.
"""

from __future__ import annotations

import logging
import os
from typing import Any, Dict, List, Optional

import requests
from cryptography.hazmat.primitives.asymmetric import rsa
from dotenv import load_dotenv

from .models import LoginResponse, UserDetailToken, UserInfo
from .services import AuthenticationService, InstitutionService, TokenService, UserService

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger(__name__)


class SaamfiClient:
    """
    Main client for interacting with the Saamfi platform.

    The class delegates most of the work to specialized service classes while
    preserving the public interface exposed by previous versions.
    """

    ROLE_CLAIM = TokenService.ROLE_CLAIM
    SYSTEM_CLAIM = TokenService.SYSTEM_CLAIM
    USERNAME_CLAIM = TokenService.USERNAME_CLAIM
    ID_CLAIM = TokenService.ID_CLAIM

    def __init__(self, saamfi_url: Optional[str] = None, system_id: Optional[int] = None):
        """
        Create a Saamfi client instance.

        Args:
            saamfi_url: Base URL of the Saamfi server. Falls back to the
                `SAAMFI_URL` environment variable.
            system_id: Tenant/system identifier. Falls back to the
                `SAAMFI_SYSTEM_ID` environment variable.

        Raises:
            ValueError: Missing or invalid configuration values.
        """
        resolved_url = saamfi_url or os.getenv("SAAMFI_URL")
        if not resolved_url:
            raise ValueError(
                "saamfi_url must be provided either as parameter or through "
                "the SAAMFI_URL environment variable"
            )

        if system_id is None:
            system_id_raw = os.getenv("SAAMFI_SYSTEM_ID")
            if system_id_raw is None:
                raise ValueError(
                    "system_id must be provided either as parameter or through "
                    "the SAAMFI_SYSTEM_ID environment variable"
                )
            try:
                system_id = int(system_id_raw)
            except ValueError as exc:
                raise ValueError(
                    "SAAMFI_SYSTEM_ID environment variable must be a valid integer, "
                    f"got: {system_id_raw}"
                ) from exc

        self._saamfi_url = resolved_url.rstrip("/")
        self._system_id = system_id
        self._session = requests.Session()

        self._token_service = TokenService(self._saamfi_url, self._session)
        self._auth_service = AuthenticationService(
            self._saamfi_url,
            self._session,
            self._system_id,
            self._token_service,
        )
        self._user_service = UserService(self._saamfi_url, self._session)
        self._institution_service = InstitutionService(self._saamfi_url, self._session)

        self._public_key: Optional[bytes] = None

        try:
            self._public_key = self._token_service.fetch_public_key_bytes()
        except Exception as exc:  # pragma: no cover - initialization is best-effort
            logger.warning("Error obtaining public key during initialization: %s", exc)

    def _get_public_key(self) -> bytes:
        """
        Retrieve the cached raw public key (DER encoded) or fetch it from Saamfi.

        Returns:
            bytes: DER-encoded public key.

        Raises:
            SaamfiConnectionError: If the Saamfi service cannot be reached.
        """
        key_bytes = self._token_service.fetch_public_key_bytes()
        self._public_key = key_bytes
        return key_bytes

    def get_public_key(self) -> rsa.RSAPublicKey:
        """
        Return the RSA public key used to validate Saamfi JWT tokens.

        Raises:
            SaamfiConnectionError: If the public key cannot be fetched or parsed.
        """
        public_key = self._token_service.get_rsa_public_key()
        self._public_key = self._token_service.public_key_bytes
        return public_key

    @property
    def saamfi_url(self) -> str:
        """Base URL of the Saamfi server."""
        return self._saamfi_url

    @property
    def system_id(self) -> int:
        """Current tenant/system identifier."""
        return self._system_id

    def login(self, username: str, password: str) -> Optional[LoginResponse]:
        """
        Authenticate a user and return the login payload if successful.

        Returns:
            LoginResponse or None.

        Raises:
            SaamfiConnectionError: Request errors while contacting Saamfi.
        """
        return self._auth_service.login(username, password)

    def get_roles_from_jwt(self, auth_token: str) -> List[str]:
        """
        Extract roles from a JWT token.

        Returns:
            List of role strings. Returns an empty list on any error.
        """
        return self._auth_service.get_roles_from_jwt(auth_token)

    def validate_token(self, auth_token: str) -> UserDetailToken:
        """
        Validate a JWT token and return the associated user details.

        Raises:
            SaamfiTokenValidationError: Invalid or expired tokens.
        """
        return self._auth_service.validate_token(auth_token)

    def get_user_info(self, auth_token: str, user_id: int) -> Optional[UserInfo]:
        """
        Retrieve complete user information by ID.

        Returns:
            UserInfo or None if the request fails or the user does not exist.
        """
        return self._user_service.get_user_info(auth_token, user_id)

    def get_user_by_username(self, auth_token: str, username: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a user by username.

        Raises:
            SaamfiAuthenticationError: Invalid credentials (HTTP 401).
            SaamfiConnectionError: Other request errors.
        """
        return self._user_service.get_user_by_username(auth_token, username)

    def get_users_by_document(self, auth_token: str, user_documents: List[str]) -> List[Dict[str, Any]]:
        """
        Retrieve users by document numbers.

        Raises:
            SaamfiAuthenticationError: Invalid credentials (HTTP 401).
            SaamfiConnectionError: Other request errors.
        """
        return self._user_service.get_users_by_document(auth_token, user_documents)

    def get_users_from_list(self, auth_token: str, user_ids: List[int]) -> Optional[str]:
        """Retrieve multiple users by their IDs."""
        return self._user_service.get_users_from_list(auth_token, user_ids)

    def get_users_by_param_and_value(self, auth_token: str, param: str, value: str) -> Optional[str]:
        """Retrieve users using the generic param/value endpoint."""
        return self._user_service.get_users_by_param_and_value(auth_token, param, value)

    def get_institution_by_nit(self, auth_token: str, nit: str) -> Optional[str]:
        """Retrieve institution metadata by NIT."""
        return self._institution_service.get_institution_by_nit(auth_token, nit)

    def get_institutions_by_ids(self, auth_token: str, institution_ids: List[int]) -> Optional[str]:
        """Retrieve multiple institutions by ID list."""
        return self._institution_service.get_institutions_by_ids(auth_token, institution_ids)

    def __repr__(self) -> str:
        """Object representation for debugging."""
        return f"SaamfiClient(saamfi_url='{self._saamfi_url}', system_id={self._system_id})"
