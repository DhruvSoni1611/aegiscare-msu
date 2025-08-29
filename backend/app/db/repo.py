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


def insert_patient(uid, first, last, age, sex, phone):
    return exec_one(Q.SQL_INSERT_PATIENT, (uid, first, last, age, sex, phone))


def insert_observations(rows):
    exec_many(Q.SQL_INSERT_OBSERVATION, rows)

# DASHBOARD


def count_patients(): return fetch_one(Q.SQL_COUNT_PATIENTS)["COUNT(*)"]
def count_observations(): return fetch_one(Q.SQL_COUNT_OBS)["COUNT(*)"]

# LIST


def list_patients(limit=100, offset=0):
    return fetch_all(Q.SQL_LIST_PATIENTS, (limit, offset))
