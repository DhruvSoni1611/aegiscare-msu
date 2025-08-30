#!/usr/bin/env python3
"""
AegisCare System Startup Script
This script helps you start both the backend and frontend services.
"""

import subprocess
import sys
import os
import time
import signal
import threading
from pathlib import Path


def print_banner():
    """Print the AegisCare banner"""
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║                    🏥 AegisCare System 🏥                    ║
    ║              Heart Disease Analytics Platform                ║
    ╚══════════════════════════════════════════════════════════════╝
    """)


def check_dependencies():
    """Check if required dependencies are installed"""
    print("🔍 Checking dependencies...")

    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ is required")
        return False

    # Check if required packages are installed
    try:
        import fastapi
        import streamlit
        import mysql.connector
        print("✅ All required packages are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing package: {e}")
        print("Please install requirements: pip install -r backend/requirements.txt")
        return False


def start_backend():
    """Start the backend FastAPI server"""
    print("🚀 Starting backend server...")

    backend_dir = Path("backend")
    if not backend_dir.exists():
        print("❌ Backend directory not found")
        return None

    try:
        # Change to backend directory
        os.chdir(backend_dir)

        # Start the server
        process = subprocess.Popen([
            sys.executable, "-m", "uvicorn",
            "app.main:app",
            "--reload",
            "--host", "0.0.0.0",
            "--port", "8000"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # Wait a bit for server to start
        time.sleep(3)

        # Check if server is running
        if process.poll() is None:
            print("✅ Backend server started on http://localhost:8000")
            return process
        else:
            print("❌ Backend server failed to start")
            return None

    except Exception as e:
        print(f"❌ Error starting backend: {e}")
        return None


def start_frontend():
    """Start the frontend Streamlit app"""
    print("🌐 Starting frontend application...")

    frontend_dir = Path("frontend")
    if not frontend_dir.exists():
        print("❌ Frontend directory not found")
        return None

    try:
        # Change to frontend directory
        os.chdir(frontend_dir)

        # Start Streamlit
        process = subprocess.Popen([
            sys.executable, "-m", "streamlit", "run", "Home.py",
            "--server.port", "8501",
            "--server.address", "0.0.0.0"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # Wait a bit for app to start
        time.sleep(5)

        # Check if app is running
        if process.poll() is None:
            print("✅ Frontend application started on http://localhost:8501")
            return process
        else:
            print("❌ Frontend application failed to start")
            return None

    except Exception as e:
        print(f"❌ Error starting frontend: {e}")
        return None


def monitor_processes(processes):
    """Monitor running processes and handle shutdown"""
    try:
        while any(p.poll() is None for p in processes if p):
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Shutting down services...")
        for process in processes:
            if process and process.poll() is None:
                process.terminate()
                process.wait()
        print("✅ All services stopped")


def main():
    """Main startup function"""
    print_banner()

    # Check dependencies
    if not check_dependencies():
        print("❌ Dependency check failed. Please install required packages.")
        sys.exit(1)

    # Store original directory
    original_dir = os.getcwd()

    try:
        # Start backend
        backend_process = start_backend()
        if not backend_process:
            print("❌ Failed to start backend. Exiting.")
            sys.exit(1)

        # Start frontend
        frontend_process = start_frontend()
        if not frontend_process:
            print("❌ Failed to start frontend. Exiting.")
            backend_process.terminate()
            sys.exit(1)

        # Return to original directory
        os.chdir(original_dir)

        print("\n🎉 AegisCare system is now running!")
        print("📊 Dashboard: http://localhost:8501")
        print("🔌 API Docs: http://localhost:8000/docs")
        print("\nPress Ctrl+C to stop all services")

        # Monitor processes
        monitor_processes([backend_process, frontend_process])

    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
    finally:
        # Cleanup
        if 'backend_process' in locals() and backend_process:
            backend_process.terminate()
        if 'frontend_process' in locals() and frontend_process:
            frontend_process.terminate()

        # Return to original directory
        os.chdir(original_dir)
        print("✅ AegisCare system stopped")


if __name__ == "__main__":
    main()
