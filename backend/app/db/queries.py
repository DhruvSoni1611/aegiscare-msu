# USERS
SQL_GET_USER_BY_EMAIL = "SELECT id, email, full_name, password_hash, role, is_active FROM users WHERE email=%s"
SQL_INSERT_USER = """
INSERT INTO users (email, full_name, password_hash, role)
VALUES (%s, %s, %s, %s)
"""
SQL_GET_USER_BY_ID = "SELECT id, email, full_name, role, is_active FROM users WHERE id=%s"

# SESSIONS
SQL_INSERT_SESSION = """
INSERT INTO sessions (session_id, user_id, expires_at) VALUES (%s, %s, %s)
"""
SQL_GET_SESSION = """
SELECT s.session_id, s.user_id, s.expires_at, u.email, u.full_name, u.role, u.is_active
FROM sessions s
JOIN users u ON u.id = s.user_id
WHERE s.session_id = %s
"""
SQL_TOUCH_SESSION = "UPDATE sessions SET last_seen_at=NOW() WHERE session_id=%s"
SQL_DELETE_SESSION = "DELETE FROM sessions WHERE session_id=%s"

# CSV UPLOADS
SQL_INSERT_UPLOAD = """
INSERT INTO csv_uploads (user_id, filename, status) VALUES (%s, %s, 'processing')
"""
SQL_COMPLETE_UPLOAD = """
UPDATE csv_uploads SET status='completed', rows_parsed=%s, rows_loaded=%s WHERE id=%s
"""
SQL_FAIL_UPLOAD = """
UPDATE csv_uploads SET status='failed', error_msg=%s WHERE id=%s
"""

# PATIENTS
SQL_GET_PATIENT_BY_UID = "SELECT id FROM patients WHERE patient_uid=%s"
SQL_INSERT_PATIENT = """
INSERT INTO patients (patient_uid, first_name, last_name, age, sex, contact_phone)
VALUES (%s, %s, %s, %s, %s, %s)
"""
SQL_INSERT_OBSERVATION = """
INSERT INTO patient_observations (patient_id, obs_type, value_num, value_text, unit, observed_at, source_upload_id)
VALUES (%s, %s, %s, %s, %s, %s, %s)
"""

# DASHBOARD
SQL_COUNT_PATIENTS = "SELECT COUNT(*) FROM patients"
SQL_COUNT_OBS = "SELECT COUNT(*) FROM patient_observations"

# LIST
SQL_LIST_PATIENTS = """
SELECT id, patient_uid, first_name, last_name, age, sex
FROM patients ORDER BY id DESC LIMIT %s OFFSET %s
"""
