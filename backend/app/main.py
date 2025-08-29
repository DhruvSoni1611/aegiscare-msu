from fastapi import FastAPI
from app.api.routers import auth, uploads, dashboard, patients
from app.db.connection import init_database

app = FastAPI(title="AegisCare API")


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    try:
        init_database()
        print("✅ Database initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize database: {e}")
        # Don't crash the app, just log the error

app.include_router(auth.router)
app.include_router(uploads.router)
app.include_router(dashboard.router)
app.include_router(patients.router)
