from fastapi import APIRouter, Depends, Query, HTTPException
from app.api.deps import require_role
from app.db import repo

router = APIRouter(prefix="/patients", tags=["patients"])


@router.get("/")
def list_patients(
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    search: str = Query(None, description="Search by name or ID"),
    session=Depends(require_role("doctor", "assistant"))
):
    """Get comprehensive list of patients with vitals summary"""
    try:
        if search:
            patients = repo.search_patients(search, limit)
        else:
            patients = repo.list_patients(limit, offset)

        # Format patient data for frontend
        formatted_patients = []
        for patient in patients:
            formatted_patient = {
                "id": patient["id"],
                "uid": patient["patient_uid"],
                "name": f"{patient['first_name']} {patient['last_name']}".strip(),
                "age": patient["age"],
                "sex": patient["sex"],
                "contact_phone": patient.get("contact_phone"),
                "height_cm": patient.get("height_cm"),
                "weight_kg": patient.get("weight_kg"),
                "bmi": patient.get("bmi"),
                "created_at": patient.get("created_at"),
                # Vitals summary
                "bp_systolic": patient.get("bp_systolic"),
                "bp_diastolic": patient.get("bp_diastolic"),
                "heart_rate": patient.get("heart_rate"),
                "temperature": patient.get("temperature"),
                "oxygen_saturation": patient.get("oxygen_saturation"),
                "respiratory_rate": patient.get("respiratory_rate"),
                "cholesterol": patient.get("cholesterol"),
                "glucose": patient.get("glucose")
            }
            formatted_patients.append(formatted_patient)

        return {
            "patients": formatted_patients,
            "total": len(formatted_patients),
            "limit": limit,
            "offset": offset
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch patients: {str(e)}")


@router.get("/{patient_id}")
def get_patient(
    patient_id: int,
    session=Depends(require_role("doctor", "assistant"))
):
    """Get detailed patient information"""
    try:
        patient = repo.get_patient_details(patient_id)
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")

        return {
            "id": patient["id"],
            "uid": patient["patient_uid"],
            "name": f"{patient['first_name']} {patient['last_name']}".strip(),
            "age": patient["age"],
            "sex": patient["sex"],
            "contact_phone": patient.get("contact_phone"),
            "height_cm": patient.get("height_cm"),
            "weight_kg": patient.get("weight_kg"),
            "bmi": patient.get("bmi"),
            "created_at": patient.get("created_at"),
            "updated_at": patient.get("updated_at"),
            # Vitals summary
            "bp_systolic": patient.get("bp_systolic"),
            "bp_diastolic": patient.get("bp_diastolic"),
            "heart_rate": patient.get("heart_rate"),
            "temperature": patient.get("temperature"),
            "oxygen_saturation": patient.get("oxygen_saturation"),
            "respiratory_rate": patient.get("respiratory_rate"),
            "cholesterol": patient.get("cholesterol"),
            "glucose": patient.get("glucose"),
            "last_updated": patient.get("last_updated")
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch patient: {str(e)}")


@router.get("/{patient_id}/vitals")
def get_patient_vitals(
    patient_id: int,
    session=Depends(require_role("doctor", "assistant"))
):
    """Get all vital signs for a specific patient"""
    try:
        vitals = repo.get_patient_vitals(patient_id)
        if not vitals:
            return {"vitals": [], "message": "No vitals data found for this patient"}

        return {
            "patient_id": patient_id,
            "vitals": vitals,
            "total_observations": len(vitals)
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch vitals: {str(e)}")


@router.get("/{patient_id}/vitals/{obs_type}")
def get_vitals_by_type(
    patient_id: int,
    obs_type: str,
    session=Depends(require_role("doctor", "assistant"))
):
    """Get specific vital signs over time for trend analysis"""
    try:
        vitals = repo.get_vitals_by_type(patient_id, obs_type.upper())
        if not vitals:
            return {
                "patient_id": patient_id,
                "obs_type": obs_type,
                "vitals": [],
                "message": f"No {obs_type} data found for this patient"
            }

        return {
            "patient_id": patient_id,
            "obs_type": obs_type,
            "vitals": vitals,
            "total_observations": len(vitals)
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch vitals: {str(e)}")


@router.get("/search")
def search_patients(
    q: str = Query(..., description="Search query for patient name or ID"),
    limit: int = Query(20, ge=1, le=100),
    session=Depends(require_role("doctor", "assistant"))
):
    """Search patients by name or ID"""
    try:
        patients = repo.search_patients(q, limit)

        formatted_patients = []
        for patient in patients:
            formatted_patient = {
                "id": patient["id"],
                "uid": patient["patient_uid"],
                "name": f"{patient['first_name']} {patient['last_name']}".strip(),
                "age": patient["age"],
                "sex": patient["sex"]
            }
            formatted_patients.append(formatted_patient)

        return {
            "query": q,
            "patients": formatted_patients,
            "total": len(formatted_patients),
            "limit": limit
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")
