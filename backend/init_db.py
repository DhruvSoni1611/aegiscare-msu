#!/usr/bin/env python3
"""
Initialize the database with the new heart disease schema.
This script will create all necessary tables and indexes.
"""

import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def init_database():
    """Initialize the database with the new schema"""
    try:
        # Database connection parameters
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD', ''),
            database=os.getenv('DB_NAME', 'aegiscare')
        )

        if connection.is_connected():
            cursor = connection.cursor()

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
                        if "already exists" not in str(e).lower():
                            print(f"⚠️  Warning: {e}")
                        else:
                            print(
                                f"ℹ️  Table already exists: {statement[:50]}...")

            # Commit changes
            connection.commit()
            print("✅ Database schema initialized successfully!")

            # Create a test user for development
            try:
                cursor.execute("""
                    INSERT INTO users (email, full_name, password_hash, role) 
                    VALUES ('admin@aegiscare.com', 'Admin User', 
                           '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/HS.i8mG', 'doctor')
                    ON DUPLICATE KEY UPDATE email=email
                """)
                connection.commit()
                print("✅ Test user created/updated: admin@aegiscare.com / password123")
            except Error as e:
                print(f"ℹ️  Test user already exists or error: {e}")

    except Error as e:
        print(f"❌ Error connecting to database: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("✅ Database connection closed.")


if __name__ == "__main__":
    print("🚀 Initializing AegisCare Database...")
    init_database()
    print("✨ Database initialization complete!")
