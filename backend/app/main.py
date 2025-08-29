from fastapi import FastAPI
from app.api.routers import auth, uploads, dashboard, patients

app = FastAPI(title="AegisCare API")
app.include_router(auth.router)
app.include_router(uploads.router)
app.include_router(dashboard.router)
app.include_router(patients.router)
