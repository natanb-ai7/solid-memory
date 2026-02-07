from fastapi import Header, HTTPException
from .config import settings


def require_auth(authorization: str | None = Header(default=None)):
    if settings.single_user_mode:
        return True
    if not authorization or authorization != f"Bearer {settings.auth_secret}":
        raise HTTPException(status_code=401, detail="Unauthorized")
    return True
