from __future__ import annotations

import logging
from typing import List, Optional

from .base import SaamfiServiceBase

logger = logging.getLogger(__name__)


class InstitutionService(SaamfiServiceBase):
    """Operations for retrieving institution metadata."""

    def get_institution_by_nit(self, auth_token: str, nit: str) -> Optional[str]:
        """Retrieve an institution by its NIT."""
        headers = self._authorization_header(auth_token)
        try:
            response = self._get(f"public/institutions?nit={nit}", headers=headers, timeout=30)
        except Exception as exc:
            logger.warning("Error retrieving institution by NIT: %s", exc)
            return None

        if self._is_success(response.status_code):
            logger.info("Retrieved institution by NIT '%s'", nit)
            return response.text

        logger.warning("Failed to retrieve institution by NIT '%s': %s", nit, response.status_code)
        return None

    def get_institutions_by_ids(self, auth_token: str, institution_ids: List[int]) -> Optional[str]:
        """Retrieve multiple institutions by ID list."""
        if not institution_ids:
            logger.warning("No institution IDs provided")
            return None

        headers = self._authorization_header(auth_token)
        params = {
            "institutionIds": ",".join(str(institution_id) for institution_id in institution_ids)
        }

        try:
            response = self._get(
                "institutions",
                headers=headers,
                params=params,
                timeout=30,
            )
        except Exception as exc:
            logger.warning("Error retrieving institutions by IDs: %s", exc)
            return None

        if self._is_success(response.status_code):
            logger.info("Retrieved institutions for IDs %s", institution_ids)
            return response.text

        logger.warning(
            "Failed to retrieve institutions by IDs %s: %s",
            institution_ids,
            response.status_code,
        )
        return None

