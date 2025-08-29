# AegisCare – Patient Risk & Outcome Prediction

ML-powered predictive analytics for healthcare data, with explainable AI insights and a doctor-facing dashboard.

# docker-compose.yml

version: '3.8'
services:
api:
build: ./api
ports:

- "8000:8000"
  app:
  build: ./app
  ports:
- "8501:8501"
  depends_on:
- api

---

## 🚀 Setup (Local Dev)

```bash
# clone
git clone https://github.com/<you>/aegiscare.git
cd aegiscare

# setup virtual env
python -m venv .venv
source .venv/bin/activate   # (Windows: .venv\Scripts\activate)

# install deps
pip install -r api/requirements.txt
pip install -r app/requirements.txt
```
