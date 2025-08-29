#!/usr/bin/env python3
"""
Database initialization script for AegisCare
Run this script to set up the database and tables
"""

from app.db.connection import init_database
import sys
import os

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))


def main():
    print("🚀 Initializing AegisCare database...")
    try:
        init_database()
        print("✅ Database initialized successfully!")
        print("📊 Tables created:")
        print("   - users")
        print("   - sessions")
        print("   - csv_uploads")
        print("   - patients")
        print("   - patient_observations")
    except Exception as e:
        print(f"❌ Failed to initialize database: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
