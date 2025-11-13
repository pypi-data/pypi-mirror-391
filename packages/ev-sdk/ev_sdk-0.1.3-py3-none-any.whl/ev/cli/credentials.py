from __future__ import annotations

import json
import os
from base64 import urlsafe_b64decode
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import requests
import toml
from pydantic import BaseModel


class AuthorizationError(Exception):
    """Exception raised when authorization fails."""

    pass


class Token(BaseModel):
    """Authentication token with workspace context."""

    workspace_id: str
    access_token: str
    refresh_token: str

    def is_expired(self) -> bool:
        """Decodes the access_token JWT to check the 'exp' field."""
        return True


class DeviceAuthorization(BaseModel):
    """Response from device authorization endpoint for OAuth device flow."""

    device_code: str
    user_code: str
    verification_uri: str
    verification_uri_complete: str
    expires_in: int
    interval: int


def device_authorize(endpoint_url: str) -> DeviceAuthorization:
    """Initiate device authorization flow."""
    url = f"{endpoint_url}/v1/auth/device/authorize"
    res = requests.post(url)
    res.raise_for_status()
    return DeviceAuthorization.model_validate(res.json())


def device_token(endpoint_url: str, device_code: str) -> Token:
    """Exchange device code for access and refresh tokens."""
    url = f"{endpoint_url}/v1/auth/device/token"
    res = requests.post(url, json={"device_code": device_code})
    res.raise_for_status()
    return Token.model_validate(res.json())


def refresh_token(endpoint_url: str, refresh_token: str) -> Token:
    """Refresh access token using refresh token."""
    url = f"{endpoint_url}/v1/auth/refresh"
    res = requests.post(url, json={"refresh_token": refresh_token})
    res.raise_for_status()
    return Token.model_validate(res.json())


def decode_jwt_expiration(access_token: str) -> datetime | None:
    """Decode JWT access token to extract expiration time.

    Args:
        access_token: JWT access token string

    Returns:
        Expiration datetime or None if unable to decode
    """
    try:
        # JWT format: header.payload.signature
        parts = access_token.split(".")
        if len(parts) != 3:
            return None

        # Decode payload (add padding if needed)
        payload = parts[1]
        padding = 4 - (len(payload) % 4)
        if padding != 4:
            payload += "=" * padding

        decoded = urlsafe_b64decode(payload)
        claims = json.loads(decoded)

        # Extract 'exp' claim (Unix timestamp)
        if "exp" in claims:
            return datetime.fromtimestamp(claims["exp"])

        return None
    except Exception:
        return None


class Credentials:
    """Manages credentials storage in EV_HOME/credentials TOML file."""

    @classmethod
    def file_path(cls) -> Path:
        """Get path to credentials file."""
        ev_home = os.environ.get("EV_HOME")
        if ev_home:
            return Path(ev_home) / "credentials"
        return Path.home() / ".ev" / "credentials"

    @classmethod
    def load(cls, profile: str) -> Token | None:
        """Load token for a profile.

        Args:
            profile: Profile name

        Returns:
            Token or None if not found
        """
        file_path = cls.file_path()
        if not file_path.exists():
            return None

        try:
            with file_path.open("r", encoding="utf-8") as f:
                credentials: dict[str, Any] = toml.load(f)
                if token_data := credentials.get(profile):
                    return Token.model_validate(token_data)
                return None
        except Exception:
            return None

    @classmethod
    def save(cls, profile: str, token: Token) -> None:
        """Save token for a profile.

        Args:
            profile: Profile name
            token: Authentication token from API

        Raises:
            OSError: If file operations fail
        """
        credentials_path = cls.file_path()
        credentials_path.parent.mkdir(exist_ok=True, parents=True)

        # Load existing credentials
        if credentials_path.exists():
            with credentials_path.open("r", encoding="utf-8") as f:
                data = toml.load(f)
        else:
            data = {}

        # Update with new credentials (convert Token to dict)
        data[profile] = token.model_dump()

        # Write with secure permissions
        with credentials_path.open("w", encoding="utf-8") as f:
            toml.dump(data, f)

        # Set file permissions to 0o600 (user read/write only)
        credentials_path.chmod(0o600)

    @classmethod
    def is_expired(cls, token: Token, buffer_minutes: int = 5) -> bool:
        """Check if a token is expired or expiring soon.

        Args:
            token: Token to check
            buffer_minutes: Consider token expired if it expires within this many minutes

        Returns:
            True if token is expired or expiring soon
        """
        expires_at = decode_jwt_expiration(token.access_token)
        if expires_at is None:
            # Unable to decode, assume expired
            return True

        time_until_expiry = expires_at - datetime.now()
        return time_until_expiry <= timedelta(minutes=buffer_minutes)

    @classmethod
    def refresh(cls, endpoint_url: str, token: Token) -> Token:
        """Refresh an expired or expiring token.

        Args:
            endpoint_url: API endpoint URL
            token: Current token with refresh_token

        Returns:
            New refreshed token

        Raises:
            AuthorizationError: If refresh fails
        """
        if not token.refresh_token:
            raise AuthorizationError("No refresh token available")

        try:
            return refresh_token(endpoint_url, token.refresh_token)
        except requests.HTTPError as e:
            raise AuthorizationError(f"Token refresh failed: {e}") from e
