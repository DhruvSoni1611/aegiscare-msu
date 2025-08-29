#!/bin/bash
# scripts/setup.sh

set -e  # exit if any command fails

echo "🔧 Setting up AegisCare environment..."

# Load environment variables
if [ -f .env ]; then
  export $(cat .env | xargs)
else
  echo "⚠️  .env file not found. Please create one from .env.example"
  exit 1
fi

# Create Python virtual environment
if [ ! -d "venv" ]; then
  echo "📦 Creating virtual environment..."
  python3 -m venv venv
fi

source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install requirements
echo "📥 Installing backend dependencies..."
pip install -r backend/requirements.txt

echo "📥 Installing frontend dependencies..."
pip install -r frontend/requirements.txt

# Run DB migrations
echo "🗄️ Running Alembic migrations..."
cd backend
alembic upgrade head
cd ..

# Start services
echo "🚀 Starting backend (FastAPI) and frontend (Streamlit)..."
# backend runs on 8000, frontend on 8501
gnome-terminal -- bash -c "cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
gnome-terminal -- bash -c "cd frontend && streamlit run app.py --server.port=8501"

echo "✅ Setup complete! Visit:"
echo "   - Backend API: http://localhost:8000/docs"
echo "   - Frontend:    http://localhost:8501"
