from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from .base import SaamfiServiceBase

logger = logging.getLogger(__name__)


class SystemService(SaamfiServiceBase):
    """Operations related to systems metadata and configuration."""

    def list_public_systems(self) -> Optional[List[Dict[str, Any]]]:
        """Retrieve public information about available systems."""
        try:
            response = self._get("public/systems", timeout=30)
        except Exception as exc:
            logger.warning("Error retrieving public systems: %s", exc)
            return None

        if self._is_success(response.status_code):
            try:
                return response.json()
            except Exception as exc:
                logger.warning("Invalid response when listing public systems: %s", exc)
                return None

        logger.warning("Failed to retrieve public systems: status code %s", response.status_code)
        return None

    def get_system_roles(self, auth_token: str, system_id: int) -> Optional[List[Dict[str, Any]]]:
        """Retrieve roles for the given system."""
        headers = self._authorization_header(auth_token)
        try:
            response = self._get(
                f"systems/{system_id}/roles",
                headers=headers,
                timeout=30,
            )
        except Exception as exc:
            logger.warning("Error retrieving roles for system %s: %s", system_id, exc)
            return None

        if self._is_success(response.status_code):
            try:
                return response.json()
            except Exception as exc:
                logger.warning(
                    "Invalid response while retrieving roles for system %s: %s",
                    system_id,
                    exc,
                )
                return None

        logger.warning(
            "Failed to retrieve roles for system %s: %s",
            system_id,
            response.status_code,
        )
        return None

