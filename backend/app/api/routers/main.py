from fastapi import FastAPI
from backend.api.routers.uploads import PatientInput, PredictionResponse
from service import predict, summarize_notes


app = FastAPI(title="AegisCare API", version="0.1")


@app.post("/predict", response_model=PredictionResponse)
def predict_patient(data: PatientInput):
    return predict(data)


@app.post("/summarize")
def summarize_notes_endpoint(text: str):
    return {"summary": summarize_notes(text)}
