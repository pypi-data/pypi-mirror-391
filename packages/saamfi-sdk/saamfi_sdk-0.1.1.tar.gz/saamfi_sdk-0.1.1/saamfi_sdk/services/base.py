from __future__ import annotations

from typing import Any, Dict, Optional

import requests


class SaamfiServiceBase:
    """Common helpers for Saamfi service classes."""

    def __init__(self, base_url: str, session: requests.Session):
        self._base_url = base_url.rstrip("/")
        self._session = session

    def _build_url(self, path: str) -> str:
        """Construct an absolute URL from a path."""
        return f"{self._base_url}/{path.lstrip('/')}"

    def _get(self, path: str, **kwargs: Any) -> requests.Response:
        """Perform a GET request using the shared session."""
        url = self._build_url(path)
        return self._session.get(url, **kwargs)

    def _post(self, path: str, **kwargs: Any) -> requests.Response:
        """Perform a POST request using the shared session."""
        url = self._build_url(path)
        return self._session.post(url, **kwargs)

    @staticmethod
    def _is_success(status_code: int) -> bool:
        """Check if an HTTP status code represents a successful response."""
        return 200 <= status_code < 300

    @staticmethod
    def _authorization_header(token: str) -> Dict[str, str]:
        """Create a bearer authorization header."""
        return {"Authorization": f"Bearer {token}"}

    @staticmethod
    def _json_headers(token: str) -> Dict[str, str]:
        """Create headers for JSON requests with bearer authorization."""
        headers = SaamfiServiceBase._authorization_header(token)
        headers["Content-Type"] = "application/json"
        return headers

