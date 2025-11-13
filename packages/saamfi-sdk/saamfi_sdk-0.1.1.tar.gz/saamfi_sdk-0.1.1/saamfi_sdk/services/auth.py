from __future__ import annotations

import logging
from typing import Optional

from saamfi_sdk.exceptions import (
    SaamfiAuthenticationError,
    SaamfiConnectionError,
    SaamfiTokenValidationError,
)
from saamfi_sdk.models import LoginBody, LoginResponse, UserDetailToken

from .base import SaamfiServiceBase
from .token import TokenService

logger = logging.getLogger(__name__)


class AuthenticationService(SaamfiServiceBase):
    """Authentication-related operations."""

    def __init__(
        self,
        base_url: str,
        session,
        system_id: int,
        token_service: TokenService,
    ):
        super().__init__(base_url, session)
        self._system_id = system_id
        self._token_service = token_service

    def login(self, username: str, password: str) -> Optional[LoginResponse]:
        """Authenticate a user and return the login response."""
        login_body = LoginBody(username=username, password=password, system_id=self._system_id)

        try:
            response = self._post(
                "public/authentication/login",
                json=login_body.model_dump(by_alias=True),
                timeout=30,
            )
        except Exception as exc:
            logger.error("Error in authentication request: %s", exc)
            raise SaamfiConnectionError(f"Error during authentication: {exc}") from exc

        if self._is_success(response.status_code):
            try:
                login_response = LoginResponse(**response.json())
            except Exception as exc:
                logger.warning("Unexpected login response payload: %s", exc)
                return None

            logger.info("User '%s' authenticated successfully", username)
            return login_response

        if response.status_code == 401:
            logger.warning("Authentication failed for user '%s': 401", username)
            return None

        logger.warning("Authentication failed for user '%s': %s", username, response.status_code)
        return None

    def get_roles_from_jwt(self, auth_token: str) -> list[str]:
        """Return roles stored in the JWT token."""
        return self._token_service.extract_roles(auth_token)

    def validate_token(self, auth_token: str) -> UserDetailToken:
        """Validate a JWT token and return user details."""
        decoded_token = self._token_service.validate_token(auth_token)

        try:
            username = str(decoded_token.get(TokenService.USERNAME_CLAIM))
            system = int(decoded_token.get(TokenService.SYSTEM_CLAIM))
            pers_id = str(decoded_token.get(TokenService.ID_CLAIM))
        except (TypeError, ValueError, KeyError) as exc:
            logger.error("Missing required claim in token: %s", exc)
            raise SaamfiTokenValidationError(f"Missing required claim in token: {exc}") from exc

        roles = self.get_roles_from_jwt(auth_token)

        user_detail = UserDetailToken(
            username=username,
            system=system,
            pers_id=pers_id,
            roles=roles,
        )
        logger.info("Token validated successfully for user '%s'", username)
        return user_detail

