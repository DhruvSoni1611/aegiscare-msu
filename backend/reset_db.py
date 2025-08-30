#!/usr/bin/env python3
"""
Database Reset Script for AegisCare
This script completely drops and recreates the database with the new schema.
WARNING: This will delete all existing data!
"""

import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def reset_database():
    """Completely reset the database with the new schema"""
    try:
        # Database connection parameters (without database name for initial connection)
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD', '')
        )

        if connection.is_connected():
            cursor = connection.cursor()
            db_name = os.getenv('DB_NAME', 'aegiscare')

            print(f"🗑️  Dropping database '{db_name}' if it exists...")
            try:
                cursor.execute(f"DROP DATABASE IF EXISTS {db_name}")
                print(f"✅ Dropped database '{db_name}'")
            except Error as e:
                print(f"⚠️  Warning dropping database: {e}")

            print(f"🆕 Creating new database '{db_name}'...")
            try:
                cursor.execute(f"CREATE DATABASE {db_name}")
                print(f"✅ Created database '{db_name}'")
            except Error as e:
                print(f"❌ Error creating database: {e}")
                return

            # Close connection and reconnect to the new database
            cursor.close()
            connection.close()

            # Reconnect to the new database
            connection = mysql.connector.connect(
                host=os.getenv('DB_HOST', 'localhost'),
                user=os.getenv('DB_USER', 'root'),
                password=os.getenv('DB_PASSWORD', ''),
                database=db_name
            )

            if connection.is_connected():
                cursor = connection.cursor()

                print("📋 Creating new tables with heart disease schema...")

                # Read and execute the schema file
                schema_file = os.path.join(os.path.dirname(
                    __file__), 'app', 'db', 'schema.sql')

                with open(schema_file, 'r') as file:
                    schema_sql = file.read()

                # Split SQL statements and execute them
                statements = schema_sql.split(';')

                for statement in statements:
                    statement = statement.strip()
                    if statement:
                        try:
                            cursor.execute(statement)
                            print(f"✅ Executed: {statement[:50]}...")
                        except Error as e:
                            print(f"⚠️  Warning: {e}")

                # Create a test user for development
                print("👤 Creating test user...")
                try:
                    cursor.execute("""
                        INSERT INTO users (email, full_name, password_hash, role) 
                        VALUES ('admin@aegiscare.com', 'Admin User', 
                               '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/HS.i8mG', 'doctor')
                    """)
                    print("✅ Test user created: admin@aegiscare.com / password123")
                except Error as e:
                    print(f"⚠️  Warning creating test user: {e}")

                # Commit changes
                connection.commit()
                print("✅ Database reset completed successfully!")

                # Verify table structure
                print("\n📋 Final table structure:")
                cursor.execute("SHOW TABLES")
                tables = cursor.fetchall()
                for table in tables:
                    print(f"  - {table[0]}")

                cursor.execute("DESCRIBE patient_vitals_summary")
                columns = cursor.fetchall()
                print(f"\n📋 patient_vitals_summary columns:")
                for col in columns:
                    print(f"  - {col[0]}: {col[1]} ({col[2]})")

            else:
                print("❌ Failed to connect to new database")

    except Error as e:
        print(f"❌ Error during database reset: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("✅ Database connection closed.")


if __name__ == "__main__":
    print("🚨 WARNING: This will delete all existing data!")
    response = input("Are you sure you want to continue? (yes/no): ")

    if response.lower() in ['yes', 'y']:
        print("🚀 Starting AegisCare Database Reset...")
        reset_database()
        print("✨ Database reset complete!")
    else:
        print("❌ Database reset cancelled.")
