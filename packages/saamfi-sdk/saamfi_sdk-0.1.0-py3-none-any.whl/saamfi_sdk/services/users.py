from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from saamfi_sdk.exceptions import SaamfiAuthenticationError, SaamfiConnectionError
from saamfi_sdk.models import UserInfo

from .base import SaamfiServiceBase

logger = logging.getLogger(__name__)


class UserService(SaamfiServiceBase):
    """Operations for querying user information."""

    def get_user_info(self, auth_token: str, user_id: int) -> Optional[UserInfo]:
        """Retrieve full user information by ID."""
        headers = self._authorization_header(auth_token)
        try:
            response = self._get(f"users/{user_id}", headers=headers, timeout=30)
        except Exception as exc:
            logger.error("Error retrieving user info: %s", exc)
            raise SaamfiConnectionError(f"Error retrieving user info: {exc}") from exc

        if self._is_success(response.status_code):
            try:
                user = UserInfo(**response.json())
            except Exception as exc:
                logger.warning("Unexpected user info payload: %s", exc)
                return None

            logger.info("User info retrieved successfully for user ID %s", user_id)
            return user

        logger.warning("Failed to retrieve user info for ID %s: %s", user_id, response.status_code)
        return None

    def get_user_by_username(self, auth_token: str, username: str) -> Optional[Dict[str, Any]]:
        """Retrieve a user by username."""
        headers = self._json_headers(auth_token)
        try:
            response = self._post(
                "users/user-from-username",
                json=username,
                headers=headers,
                timeout=30,
            )
        except Exception as exc:
            logger.error("Error searching user by username: %s", exc)
            raise SaamfiConnectionError(f"Error searching user by username: {exc}") from exc

        if response.status_code == 401:
            logger.error("Authentication error when searching user by username")
            raise SaamfiAuthenticationError("Error authenticating")

        if response.status_code != 200:
            logger.error(
                "Error searching user by username '%s': %s", username, response.status_code
            )
            raise SaamfiConnectionError("Error")

        try:
            payload = response.json()
        except ValueError:
            logger.warning("Empty response when searching user by username '%s'", username)
            return None

        logger.info("User found by username '%s'", username)
        return payload

    def get_users_by_document(self, auth_token: str, user_documents: List[str]) -> List[Dict[str, Any]]:
        """Retrieve users by document list."""
        headers = self._json_headers(auth_token)
        try:
            response = self._post(
                "users/users-from-document",
                json=user_documents,
                headers=headers,
                timeout=30,
            )
        except Exception as exc:
            logger.error("Error searching users by documents: %s", exc)
            raise SaamfiConnectionError(f"Error searching users by documents: {exc}") from exc

        if response.status_code == 401:
            logger.error("Authentication error when searching users by documents")
            raise SaamfiAuthenticationError("Error authenticating")

        if response.status_code != 200:
            logger.error(
                "Error searching users by documents %s: %s",
                user_documents,
                response.status_code,
            )
            raise SaamfiConnectionError("Error")

        users = response.json()
        logger.info("Found %s users by documents", len(users))
        return users

    def get_users_from_list(self, auth_token: str, user_ids: List[int]) -> Optional[str]:
        """Retrieve multiple users by ID list."""
        headers = self._json_headers(auth_token)
        try:
            response = self._post(
                "users/users-from-list",
                json=user_ids,
                headers=headers,
                timeout=30,
            )
        except Exception as exc:
            logger.warning("Error retrieving users from list: %s", exc)
            return None

        if self._is_success(response.status_code):
            logger.info("Retrieved users from list of %s IDs", len(user_ids))
            return response.text

        logger.warning("Failed to retrieve users from list: %s", response.status_code)
        return None

    def get_users_by_param_and_value(self, auth_token: str, param: str, value: str) -> Optional[str]:
        """Retrieve users using the generic param/value endpoint."""
        headers = self._authorization_header(auth_token)
        try:
            response = self._get(
                f"users?param={param}&value={value}",
                headers=headers,
                timeout=30,
            )
        except Exception as exc:
            logger.warning("Error retrieving users by parameter: %s", exc)
            return None

        if self._is_success(response.status_code):
            logger.info("Retrieved users by param '%s' and value '%s'", param, value)
            return response.text

        logger.warning(
            "Failed to retrieve users by param '%s' and value '%s': %s",
            param,
            value,
            response.status_code,
        )
        return None

