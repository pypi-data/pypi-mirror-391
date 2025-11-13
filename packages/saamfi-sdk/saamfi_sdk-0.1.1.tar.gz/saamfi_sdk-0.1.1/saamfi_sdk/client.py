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
from .services import (
    AuthenticationService,
    InstitutionService,
    SystemService,
    TokenService,
    UserService,
)

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

    def __init__(
        self,
        saamfi_url: Optional[str] = None,
        system_id: Optional[int] = None,
        client_id: Optional[int] = None,
        client_secret: Optional[str] = None,
        tenant_id: Optional[int] = None,
    ):
        """
        Create a Saamfi client instance.

        Args:
            saamfi_url: Base URL of the Saamfi server. Falls back to the
                `SAAMFI_BASE_URL`/`SAAMFI_URL` environment variables.
            system_id: Tenant/system identifier. Falls back to the
                `SAAMFI_SYS_ID`/`SAAMFI_SYSTEM_ID` environment variables.
            client_id: OAuth-style client identifier. Falls back to the
                `SAAMFI_CLIENT_ID` environment variable.
            client_secret: Client secret used for confidential flows.
                Falls back to `SAAMFI_CLIENT_SECRET`.
            tenant_id: Institution/tenant identifier for institution-specific
                requests. Falls back to `SAAMFI_TENANT_ID`/`SAAMFI_INST_ID`.

        Raises:
            ValueError: Missing or invalid configuration values.
        """
        resolved_url = saamfi_url or self._get_first_env("SAAMFI_BASE_URL", "SAAMFI_URL")
        if not resolved_url:
            raise ValueError(
                "saamfi_url must be provided either as parameter or through "
                "the SAAMFI_BASE_URL/SAAMFI_URL environment variables"
            )

        if system_id is None:
            system_id_raw = self._get_first_env("SAAMFI_SYS_ID", "SAAMFI_SYSTEM_ID")
            if system_id_raw is None:
                raise ValueError(
                    "system_id must be provided either as parameter or through "
                    "the SAAMFI_SYS_ID/SAAMFI_SYSTEM_ID environment variables"
                )
            try:
                system_id = int(system_id_raw)
            except ValueError as exc:
                raise ValueError(
                    "SAAMFI_SYS_ID/SAAMFI_SYSTEM_ID environment variables must contain a valid "
                    f"integer, got: {system_id_raw}"
                ) from exc

        if client_id is None:
            client_id_raw = self._get_first_env("SAAMFI_CLIENT_ID")
            if client_id_raw is not None:
                try:
                    client_id = int(client_id_raw)
                except ValueError as exc:
                    raise ValueError(
                        "SAAMFI_CLIENT_ID environment variable must be a valid integer, "
                        f"got: {client_id_raw}"
                    ) from exc

        if tenant_id is None:
            tenant_id_raw = self._get_first_env("SAAMFI_TENANT_ID", "SAAMFI_INST_ID")
            if tenant_id_raw is not None:
                try:
                    tenant_id = int(tenant_id_raw)
                except ValueError as exc:
                    raise ValueError(
                        "SAAMFI_TENANT_ID/SAAMFI_INST_ID environment variables must contain a "
                        f"valid integer, got: {tenant_id_raw}"
                ) from exc

        self._saamfi_url = resolved_url.rstrip("/")
        self._system_id = system_id
        self._client_id = client_id
        self._client_secret = client_secret or self._get_first_env("SAAMFI_CLIENT_SECRET")
        self._tenant_id = tenant_id
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
        self._system_service = SystemService(self._saamfi_url, self._session)

        self._public_key: Optional[bytes] = None

        try:
            self._public_key = self._token_service.fetch_public_key_bytes()
        except Exception as exc:  # pragma: no cover - initialization is best-effort
            logger.warning("Error obtaining public key during initialization: %s", exc)

    @staticmethod
    def _get_first_env(*names: str) -> Optional[str]:
        """Return the first non-empty environment variable among the provided names."""
        for env_name in names:
            value = os.getenv(env_name)
            if value:
                return value
        return None

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

    @property
    def client_id(self) -> Optional[int]:
        """Client identifier configured for this SDK instance."""
        return self._client_id

    @property
    def client_secret(self) -> Optional[str]:
        """Client secret configured for this SDK instance."""
        return self._client_secret

    @property
    def tenant_id(self) -> Optional[int]:
        """Tenant/Institution identifier configured for this SDK instance."""
        return self._tenant_id

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

    def list_public_institutions(
        self, *, name: Optional[str] = None, nit: Optional[str] = None
    ) -> Optional[Any]:
        """Retrieve the list of public institutions exposed by Saamfi."""
        return self._institution_service.list_public_institutions(name=name, nit=nit)

    def get_institution_params(
        self, auth_token: str, institution_id: Optional[int] = None
    ) -> Optional[Dict[str, Any]]:
        """Retrieve configuration parameters for an institution."""
        target_institution = institution_id or self._tenant_id
        if target_institution is None:
            raise ValueError(
                "institution_id must be provided either as parameter or configured via "
                "SAAMFI_TENANT_ID/SAAMFI_INST_ID"
            )
        return self._institution_service.get_institution_params(auth_token, target_institution)

    def list_public_systems(self) -> Optional[List[Dict[str, Any]]]:
        """Retrieve the list of systems available in Saamfi."""
        return self._system_service.list_public_systems()

    def get_system_roles(
        self, auth_token: str, system_id: Optional[int] = None
    ) -> Optional[List[Dict[str, Any]]]:
        """Retrieve roles configured in a system."""
        target_system = system_id or self._system_id
        return self._system_service.get_system_roles(auth_token, target_system)

    def __repr__(self) -> str:
        """Object representation for debugging."""
        return (
            "SaamfiClient("
            f"saamfi_url='{self._saamfi_url}', "
            f"system_id={self._system_id}, "
            f"tenant_id={self._tenant_id}, "
            f"client_id={self._client_id}"
            ")"
        )
