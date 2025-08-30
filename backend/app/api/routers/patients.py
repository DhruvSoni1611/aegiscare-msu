from fastapi import APIRouter, Depends, Query, HTTPException
from app.api.deps import require_role
from app.db import repo

router = APIRouter(prefix="/patients", tags=["patients"])


@router.get("/")
def list_patients(
    # Increased limit to handle more patients
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    search: str = Query(None, description="Search by name or ID"),
    session=Depends(require_role("doctor", "assistant"))
):
    """Get comprehensive list of patients with heart disease vitals summary"""
    try:
        if search:
            patients = repo.search_patients(search)
        else:
            patients = repo.list_patients(limit, offset)

        # Format patient data for frontend
        formatted_patients = []
        for patient in patients:
            formatted_patient = {
                "id": patient["id"],
                "uid": patient["patient_uid"],
                "name": patient["patient_name"],
                "age": patient["age"],
                "sex": patient["sex"],
                "phone": patient.get("phone"),
                "created_at": patient.get("created_at"),
                "condition": patient.get("condition", "Unknown"),
                # Heart disease vitals summary
                "chest_pain_type": patient.get("chest_pain_type"),
                "resting_bp": patient.get("resting_bp"),
                "cholesterol": patient.get("cholesterol"),
                "fasting_bs": patient.get("fasting_bs"),
                "resting_ecg": patient.get("resting_ecg"),
                "max_heart_rate": patient.get("max_heart_rate"),
                "exercise_angina": patient.get("exercise_angina"),
                "st_depression": patient.get("st_depression"),
                "st_slope": patient.get("st_slope"),
                "num_vessels": patient.get("num_vessels"),
                "thalassemia": patient.get("thalassemia"),
                "target": patient.get("target")
            }
            formatted_patients.append(formatted_patient)

        # Get total count for pagination
        total_count = repo.get_total_patients_count()

        return {
            "patients": formatted_patients,
            "total": total_count,
            "limit": limit,
            "offset": offset,
            "total_pages": (total_count + limit - 1) // limit
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch patients: {str(e)}")


@router.get("/search")
def search_patients(
    q: str = Query(..., description="Search query for patient name or ID"),
    session=Depends(require_role("doctor", "assistant"))
):
    """Search patients by name or ID"""
    try:
        patients = repo.search_patients(q)

        # Format patient data for frontend
        formatted_patients = []
        for patient in patients:
            formatted_patient = {
                "id": patient["id"],
                "uid": patient["patient_uid"],
                "name": patient["patient_name"],
                "age": patient["age"],
                "sex": patient["sex"],
                "phone": patient.get("phone"),
                "created_at": patient.get("created_at"),
                # Heart disease vitals summary
                "chest_pain_type": patient.get("chest_pain_type"),
                "resting_bp": patient.get("resting_bp"),
                "cholesterol": patient.get("cholesterol"),
                "fasting_bs": patient.get("fasting_bs"),
                "resting_ecg": patient.get("resting_ecg"),
                "max_heart_rate": patient.get("max_heart_rate"),
                "exercise_angina": patient.get("exercise_angina"),
                "st_depression": patient.get("st_depression"),
                "st_slope": patient.get("st_slope"),
                "num_vessels": patient.get("num_vessels"),
                "thalassemia": patient.get("thalassemia"),
                "target": patient.get("target")
            }
            formatted_patients.append(formatted_patient)

        return {
            "patients": formatted_patients,
            "total": len(formatted_patients),
            "query": q
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to search patients: {str(e)}")


@router.get("/{patient_id}")
def get_patient(
    patient_id: int,
    session=Depends(require_role("doctor", "assistant"))
):
    """Get detailed patient information"""
    try:
        # Get patient from list_patients with limit 1
        patients = repo.list_patients(1, 0)
        patient = None
        for p in patients:
            if p["id"] == patient_id:
                patient = p
                break

        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")

        return {
            "id": patient["id"],
            "uid": patient["patient_uid"],
            "name": patient["patient_name"],
            "age": patient["age"],
            "sex": patient["sex"],
            "phone": patient.get("phone"),
            "created_at": patient.get("created_at"),
            # Heart disease vitals summary
            "chest_pain_type": patient.get("chest_pain_type"),
            "resting_bp": patient.get("resting_bp"),
            "cholesterol": patient.get("cholesterol"),
            "fasting_bs": patient.get("fasting_bs"),
            "resting_ecg": patient.get("resting_ecg"),
            "max_heart_rate": patient.get("max_heart_rate"),
            "exercise_angina": patient.get("exercise_angina"),
            "st_depression": patient.get("st_depression"),
            "st_slope": patient.get("st_slope"),
            "num_vessels": patient.get("num_vessels"),
            "thalassemia": patient.get("thalassemia"),
            "target": patient.get("target")
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
    """Get patient vitals over time"""
    try:
        vitals = repo.get_patient_vitals(patient_id)
        return {
            "patient_id": patient_id,
            "vitals": vitals,
            "total_observations": len(vitals)
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch patient vitals: {str(e)}")


@router.get("/{patient_id}/vitals/{vital_type}")
def get_vital_by_type(
    patient_id: int,
    vital_type: str,
    session=Depends(require_role("doctor", "assistant"))
):
    """Get specific vital sign over time for a patient"""
    try:
        vitals = repo.get_vitals_by_type(patient_id, vital_type)
        return {
            "patient_id": patient_id,
            "vital_type": vital_type,
            "vitals": vitals,
            "total_observations": len(vitals)
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch vital data: {str(e)}")


@router.get("/{patient_id}/predictions")
def get_patient_predictions(
    patient_id: int,
    session=Depends(require_role("doctor", "assistant"))
):
    """Get ML model predictions for a patient"""
    try:
        # Get patient data for ML predictions
        patient = repo.get_patient_by_id(patient_id)
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")

        # Get vitals data for predictions
        vitals = repo.get_patient_vitals(patient_id)

        # Calculate ML predictions based on patient data and vitals
        predictions = calculate_ml_predictions(patient, vitals)

        return {
            "patient_id": patient_id,
            "predictions": predictions,
            "model_version": "1.0",
            "prediction_timestamp": "2024-01-01T00:00:00Z"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to generate predictions: {str(e)}")


def calculate_ml_predictions(patient, vitals):
    """Calculate ML predictions based on patient data and vitals"""
    try:
        # This is a placeholder for the actual ML model integration
        # In production, this would call your trained ML model

        # Calculate risk scores based on available data
        risk_factors = 0

        # Age risk
        if patient.get('age', 0) > 65:
            risk_factors += 2
        elif patient.get('age', 0) > 45:
            risk_factors += 1

        # Blood pressure risk
        if patient.get('resting_bp', 0) > 140:
            risk_factors += 2
        elif patient.get('resting_bp', 0) > 120:
            risk_factors += 1

        # Cholesterol risk
        if patient.get('cholesterol', 0) > 200:
            risk_factors += 1

        # Heart rate risk
        if patient.get('max_heart_rate', 0) > 150:
            risk_factors += 1

        # Calculate risk percentages
        readmission_risk = min(0.9, 0.1 + (risk_factors * 0.15))
        complication_risk = min(0.8, 0.05 + (risk_factors * 0.12))
        mortality_risk = min(0.6, 0.02 + (risk_factors * 0.08))

        # Outcome predictions
        target = 1 if risk_factors < 3 else 0  # Positive outcome if low risk
        readmiss = 1 if readmission_risk > 0.5 else 0
        complication = 1 if complication_risk > 0.4 else 0
        mortalit = 1 if mortality_risk > 0.3 else 0

        return {
            "target": target,
            "readmiss": readmiss,
            "complication": complication,
            "mortalit": mortalit,
            "readmission_risk": readmission_risk,
            "complication_risk": complication_risk,
            "mortality_risk": mortality_risk
        }

    except Exception as e:
        # Return default predictions if calculation fails
        return {
            "target": 0,
            "readmiss": 0,
            "complication": 0,
            "mortalit": 0,
            "readmission_risk": 0.3,
            "complication_risk": 0.2,
            "mortality_risk": 0.1
        }
