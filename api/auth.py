import os
import time
from typing import Optional

import jwt
from fastapi import Depends, Header, HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer


class AuthConfig:
    """Configuration for API keys and JWT validation."""

    def __init__(self) -> None:
        api_keys = os.getenv("API_KEYS", "demo-key").split(",")
        self.api_keys = {key.strip() for key in api_keys if key.strip()}
        self.jwt_secret = os.getenv("JWT_SECRET", "demo-secret")
        self.jwt_algorithm = os.getenv("JWT_ALGORITHM", "HS256")


security_scheme = HTTPBearer(auto_error=False)


def require_auth(
    api_key: Optional[str] = Header(None, alias="X-API-Key"),
    credentials: Optional[HTTPAuthorizationCredentials] = Security(security_scheme),
    config: AuthConfig = Depends(AuthConfig),
) -> str:
    """
    Validate API key header or JWT bearer token.

    Returns the subject identifier for downstream use.
    """
    if api_key:
        if api_key in config.api_keys:
            return api_key
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )

    if credentials:
        try:
            payload = jwt.decode(
                credentials.credentials,
                config.jwt_secret,
                algorithms=[config.jwt_algorithm],
            )
        except jwt.PyJWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
            ) from None
        exp = payload.get("exp")
        if exp and exp < time.time():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expired",
            )
        subject = payload.get("sub")
        return subject or "token"

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Authorization required",
    )

