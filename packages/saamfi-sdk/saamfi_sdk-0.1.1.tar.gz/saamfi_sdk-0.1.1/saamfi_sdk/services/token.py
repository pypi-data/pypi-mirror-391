from __future__ import annotations

import logging
import base64
from typing import List, Optional

import jwt
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization import load_der_public_key

from saamfi_sdk.exceptions import SaamfiConnectionError, SaamfiTokenValidationError

from .base import SaamfiServiceBase

logger = logging.getLogger(__name__)


class TokenService(SaamfiServiceBase):
    """Handle public key retrieval and JWT token operations."""

    ROLE_CLAIM = "role"
    SYSTEM_CLAIM = "system"
    USERNAME_CLAIM = "username"
    ID_CLAIM = "persId"

    def __init__(self, base_url: str, session):
        super().__init__(base_url, session)
        self._public_key_cache: Optional[bytes] = None

    @property
    def public_key_bytes(self) -> Optional[bytes]:
        """Return cached public key bytes, if available."""
        return self._public_key_cache

    def fetch_public_key_bytes(self) -> bytes:
        """Retrieve raw DER-encoded public key bytes from the Saamfi server."""
        if self._public_key_cache is not None:
            return self._public_key_cache

        try:
            response = self._get("public/publicKey", timeout=30)
            response.raise_for_status()
        except Exception as exc:
            logger.error("Error retrieving public key: %s", exc)
            raise SaamfiConnectionError(f"Error retrieving public key: {exc}") from exc

        key_bytes: Optional[bytes] = None
        payload = response.text.strip()

        # Format 1: Legacy numeric list "[48, 130, ...]"
        if payload.startswith("[") and payload.endswith("]"):
            key_string = payload[1:-1]
            byte_strings = key_string.split(",")

            try:
                byte_values = []
                for item in byte_strings:
                    stripped = item.strip()
                    if not stripped:
                        raise ValueError("Empty byte element in public key payload")
                    value = int(stripped)
                    if not -256 <= value <= 255:
                        raise ValueError(f"Byte element out of range: {value}")
                    byte_values.append(value & 0xFF)
                key_bytes = bytes(byte_values)
            except Exception as exc:
                logger.error("Invalid public key payload: %s", payload)
                raise SaamfiConnectionError(f"Error retrieving public key: {exc}") from exc

        # Format 2: PEM with headers (-----BEGIN PUBLIC KEY-----)
        if key_bytes is None and "BEGIN PUBLIC KEY" in payload:
            try:
                pem_lines = [
                    line.strip()
                    for line in payload.splitlines()
                    if line and "BEGIN" not in line and "END" not in line
                ]
                key_bytes = base64.b64decode("".join(pem_lines), validate=True)
            except Exception as exc:
                logger.error("Invalid PEM-formatted public key payload")
                raise SaamfiConnectionError(f"Error retrieving public key: {exc}") from exc

        # Format 3: Plain base64 string
        if key_bytes is None:
            try:
                key_bytes = base64.b64decode(payload, validate=True)
            except Exception:
                logger.error("Invalid public key payload: %s", payload[:64] + "...")
                raise SaamfiConnectionError("Error retrieving public key: invalid payload format")

        if not key_bytes:
            logger.error("Public key payload is empty")
            raise SaamfiConnectionError("Error retrieving public key: empty payload")

        self._public_key_cache = key_bytes
        logger.info("Public key successfully retrieved from Saamfi server")
        return key_bytes

    def get_rsa_public_key(self) -> rsa.RSAPublicKey:
        """Return the RSA public key object used to validate JWT tokens."""
        try:
            key_bytes = self.fetch_public_key_bytes()
            public_key = load_der_public_key(key_bytes, backend=default_backend())
        except SaamfiConnectionError:
            raise
        except Exception as exc:
            logger.error("Error getting public key: %s", exc)
            raise SaamfiConnectionError(f"Error getting public key: {exc}") from exc

        if not isinstance(public_key, rsa.RSAPublicKey):
            raise SaamfiConnectionError("Retrieved key is not an RSA public key")
        return public_key

    def extract_roles(self, auth_token: str) -> List[str]:
        """Extract roles from a JWT token."""
        try:
            decoded_token = jwt.decode(
                auth_token,
                self.get_rsa_public_key(),
                algorithms=["RS256"],
            )
        except Exception as exc:
            logger.warning("Error extracting roles from JWT: %s", exc)
            return []

        role_claim = decoded_token.get(self.ROLE_CLAIM, "")
        if not role_claim:
            return []
        return [role.strip() for role in role_claim.split(",")]

    def validate_token(self, auth_token: str) -> dict:
        """Validate a JWT token and return decoded claims."""
        try:
            decoded_token = jwt.decode(
                auth_token,
                self.get_rsa_public_key(),
                algorithms=["RS256"],
            )
        except jwt.ExpiredSignatureError as exc:
            logger.error("Token has expired: %s", exc)
            raise SaamfiTokenValidationError(f"Token has expired: {exc}") from exc
        except jwt.InvalidTokenError as exc:
            logger.error("Invalid token: %s", exc)
            raise SaamfiTokenValidationError(f"Invalid token: {exc}") from exc
        except Exception as exc:
            logger.error("Error validating token: %s", exc)
            raise SaamfiTokenValidationError(f"Error validating token: {exc}") from exc

        return decoded_token

    def reset_public_key_cache(self) -> None:
        """Clear the cached public key. Intended for testing."""
        self._public_key_cache = None

