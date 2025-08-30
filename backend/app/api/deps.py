from fastapi import Header, HTTPException, status, Depends
from app.db import repo


def require_session(x_session_id: str | None = Header(default=None, alias="X-Session-Id")):
    if not x_session_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing session")
    s = repo.get_session(x_session_id)
    if not s:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid session")
    repo.touch_session(x_session_id)
    return s  # contains role, user_id, email


def require_role(*roles: str):
    def _inner(session=Depends(require_session)):
        if session["role"] not in roles:
            raise HTTPException(status_code=403, detail="Forbidden")
        return session
    return _inner
