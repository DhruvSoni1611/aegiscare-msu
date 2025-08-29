from fastapi import APIRouter, Depends, Query
from app.api.deps import require_role
from app.db import repo

router = APIRouter(prefix="/patients", tags=["patients"])


@router.get("/")
def list_patients(
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    session=Depends(require_role("doctor", "assistant"))
):
    rows = repo.list_patients(limit, offset)
    return [
        {
            "id": r["id"],
            "uid": r["patient_uid"],
            "name": f"{r['first_name']} {r['last_name']}".strip(),
            "age": r["age"],
            "sex": r["sex"]
        } for r in rows
    ]
