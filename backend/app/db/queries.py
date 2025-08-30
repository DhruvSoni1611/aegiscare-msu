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

# PATIENTS (Updated for heart disease dataset)
SQL_GET_PATIENT_BY_UID = "SELECT id FROM patients WHERE patient_uid=%s"
SQL_INSERT_PATIENT = """
INSERT INTO patients (patient_uid, patient_name, phone, age, sex)
VALUES (%s, %s, %s, %s, %s)
"""
SQL_UPDATE_PATIENT = """
UPDATE patients SET patient_name=%s, phone=%s, age=%s, sex=%s, updated_at=NOW() WHERE id=%s
"""
SQL_INSERT_OBSERVATION = """
INSERT INTO patient_observations (patient_id, obs_type, value_num, value_text, unit, observed_at, source_upload_id)
VALUES (%s, %s, %s, %s, %s, %s, %s)
"""

# HEART DISEASE VITAL SIGNS SUMMARY
SQL_INSERT_VITALS_SUMMARY = """
INSERT INTO patient_vitals_summary 
(patient_id, chest_pain_type, resting_bp, cholesterol, fasting_bs, resting_ecg, 
max_heart_rate, exercise_angina, st_depression, st_slope, num_vessels, thalassemia, target, last_updated)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
ON DUPLICATE KEY UPDATE
chest_pain_type=VALUES(chest_pain_type), resting_bp=VALUES(resting_bp), 
cholesterol=VALUES(cholesterol), fasting_bs=VALUES(fasting_bs), 
resting_ecg=VALUES(resting_ecg), max_heart_rate=VALUES(max_heart_rate),
exercise_angina=VALUES(exercise_angina), st_depression=VALUES(st_depression), 
st_slope=VALUES(st_slope), num_vessels=VALUES(num_vessels),
thalassemia=VALUES(thalassemia), target=VALUES(target), last_updated=NOW()
"""

# PATIENT OUTCOMES AND RISK ASSESSMENT
SQL_INSERT_PATIENT_OUTCOMES = """
INSERT INTO patient_outcomes 
(patient_id, readmission, complication, mortality, readmission_risk, complication_risk, mortality_risk, last_updated)
VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
ON DUPLICATE KEY UPDATE
readmission=VALUES(readmission), complication=VALUES(complication), 
mortality=VALUES(mortality), readmission_risk=VALUES(readmission_risk),
complication_risk=VALUES(complication_risk), mortality_risk=VALUES(mortality_risk), last_updated=NOW()
"""

# DASHBOARD - Comprehensive statistics for heart disease
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
    (SELECT 
        CASE 
            WHEN COUNT(*) > 0 THEN 
                ROUND(SUM(CASE WHEN target = 0 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1)
            ELSE 0 
        END 
     FROM patient_vitals_summary) as recovery_rate,
    (SELECT COUNT(*) FROM patient_vitals_summary WHERE target=1) as heart_disease_count,
    (SELECT COUNT(*) FROM patient_vitals_summary WHERE target=0) as healthy_count,
    (SELECT COUNT(*) FROM patient_outcomes WHERE readmission=1) as readmission_count,
    (SELECT COUNT(*) FROM patient_outcomes WHERE complication=1) as complication_count,
    (SELECT COUNT(*) FROM patient_outcomes WHERE mortality=1) as mortality_count
"""

# PATIENT LISTING - Comprehensive patient data with heart disease vitals
SQL_LIST_PATIENTS = """
SELECT p.id, p.patient_uid, p.patient_name, p.age, p.sex, p.phone, p.created_at,
       pvs.chest_pain_type, pvs.resting_bp, pvs.cholesterol, pvs.fasting_bs,
       pvs.resting_ecg, pvs.max_heart_rate, pvs.exercise_angina, pvs.st_depression,
       pvs.st_slope, pvs.num_vessels, pvs.thalassemia, pvs.target
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
ORDER BY observed_at DESC
"""

# PATIENT SEARCH
SQL_SEARCH_PATIENTS = """
SELECT p.id, p.patient_uid, p.patient_name, p.age, p.sex, p.phone, p.created_at,
       pvs.chest_pain_type, pvs.resting_bp, pvs.cholesterol, pvs.fasting_bs,
       pvs.resting_ecg, pvs.max_heart_rate, pvs.exercise_angina, pvs.st_depression,
       pvs.st_slope, pvs.num_vessels, pvs.thalassemia, pvs.target
FROM patients p
LEFT JOIN patient_vitals_summary pvs ON p.id = pvs.patient_id
WHERE p.patient_name LIKE %s OR p.patient_uid LIKE %s
ORDER BY p.id DESC
"""

# VITALS SUMMARY FOR DASHBOARD
SQL_GET_VITALS_SUMMARY = """
SELECT 
    (SELECT COUNT(*) FROM patient_vitals_summary WHERE resting_bp < 120) as bp_normal,
    (SELECT COUNT(*) FROM patient_vitals_summary WHERE resting_bp >= 120 AND resting_bp < 130) as bp_elevated,
    (SELECT COUNT(*) FROM patient_vitals_summary WHERE resting_bp >= 130) as bp_high,
    (SELECT COUNT(*) FROM patient_vitals_summary WHERE max_heart_rate < 60) as hr_low,
    (SELECT COUNT(*) FROM patient_vitals_summary WHERE max_heart_rate >= 60 AND max_heart_rate <= 100) as hr_normal,
    (SELECT COUNT(*) FROM patient_vitals_summary WHERE max_heart_rate > 100) as hr_high,
    (SELECT COUNT(*) FROM patient_vitals_summary WHERE cholesterol < 200) as chol_normal,
    (SELECT COUNT(*) FROM patient_vitals_summary WHERE cholesterol >= 200 AND cholesterol < 240) as chol_borderline,
    (SELECT COUNT(*) FROM patient_vitals_summary WHERE cholesterol >= 240) as chol_high,
    (SELECT COUNT(*) FROM patient_vitals_summary WHERE target = 1) as heart_disease,
    (SELECT COUNT(*) FROM patient_vitals_summary WHERE target = 0) as healthy
"""

# RECENT ACTIVITY
SQL_GET_RECENT_ACTIVITY = """
SELECT p.patient_uid, p.patient_name, p.age, p.sex, pvs.target as heart_disease
FROM patients p
LEFT JOIN patient_vitals_summary pvs ON p.id = pvs.patient_id
ORDER BY p.created_at DESC
LIMIT 10
"""

# PATIENT BY ID FOR ML PREDICTIONS
SQL_GET_PATIENT_BY_ID = """
SELECT p.id, p.patient_uid, p.patient_name, p.age, p.sex, p.phone, p.created_at,
       pvs.chest_pain_type, pvs.resting_bp, pvs.cholesterol, pvs.fasting_bs,
       pvs.resting_ecg, pvs.max_heart_rate, pvs.exercise_angina, pvs.st_depression,
       pvs.st_slope, pvs.num_vessels, pvs.thalassemia, pvs.target
FROM patients p
LEFT JOIN patient_vitals_summary pvs ON p.id = pvs.patient_id
WHERE p.id = %s
"""
