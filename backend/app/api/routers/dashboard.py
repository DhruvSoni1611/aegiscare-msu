from fastapi import APIRouter, Depends
from app.api.deps import require_role
from app.db import repo

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/stats")
def stats(session=Depends(require_role("doctor", "assistant"))):
    return {
        "total_patients": repo.count_patients(),
        "total_observations": repo.count_observations()
    }
