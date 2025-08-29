import csv
import io
from datetime import datetime
from app.db import repo


def ingest_csv(user_id: int, filename: str, file_bytes: bytes):
    upload_id = repo.start_upload(user_id, filename)
    rows_parsed = rows_loaded = 0
    try:
        text = file_bytes.decode("utf-8", errors="ignore")
        reader = csv.DictReader(io.StringIO(text))
        obs_rows = []
        for row in reader:
            rows_parsed += 1
            uid = row.get("patient_uid") or row.get(
                "id") or f"auto_{upload_id}_{rows_parsed}"
            first = row.get("first_name", "")
            last = row.get("last_name", "")
            age = int(float(row.get("age", "0") or 0))
            sex = (row.get("sex", "O") or "O")[0].upper()
            phone = row.get("contact_phone")

            pid = repo.get_patient_id_by_uid(uid)
            if not pid:
                pid = repo.insert_patient(uid, first, last, age, sex, phone)

            now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
            for key in ["bp_sys", "bp_dia", "cholesterol", "hr", "bmi"]:
                val = row.get(key)
                if val not in (None, "", "NaN"):
                    obs_rows.append(
                        (pid, key.upper(), float(val), None, "", now, upload_id))

            rows_loaded += 1

        if obs_rows:
            repo.insert_observations(obs_rows)
        repo.complete_upload(upload_id, rows_parsed, rows_loaded)
        return {"upload_id": upload_id, "rows_parsed": rows_parsed, "rows_loaded": rows_loaded}
    except Exception as e:
        repo.fail_upload(upload_id, str(e))
        raise
