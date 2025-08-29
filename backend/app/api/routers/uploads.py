from fastapi import APIRouter, File, UploadFile, Depends, HTTPException
from app.api.deps import require_role
from app.services.ingest import ingest_csv

router = APIRouter(prefix="/uploads", tags=["uploads"])


@router.post("/csv")
def upload_csv(
    f: UploadFile = File(...),
    session=Depends(require_role("doctor", "assistant"))
):
    try:
        content = f.file.read()
        res = ingest_csv(
            user_id=session["user_id"], filename=f.filename, file_bytes=content)
        return {"status": "completed", **res}
    except Exception as e:
        raise HTTPException(400, f"CSV ingest failed: {e}")
