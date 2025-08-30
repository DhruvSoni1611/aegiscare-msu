import uuid
from datetime import datetime, timedelta
from .connection import fetch_one, fetch_all, exec_one, exec_many
from . import queries as Q
from app.core.security import hash_password, verify_password

# USERS


def get_user_by_email(email: str):
    return fetch_one(Q.SQL_GET_USER_BY_EMAIL, (email,))


def create_user(email: str, full_name: str, password: str, role: str):
    pw = hash_password(password)
    return exec_one(Q.SQL_INSERT_USER, (email, full_name, pw, role))


def check_password(email: str, password: str):
    row = fetch_one(Q.SQL_GET_USER_BY_EMAIL, (email,))
    if not row or not row["is_active"]:
        return None
    if verify_password(password, row["password_hash"]):
        return row
    return None

# SESSIONS


def create_session(user_id: int, hours_valid: int = 8):
    sid = str(uuid.uuid4())
    expires = datetime.utcnow() + timedelta(hours=hours_valid)
    exec_one(Q.SQL_INSERT_SESSION, (sid, user_id,
             expires.strftime("%Y-%m-%d %H:%M:%S")))
    return sid, expires


def get_session(session_id: str):
    return fetch_one(Q.SQL_GET_SESSION, (session_id,))


def touch_session(session_id: str):
    exec_one(Q.SQL_TOUCH_SESSION, (session_id,))


def delete_session(session_id: str):
    exec_one(Q.SQL_DELETE_SESSION, (session_id,))

# UPLOADS & INGEST


def start_upload(user_id: int, filename: str) -> int:
    return exec_one(Q.SQL_INSERT_UPLOAD, (user_id, filename))


def complete_upload(upload_id: int, rows_parsed: int, rows_loaded: int):
    exec_one(Q.SQL_COMPLETE_UPLOAD, (rows_parsed, rows_loaded, upload_id))


def fail_upload(upload_id: int, error_msg: str):
    exec_one(Q.SQL_FAIL_UPLOAD, (error_msg, upload_id))


def get_patient_id_by_uid(uid: str):
    row = fetch_one(Q.SQL_GET_PATIENT_BY_UID, (uid,))
    return row["id"] if row else None


def insert_patient(uid, patient_name, phone, age, sex):
    return exec_one(Q.SQL_INSERT_PATIENT, (uid, patient_name, phone, age, sex))


def update_patient(patient_id, patient_name, phone, age, sex):
    exec_one(Q.SQL_UPDATE_PATIENT, (patient_name, phone, age, sex, patient_id))


def insert_observations(rows):
    exec_many(Q.SQL_INSERT_OBSERVATION, rows)


def insert_vitals_summary(patient_id, chest_pain_type, resting_bp, cholesterol, fasting_bs,
                          resting_ecg, max_heart_rate, exercise_angina, st_depression,
                          st_slope, num_vessels, thalassemia, target):
    exec_one(Q.SQL_INSERT_VITALS_SUMMARY, (patient_id, chest_pain_type, resting_bp,
             cholesterol, fasting_bs, resting_ecg, max_heart_rate, exercise_angina, st_depression,
             st_slope, num_vessels, thalassemia, target))


def insert_patient_outcomes(patient_id, readmission, complication, mortality,
                            readmission_risk, complication_risk, mortality_risk):
    exec_one(Q.SQL_INSERT_PATIENT_OUTCOMES, (patient_id, readmission, complication, mortality,
             readmission_risk, complication_risk, mortality_risk))

# DASHBOARD - Comprehensive statistics


def get_dashboard_stats():
    """Get comprehensive dashboard statistics"""
    return fetch_one(Q.SQL_GET_DASHBOARD_STATS)


def count_patients():
    result = fetch_one(Q.SQL_COUNT_PATIENTS)
    return result["count"] if result else 0


def count_observations():
    result = fetch_one(Q.SQL_COUNT_OBS)
    return result["count"] if result else 0


def count_uploads():
    result = fetch_one(Q.SQL_COUNT_UPLOADS)
    return result["count"] if result else 0


def get_vitals_summary():
    """Get vitals summary for dashboard charts"""
    return fetch_one(Q.SQL_GET_VITALS_SUMMARY)


def get_recent_activity():
    """Get recent patient activity for dashboard"""
    return fetch_all(Q.SQL_GET_RECENT_ACTIVITY)


def list_patients(limit: int = 100, offset: int = 0):
    """Get paginated list of patients with vitals"""
    return fetch_all(Q.SQL_LIST_PATIENTS, (limit, offset))


def search_patients(query: str):
    """Search patients by name or ID"""
    search_term = f"%{query}%"
    return fetch_all(Q.SQL_SEARCH_PATIENTS, (search_term, search_term))


def get_patient_vitals(patient_id: int):
    """Get all vitals for a specific patient"""
    return fetch_all(Q.SQL_GET_PATIENT_VITALS, (patient_id,))


def get_vitals_by_type(patient_id: int, obs_type: str):
    """Get specific vital signs over time for a patient"""
    return fetch_all(Q.SQL_GET_VITALS_BY_TYPE, (patient_id, obs_type))


def get_total_patients_count():
    """Get total count of patients for pagination"""
    result = fetch_one(Q.SQL_COUNT_PATIENTS)
    return result["count"] if result else 0


def get_patient_by_id(patient_id: int):
    """Get patient by ID for ML predictions"""
    return fetch_one(Q.SQL_GET_PATIENT_BY_ID, (patient_id,))
