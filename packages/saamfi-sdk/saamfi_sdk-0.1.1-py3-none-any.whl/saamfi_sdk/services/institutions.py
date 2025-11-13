from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Union

from .base import SaamfiServiceBase

logger = logging.getLogger(__name__)


InstitutionPayload = Union[List[Dict[str, Any]], Dict[str, Any]]


class InstitutionService(SaamfiServiceBase):
    """Operations for retrieving institution metadata."""

    def list_public_institutions(
        self, *, name: Optional[str] = None, nit: Optional[str] = None
    ) -> Optional[InstitutionPayload]:
        """
        Retrieve the public list of institutions.

        The Saamfi API expects at least one filter (name or nit). Both parameters are optional
        to preserve backward compatibility with older deployments that allowed unfiltered access.
        """
        params: Dict[str, str] = {}
        if name:
            params["name"] = name
        if nit:
            params["nit"] = nit

        request_kwargs: Dict[str, Any] = {"timeout": 30}
        if params:
            request_kwargs["params"] = params

        try:
            response = self._get("public/institutions", **request_kwargs)
        except Exception as exc:
            logger.warning("Error retrieving public institutions: %s", exc)
            return None

        if self._is_success(response.status_code):
            try:
                return response.json()
            except Exception as exc:
                logger.warning("Invalid response when listing public institutions: %s", exc)
                return None

        logger.warning(
            "Failed to retrieve public institutions%s: status code %s",
            f" with filters {params}" if params else "",
            response.status_code,
        )
        return None

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

    def get_institution_params(self, auth_token: str, institution_id: int) -> Optional[Dict[str, Any]]:
        """Retrieve configuration parameters for a specific institution."""
        headers = self._authorization_header(auth_token)
        try:
            response = self._get(
                f"institutions/{institution_id}/params",
                headers=headers,
                timeout=30,
            )
        except Exception as exc:
            logger.warning("Error retrieving params for institution %s: %s", institution_id, exc)
            return None

        if self._is_success(response.status_code):
            try:
                return response.json()
            except Exception as exc:
                logger.warning(
                    "Invalid response while retrieving params for institution %s: %s",
                    institution_id,
                    exc,
                )
                return None

        logger.warning(
            "Failed to retrieve params for institution %s: %s",
            institution_id,
            response.status_code,
        )
        return None

