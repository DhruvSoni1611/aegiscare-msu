from fastapi import APIRouter, Depends, Query
from app.api.deps import require_role
from app.db import repo

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/stats")
def stats(session=Depends(require_role("doctor", "assistant"))):
    """Get comprehensive dashboard statistics for heart disease dataset"""
    try:
        stats_data = repo.get_dashboard_stats()
        return {
            "total_patients": stats_data.get("total_patients", 0),
            "total_observations": stats_data.get("total_observations", 0),
            "total_uploads": stats_data.get("total_uploads", 0),
            "male_patients": stats_data.get("male_patients", 0),
            "female_patients": stats_data.get("female_patients", 0),
            "avg_age": round(stats_data.get("avg_age", 0), 1) if stats_data.get("avg_age") else 0,
            "avg_bp": round(stats_data.get("avg_bp", 0), 1) if stats_data.get("avg_bp") else 0,
            "heart_disease_count": stats_data.get("heart_disease_count", 0),
            "healthy_count": stats_data.get("healthy_count", 0)
        }
    except Exception as e:
        return {
            "total_patients": 0,
            "total_observations": 0,
            "total_uploads": 0,
            "male_patients": 0,
            "female_patients": 0,
            "avg_age": 0,
            "avg_bp": 0,
            "heart_disease_count": 0,
            "healthy_count": 0,
            "error": str(e)
        }


@router.get("/patients")
def list_patients(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    session=Depends(require_role("doctor", "assistant"))
):
    """Get list of patients with heart disease vitals summary for dashboard"""
    try:
        patients = repo.list_patients(limit, offset)
        return {
            "patients": patients,
            "total": len(patients),
            "limit": limit,
            "offset": offset
        }
    except Exception as e:
        return {"patients": [], "total": 0, "error": str(e)}


@router.get("/vitals-summary")
def vitals_summary(session=Depends(require_role("doctor", "assistant"))):
    """Get summary of heart disease vital signs across all patients"""
    try:
        # Get vitals summary from database
        vitals_data = repo.get_vitals_summary()

        if not vitals_data:
            return {"error": "No vitals data available"}

        # Blood pressure ranges
        bp_ranges = {
            "normal": vitals_data.get("bp_normal", 0),
            "elevated": vitals_data.get("bp_elevated", 0),
            "high": vitals_data.get("bp_high", 0)
        }

        # Heart rate ranges
        hr_ranges = {
            "low": vitals_data.get("hr_low", 0),
            "normal": vitals_data.get("hr_normal", 0),
            "high": vitals_data.get("hr_high", 0)
        }

        # Cholesterol ranges
        chol_ranges = {
            "normal": vitals_data.get("chol_normal", 0),
            "borderline": vitals_data.get("chol_borderline", 0),
            "high": vitals_data.get("chol_high", 0)
        }

        # Heart disease status
        heart_disease_status = {
            "healthy": vitals_data.get("healthy", 0),
            "heart_disease": vitals_data.get("heart_disease", 0)
        }

        return {
            "blood_pressure_ranges": bp_ranges,
            "heart_rate_ranges": hr_ranges,
            "cholesterol_ranges": chol_ranges,
            "heart_disease_status": heart_disease_status,
            "total_patients": vitals_data.get("bp_normal", 0) + vitals_data.get("bp_elevated", 0) + vitals_data.get("bp_high", 0)
        }

    except Exception as e:
        return {"error": str(e)}


@router.get("/recent-activity")
def recent_activity(session=Depends(require_role("doctor", "assistant"))):
    """Get recent patient activity for dashboard"""
    try:
        # Get recent patients with heart disease status
        recent_patients = repo.get_recent_activity()

        return {
            "recent_patients": recent_patients,
            "last_updated": recent_patients[0]["created_at"] if recent_patients else None
        }
    except Exception as e:
        return {"recent_patients": [], "error": str(e)}
