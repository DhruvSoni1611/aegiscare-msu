import random
from backend.api.routers.uploads import PatientInput, PredictionResponse, Explanation
from ml import nlp


def predict(data: PatientInput) -> PredictionResponse:
    # placeholder random risk score
    score = random.uniform(0, 100)
    label = "low" if score < 30 else ("medium" if score < 70 else "high")
    explanations = [
        Explanation(feature="glucose", direction="+", contribution=0.2),
        Explanation(feature="age", direction="+", contribution=0.15)
    ]
    recos = ["Follow-up in 7 days", "Lifestyle counseling"]
    return PredictionResponse(
        risk_score=round(score, 2),
        label=label,
        explanations=explanations,
        recommendations=recos,
        model_meta={"version": "v0.1",
                    "auroc": "0.80", "trained": "2025-08-28"}
    )


def summarize_notes(text: str) -> str:
    return nlp.summarize_notes(text)
