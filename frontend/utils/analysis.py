import numpy as np
import pandas as pd
from typing import Dict


def analyze_vitals_trends(vitals_df: pd.DataFrame) -> Dict:
    latest = vitals_df.iloc[-1]
    previous = vitals_df.iloc[-24:].mean()

    trends = {}
    for vital in ['heart_rate', 'blood_pressure_sys', 'blood_pressure_dia', 'temperature', 'oxygen_saturation']:
        current_val = latest[vital]
        avg_val = previous[vital]

        if vital == 'heart_rate':
            status = 'HIGH' if current_val > 100 else 'LOW' if current_val < 60 else 'NORMAL'
        elif vital == 'blood_pressure_sys':
            status = 'HIGH' if current_val > 140 else 'LOW' if current_val < 90 else 'NORMAL'
        elif vital == 'blood_pressure_dia':
            status = 'HIGH' if current_val > 90 else 'LOW' if current_val < 60 else 'NORMAL'
        elif vital == 'temperature':
            status = 'HIGH' if current_val > 100.4 else 'LOW' if current_val < 97.0 else 'NORMAL'
        else:
            status = 'LOW' if current_val < 95 else 'NORMAL'

        trend_direction = 'UP' if current_val > avg_val else 'DOWN' if current_val < avg_val else 'STABLE'

        trends[vital] = {
            'current': current_val,
            'average': avg_val,
            'status': status,
            'trend': trend_direction
        }
    return trends


def simulate_intervention_impact(vitals_df: pd.DataFrame, intervention: str, magnitude: float) -> pd.DataFrame:
    simulated_df = vitals_df.copy()
    if intervention == "Blood Pressure Medication":
        simulated_df['blood_pressure_sys'] -= magnitude
        simulated_df['blood_pressure_dia'] -= magnitude * 0.7
    elif intervention == "Beta Blocker":
        simulated_df['heart_rate'] -= magnitude
        simulated_df['blood_pressure_sys'] -= magnitude * 0.5
    elif intervention == "Oxygen Therapy":
        simulated_df['oxygen_saturation'] = np.minimum(
            100, simulated_df['oxygen_saturation'] + magnitude)
    elif intervention == "Fever Reducer":
        simulated_df['temperature'] -= magnitude
    return simulated_df
