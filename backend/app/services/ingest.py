import csv
import io
from datetime import datetime
from app.db import repo


def ingest_csv(user_id: int, filename: str, file_bytes: bytes):
    """
    Comprehensive CSV ingestion for heart disease dataset.
    Processes patient data once and stores it efficiently.
    Creates both detailed observations and summary vitals for dashboard performance.
    """
    upload_id = repo.start_upload(user_id, filename)
    rows_parsed = rows_loaded = 0

    try:
        text = file_bytes.decode("utf-8", errors="ignore")
        reader = csv.DictReader(io.StringIO(text))

        # Store all observations for detailed analysis
        obs_rows = []
        # Store vitals summaries for dashboard performance
        vitals_summaries = {}

        for row in reader:
            rows_parsed += 1

            # Extract patient identification
            patient_id = row.get(
                "patient_id", f"auto_{upload_id}_{rows_parsed}")
            patient_name = row.get("patient_name", "").strip()
            phone = row.get("phone", "").strip()

            # Extract basic patient info
            try:
                age = int(float(row.get("age", "0") or 0))
            except (ValueError, TypeError):
                age = 0

            # Convert sex from numeric to character (1=F, 0=M based on dataset)
            sex_num = row.get("sex", "0")
            if sex_num == "1":
                sex = "F"
            elif sex_num == "0":
                sex = "M"
            else:
                sex = "O"

            # Get or create patient
            pid = repo.get_patient_id_by_uid(patient_id)
            if not pid:
                pid = repo.insert_patient(
                    patient_id, patient_name, phone, age, sex)
            else:
                # Update existing patient with new information
                repo.update_patient(pid, patient_name, phone, age, sex)

            # Process heart disease specific vital signs and observations
            now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

            # Define vital signs mapping for heart disease dataset
            vital_signs = {
                "chest pain type": "CHEST_PAIN_TYPE",
                "Resting blood pressure": "RESTING_BP",
                "Serum cholesterol level (mg/dl).": "CHOLESTEROL",
                "Fasting Blood Sugar": "FASTING_BS",
                "Resting Electrocardiogram Results": "RESTING_ECG",
                "Maximum Heart Rate Achieved": "MAX_HEART_RATE",
                "Exercise-Induced Angina": "EXERCISE_ANGINA",
                "ST Depression Induced by Exercise": "ST_DEPRESSION",
                "Slope of the Peak Exercise ST Segment": "ST_SLOPE",
                "Number of Major Vessels Colored by Fluoroscopy": "NUM_VESSELS",
                "Thalassemia": "THALASSEMIA",
                "target": "HEART_DISEASE"
            }

            # Collect observations and prepare vitals summary
            patient_vitals = {
                'chest_pain_type': None,
                'resting_bp': None,
                'cholesterol': None,
                'fasting_bs': None,
                'resting_ecg': None,
                'max_heart_rate': None,
                'exercise_angina': None,
                'st_depression': None,
                'st_slope': None,
                'num_vessels': None,
                'thalassemia': None,
                'target': None
            }

            for csv_key, obs_type in vital_signs.items():
                val = row.get(csv_key)
                if val not in (None, "", "NaN", "nan", "-1"):
                    try:
                        # Handle special cases
                        if csv_key == "Fasting Blood Sugar":
                            # Convert to binary (1 if > 120, 0 otherwise)
                            num_val = 1 if float(val) > 120 else 0
                        else:
                            num_val = float(val)

                        # Store observation
                        obs_rows.append(
                            (pid, obs_type, num_val, None, "", now, upload_id))

                        # Update vitals summary for dashboard
                        if csv_key == "chest pain type":
                            patient_vitals['chest_pain_type'] = int(num_val)
                        elif csv_key == "Resting blood pressure":
                            patient_vitals['resting_bp'] = int(num_val)
                        elif csv_key == "Serum cholesterol level (mg/dl).":
                            patient_vitals['cholesterol'] = int(num_val)
                        elif csv_key == "Fasting Blood Sugar":
                            patient_vitals['fasting_bs'] = int(num_val)
                        elif csv_key == "Resting Electrocardiogram Results":
                            patient_vitals['resting_ecg'] = int(num_val)
                        elif csv_key == "Maximum Heart Rate Achieved":
                            patient_vitals['max_heart_rate'] = int(num_val)
                        elif csv_key == "Exercise-Induced Angina":
                            patient_vitals['exercise_angina'] = int(num_val)
                        elif csv_key == "ST Depression Induced by Exercise":
                            patient_vitals['st_depression'] = round(num_val, 2)
                        elif csv_key == "Slope of the Peak Exercise ST Segment":
                            patient_vitals['st_slope'] = int(num_val)
                        elif csv_key == "Number of Major Vessels Colored by Fluoroscopy":
                            patient_vitals['num_vessels'] = int(num_val)
                        elif csv_key == "Thalassemia":
                            patient_vitals['thalassemia'] = int(num_val)
                        elif csv_key == "target":
                            patient_vitals['target'] = int(num_val)

                    except (ValueError, TypeError):
                        # Store as text if numeric conversion fails
                        obs_rows.append(
                            (pid, obs_type, None, str(val), "", now, upload_id))

            # Store vitals summary for this patient
            vitals_summaries[pid] = patient_vitals
            rows_loaded += 1

        # Insert all observations
        if obs_rows:
            repo.insert_observations(obs_rows)

        # Insert vitals summaries for dashboard performance
        for pid, vitals in vitals_summaries.items():
            repo.insert_vitals_summary(
                pid,
                vitals['chest_pain_type'],
                vitals['resting_bp'],
                vitals['cholesterol'],
                vitals['fasting_bs'],
                vitals['resting_ecg'],
                vitals['max_heart_rate'],
                vitals['exercise_angina'],
                vitals['st_depression'],
                vitals['st_slope'],
                vitals['num_vessels'],
                vitals['thalassemia'],
                vitals['target']
            )

        repo.complete_upload(upload_id, rows_parsed, rows_loaded)

        return {
            "upload_id": upload_id,
            "rows_parsed": rows_parsed,
            "rows_loaded": rows_loaded,
            "patients_processed": len(vitals_summaries)
        }

    except Exception as e:
        repo.fail_upload(upload_id, str(e))
        raise


def _safe_float(value):
    """Safely convert value to float, return None if conversion fails"""
    if value is None or value == "" or value == "NaN" or value == "nan" or value == "-1":
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return None
