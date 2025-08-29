import pandas as pd
import random
from datetime import datetime, timedelta
from typing import Dict, List


def generate_clinical_notes() -> List[str]:
    templates = [
        "Patient shows stable vitals with minor fluctuations. Continue medication.",
        "Blood pressure elevated during morning rounds.",
        "Patient reports feeling better today.",
        "Oxygen saturation slightly low overnight.",
        "Temperature spike noted at 14:00.",
        "Patient comfortable, pain well controlled.",
        "Heart rate irregular during exercise."
    ]
    return random.sample(templates, random.randint(3, 6))


def generate_sample_patients(n_patients: int = 50) -> Dict:
    patients = {}
    for i in range(n_patients):
        patient_id = f"PT{str(i+1).zfill(4)}"
        dates = pd.date_range(
            start=datetime.now() - timedelta(days=30),
            end=datetime.now(),
            freq='4H'
        )

        base_hr = random.randint(60, 100)
        base_bp_sys = random.randint(110, 140)
        base_bp_dia = random.randint(70, 90)
        base_temp = random.uniform(98.0, 99.5)
        base_o2 = random.randint(95, 100)

        vitals_data = []
        for date in dates:
            vitals_data.append({
                'timestamp': date,
                'heart_rate': max(40, base_hr + random.randint(-10, 15)),
                'blood_pressure_sys': max(80, base_bp_sys + random.randint(-15, 20)),
                'blood_pressure_dia': max(50, base_bp_dia + random.randint(-10, 15)),
                'temperature': max(96.0, base_temp + random.uniform(-1.0, 2.0)),
                'oxygen_saturation': min(100, max(85, base_o2 + random.randint(-5, 3)))
            })

        patients[patient_id] = {
            'name': f"Patient {i+1}",
            'age': random.randint(25, 85),
            'gender': random.choice(['Male', 'Female']),
            'condition': random.choice([
                'Hypertension', 'Diabetes', 'Heart Disease',
                'Respiratory Issue', 'Post-Surgery Recovery'
            ]),
            'vitals': pd.DataFrame(vitals_data),
            'notes': generate_clinical_notes()
        }
    return patients
