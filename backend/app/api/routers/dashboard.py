from fastapi import APIRouter, Depends, Query
from app.api.deps import require_role
from app.db import repo

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/stats")
def stats(session=Depends(require_role("doctor", "assistant"))):
    """Get comprehensive dashboard statistics"""
    try:
        stats_data = repo.get_dashboard_stats()
        return {
            "total_patients": stats_data.get("total_patients", 0),
            "total_observations": stats_data.get("total_observations", 0),
            "total_uploads": stats_data.get("total_uploads", 0),
            "male_patients": stats_data.get("male_patients", 0),
            "female_patients": stats_data.get("female_patients", 0),
            "avg_age": round(stats_data.get("avg_age", 0), 1) if stats_data.get("avg_age") else 0,
            "avg_bmi": round(stats_data.get("avg_bmi", 0), 2) if stats_data.get("avg_bmi") else 0
        }
    except Exception as e:
        return {
            "total_patients": 0,
            "total_observations": 0,
            "total_uploads": 0,
            "male_patients": 0,
            "female_patients": 0,
            "avg_age": 0,
            "avg_bmi": 0,
            "error": str(e)
        }


@router.get("/patients")
def list_patients(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    session=Depends(require_role("doctor", "assistant"))
):
    """Get list of patients with vitals summary for dashboard"""
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
    """Get summary of vital signs across all patients"""
    try:
        # Get basic counts for different vital ranges
        patients = repo.list_patients(1000, 0)  # Get all patients for summary

        # Calculate vital signs ranges
        bp_systolic_ranges = {"normal": 0, "elevated": 0, "high": 0}
        bmi_ranges = {"underweight": 0, "normal": 0,
                      "overweight": 0, "obese": 0}
        heart_rate_ranges = {"normal": 0, "elevated": 0, "high": 0}

        for patient in patients:
            # Blood pressure classification
            if patient.get("bp_systolic"):
                if patient["bp_systolic"] < 120:
                    bp_systolic_ranges["normal"] += 1
                elif patient["bp_systolic"] < 130:
                    bp_systolic_ranges["elevated"] += 1
                else:
                    bp_systolic_ranges["high"] += 1

            # BMI classification
            if patient.get("bmi"):
                if patient["bmi"] < 18.5:
                    bmi_ranges["underweight"] += 1
                elif patient["bmi"] < 25:
                    bmi_ranges["normal"] += 1
                elif patient["bmi"] < 30:
                    bmi_ranges["overweight"] += 1
                else:
                    bmi_ranges["obese"] += 1

            # Heart rate classification
            if patient.get("heart_rate"):
                if 60 <= patient["heart_rate"] <= 100:
                    heart_rate_ranges["normal"] += 1
                elif 100 < patient["heart_rate"] <= 120:
                    heart_rate_ranges["elevated"] += 1
                else:
                    heart_rate_ranges["high"] += 1

        return {
            "blood_pressure_ranges": bp_systolic_ranges,
            "bmi_ranges": bmi_ranges,
            "heart_rate_ranges": heart_rate_ranges,
            "total_patients": len(patients)
        }

    except Exception as e:
        return {"error": str(e)}


@router.get("/recent-activity")
def recent_activity(session=Depends(require_role("doctor", "assistant"))):
    """Get recent uploads and data changes"""
    try:
        # Get recent patients (last 10)
        recent_patients = repo.list_patients(10, 0)

        return {
            "recent_patients": recent_patients,
            "last_updated": recent_patients[0]["created_at"] if recent_patients else None
        }
    except Exception as e:
        return {"recent_patients": [], "error": str(e)}
