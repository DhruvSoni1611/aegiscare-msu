#!/usr/bin/env python3
"""
Test script to verify database connection and basic functionality
"""

import sys
import os

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))


def test_database_connection():
    """Test basic database connectivity"""
    try:
        from app.db.connection import get_conn, init_database

        print("🔍 Testing database connection...")

        # Test connection
        conn = get_conn()
        print("✅ Database connection successful!")

        # Test basic query
        with conn.cursor() as cur:
            cur.execute("SELECT VERSION() as version")
            result = cur.fetchone()
            print(f"📊 Connected to MySQL {result['version']}")

        conn.close()

        # Test database initialization
        print("🔧 Testing database initialization...")
        init_database()
        print("✅ Database initialization successful!")

        return True

    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False


def test_repository_functions():
    """Test basic repository functions"""
    try:
        from app.db import repo

        print("🔍 Testing repository functions...")

        # Test dashboard stats
        stats = repo.get_dashboard_stats()
        print(f"📊 Dashboard stats: {stats}")

        # Test patient count
        patient_count = repo.count_patients()
        print(f"👥 Patient count: {patient_count}")

        print("✅ Repository functions working!")
        return True

    except Exception as e:
        print(f"❌ Repository test failed: {e}")
        return False


def main():
    """Run all tests"""
    print("🚀 Starting AegisCare Backend Tests...")
    print("=" * 50)

    # Test database connection
    db_ok = test_database_connection()

    if db_ok:
        # Test repository functions
        repo_ok = test_repository_functions()

        if repo_ok:
            print("\n🎉 All tests passed! Backend is ready.")
        else:
            print("\n⚠️ Database connection OK, but repository functions failed.")
    else:
        print("\n❌ Database connection failed. Check your MySQL setup.")

    print("=" * 50)


if __name__ == "__main__":
    main()
