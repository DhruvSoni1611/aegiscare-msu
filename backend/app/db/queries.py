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

# PATIENTS (Updated for comprehensive data)
SQL_GET_PATIENT_BY_UID = "SELECT id FROM patients WHERE patient_uid=%s"
SQL_INSERT_PATIENT = """
INSERT INTO patients (patient_uid, first_name, last_name, age, sex, contact_phone, height_cm, weight_kg, bmi)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
"""
SQL_UPDATE_PATIENT = """
UPDATE patients SET first_name=%s, last_name=%s, age=%s, sex=%s, contact_phone=%s, 
height_cm=%s, weight_kg=%s, bmi=%s, updated_at=NOW() WHERE id=%s
"""
SQL_INSERT_OBSERVATION = """
INSERT INTO patient_observations (patient_id, obs_type, value_num, value_text, unit, observed_at, source_upload_id)
VALUES (%s, %s, %s, %s, %s, %s, %s)
"""

# PATIENT VITALS SUMMARY
SQL_INSERT_VITALS_SUMMARY = """
INSERT INTO patient_vitals_summary 
(patient_id, bp_systolic, bp_diastolic, heart_rate, temperature, oxygen_saturation, 
respiratory_rate, cholesterol, glucose, bmi, last_updated)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
ON DUPLICATE KEY UPDATE
bp_systolic=VALUES(bp_systolic), bp_diastolic=VALUES(bp_diastolic), 
heart_rate=VALUES(heart_rate), temperature=VALUES(temperature), 
oxygen_saturation=VALUES(oxygen_saturation), respiratory_rate=VALUES(respiratory_rate),
cholesterol=VALUES(cholesterol), glucose=VALUES(glucose), bmi=VALUES(bmi), 
last_updated=NOW()
"""

# DASHBOARD - Comprehensive statistics
SQL_COUNT_PATIENTS = "SELECT COUNT(*) as count FROM patients"
SQL_COUNT_OBS = "SELECT COUNT(*) as count FROM patient_observations"
SQL_COUNT_UPLOADS = "SELECT COUNT(*) as count FROM csv_uploads WHERE status='completed'"
SQL_GET_DASHBOARD_STATS = """
SELECT 
    (SELECT COUNT(*) FROM patients) as total_patients,
    (SELECT COUNT(*) FROM patient_observations) as total_observations,
    (SELECT COUNT(*) FROM csv_uploads WHERE status='completed') as total_uploads,
    (SELECT COUNT(*) FROM patients WHERE sex='M') as male_patients,
    (SELECT COUNT(*) FROM patients WHERE sex='F') as female_patients,
    (SELECT AVG(age) FROM patients) as avg_age,
    (SELECT AVG(bmi) FROM patients WHERE bmi IS NOT NULL) as avg_bmi
"""

# PATIENT LISTING - Comprehensive patient data
SQL_LIST_PATIENTS = """
SELECT p.id, p.patient_uid, p.first_name, p.last_name, p.age, p.sex, 
       p.contact_phone, p.height_cm, p.weight_kg, p.bmi, p.created_at,
       pvs.bp_systolic, pvs.bp_diastolic, pvs.heart_rate, pvs.temperature,
       pvs.oxygen_saturation, pvs.respiratory_rate, pvs.cholesterol, pvs.glucose
FROM patients p
LEFT JOIN patient_vitals_summary pvs ON p.id = pvs.patient_id
ORDER BY p.id DESC LIMIT %s OFFSET %s
"""

# PATIENT VITALS TRENDS - Get observations over time for specific patient
SQL_GET_PATIENT_VITALS = """
SELECT obs_type, value_num, value_text, unit, observed_at
FROM patient_observations 
WHERE patient_id = %s 
ORDER BY observed_at DESC
"""

# PATIENT VITALS BY TYPE - Get specific vital signs over time
SQL_GET_VITALS_BY_TYPE = """
SELECT value_num, observed_at
FROM patient_observations 
WHERE patient_id = %s AND obs_type = %s
ORDER BY observed_at ASC
"""

# PATIENT DETAILS - Get comprehensive patient information
SQL_GET_PATIENT_DETAILS = """
SELECT p.*, pvs.*
FROM patients p
LEFT JOIN patient_vitals_summary pvs ON p.id = pvs.patient_id
WHERE p.id = %s
"""

# SEARCH PATIENTS
SQL_SEARCH_PATIENTS = """
SELECT p.id, p.patient_uid, p.first_name, p.last_name, p.age, p.sex
FROM patients p
WHERE p.first_name LIKE %s OR p.last_name LIKE %s OR p.patient_uid LIKE %s
ORDER BY p.last_name, p.first_name
LIMIT %s
"""
