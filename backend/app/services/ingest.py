import csv
import io
from datetime import datetime
from app.db import repo


def ingest_csv(user_id: int, filename: str, file_bytes: bytes):
    """
    Comprehensive CSV ingestion that processes patient data once and stores it efficiently.
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
            uid = row.get("patient_uid") or row.get(
                "id") or f"auto_{upload_id}_{rows_parsed}"
            first = row.get("first_name", "").strip()
            last = row.get("last_name", "").strip()

            # Extract basic patient info
            try:
                age = int(float(row.get("age", "0") or 0))
            except (ValueError, TypeError):
                age = 0

            sex = (row.get("sex", "O") or "O")[0].upper()
            if sex not in ['M', 'F', 'O']:
                sex = 'O'

            phone = row.get("contact_phone", "").strip()

            # Extract measurements
            height = _safe_float(row.get("height_cm") or row.get("height"))
            weight = _safe_float(row.get("weight_kg") or row.get("weight"))
            bmi = _safe_float(row.get("bmi"))

            # Calculate BMI if not provided but height and weight are available
            if bmi is None and height and weight and height > 0:
                bmi = round(weight / ((height / 100) ** 2), 2)

            # Get or create patient
            pid = repo.get_patient_id_by_uid(uid)
            if not pid:
                pid = repo.insert_patient(
                    uid, first, last, age, sex, phone, height, weight, bmi)
            else:
                # Update existing patient with new information
                repo.update_patient(pid, first, last, age,
                                    sex, phone, height, weight, bmi)

            # Process vital signs and observations
            now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

            # Define vital signs mapping
            vital_signs = {
                "bp_sys": "BP_SYSTOLIC",
                "bp_dia": "BP_DIASTOLIC",
                "cholesterol": "CHOLESTEROL",
                "hr": "HEART_RATE",
                "bmi": "BMI",
                "glucose": "GLUCOSE",
                "temperature": "TEMPERATURE",
                "oxygen_saturation": "OXYGEN_SATURATION",
                "respiratory_rate": "RESPIRATORY_RATE",
                "weight": "WEIGHT",
                "height": "HEIGHT"
            }

            # Collect observations and prepare vitals summary
            patient_vitals = {
                'bp_systolic': None,
                'bp_diastolic': None,
                'heart_rate': None,
                'temperature': None,
                'oxygen_saturation': None,
                'respiratory_rate': None,
                'cholesterol': None,
                'glucose': None,
                'bmi': bmi
            }

            for csv_key, obs_type in vital_signs.items():
                val = row.get(csv_key)
                if val not in (None, "", "NaN", "nan"):
                    try:
                        num_val = float(val)
                        obs_rows.append(
                            (pid, obs_type, num_val, None, "", now, upload_id))

                        # Update vitals summary for dashboard
                        if csv_key == "bp_sys":
                            patient_vitals['bp_systolic'] = int(num_val)
                        elif csv_key == "bp_dia":
                            patient_vitals['bp_diastolic'] = int(num_val)
                        elif csv_key == "hr":
                            patient_vitals['heart_rate'] = int(num_val)
                        elif csv_key == "temperature":
                            patient_vitals['temperature'] = round(num_val, 1)
                        elif csv_key == "oxygen_saturation":
                            patient_vitals['oxygen_saturation'] = round(
                                num_val, 1)
                        elif csv_key == "respiratory_rate":
                            patient_vitals['respiratory_rate'] = int(num_val)
                        elif csv_key == "cholesterol":
                            patient_vitals['cholesterol'] = round(num_val, 2)
                        elif csv_key == "glucose":
                            patient_vitals['glucose'] = round(num_val, 2)

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
                vitals['bp_systolic'],
                vitals['bp_diastolic'],
                vitals['heart_rate'],
                vitals['temperature'],
                vitals['oxygen_saturation'],
                vitals['respiratory_rate'],
                vitals['cholesterol'],
                vitals['glucose'],
                vitals['bmi']
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
    if value is None or value == "" or value == "NaN" or value == "nan":
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return None
