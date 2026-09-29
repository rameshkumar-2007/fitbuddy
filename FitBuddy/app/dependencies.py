import secrets

from fastapi import Depends, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from .config import get_settings

admin_auth = HTTPBasic(auto_error=False)

def require_admin(credentials: HTTPBasicCredentials | None = Depends(admin_auth)):
    expected = get_settings().admin_key
    if not expected or secrets.compare_digest(expected, "change-me"):
        raise HTTPException(status_code=503, detail="Admin access is disabled. Configure a unique ADMIN_KEY.")
    if credentials is None:
        raise HTTPException(
            status_code=401,
            detail="Admin authentication required.",
            headers={"WWW-Authenticate": "Basic"},
        )

    valid_username = secrets.compare_digest(credentials.username.encode("utf-8"), b"admin")
    valid_password = secrets.compare_digest(credentials.password.encode("utf-8"), expected.encode("utf-8"))
    if not (valid_username and valid_password):
        raise HTTPException(
            status_code=401,
            detail="Invalid admin credentials.",
            headers={"WWW-Authenticate": "Basic"},
        )
