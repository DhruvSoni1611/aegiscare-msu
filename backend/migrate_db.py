#!/usr/bin/env python3
"""
Database Migration Script for AegisCare
This script updates the existing database schema to match the new heart disease structure.
"""

import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def migrate_database():
    """Migrate the existing database to the new heart disease schema"""
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
            print("🔍 Checking current database structure...")

            # Check if patient_vitals_summary table exists and get its structure
            cursor.execute("SHOW TABLES LIKE 'patient_vitals_summary'")
            table_exists = cursor.fetchone()

            if not table_exists:
                print(
                    "❌ Table 'patient_vitals_summary' does not exist. Please run init_db.py first.")
                return

            # Get current table structure
            cursor.execute("DESCRIBE patient_vitals_summary")
            columns = cursor.fetchall()
            column_names = [col[0] for col in columns]

            print(f"📋 Current columns: {column_names}")

            # Check if target column exists
            if 'target' not in column_names:
                print("🔄 Adding missing columns to patient_vitals_summary table...")

                # Add missing columns
                missing_columns = [
                    "ADD COLUMN chest_pain_type INT NULL COMMENT '0-3: typical angina, atypical angina, non-anginal pain, asymptomatic'",
                    "ADD COLUMN resting_bp INT NULL COMMENT 'Resting blood pressure (mmHg)'",
                    "ADD COLUMN cholesterol INT NULL COMMENT 'Serum cholesterol (mg/dl)'",
                    "ADD COLUMN fasting_bs INT NULL COMMENT 'Fasting blood sugar > 120 mg/dl (1=true, 0=false)'",
                    "ADD COLUMN resting_ecg INT NULL COMMENT 'Resting ECG results (0-2)'",
                    "ADD COLUMN max_heart_rate INT NULL COMMENT 'Maximum heart rate achieved'",
                    "ADD COLUMN exercise_angina INT NULL COMMENT 'Exercise induced angina (1=yes, 0=no)'",
                    "ADD COLUMN st_depression DECIMAL(4,2) NULL COMMENT 'ST depression induced by exercise'",
                    "ADD COLUMN st_slope INT NULL COMMENT 'Slope of peak exercise ST segment (0-2)'",
                    "ADD COLUMN num_vessels INT NULL COMMENT 'Number of major vessels colored by fluoroscopy'",
                    "ADD COLUMN thalassemia INT NULL COMMENT 'Thalassemia (0-3)'",
                    "ADD COLUMN target INT NULL COMMENT 'Heart disease (1=yes, 0=no)'"
                ]

                for column_def in missing_columns:
                    try:
                        sql = f"ALTER TABLE patient_vitals_summary {column_def}"
                        cursor.execute(sql)
                        print(f"✅ Added column: {column_def.split()[2]}")
                    except Error as e:
                        if "Duplicate column name" in str(e):
                            print(
                                f"ℹ️  Column already exists: {column_def.split()[2]}")
                        else:
                            print(
                                f"⚠️  Warning adding column {column_def.split()[2]}: {e}")

                # Update patients table if needed
                cursor.execute("DESCRIBE patients")
                patient_columns = cursor.fetchall()
                patient_column_names = [col[0] for col in patient_columns]

                if 'patient_name' not in patient_column_names:
                    print("🔄 Updating patients table structure...")

                    # Check if old columns exist and rename them
                    if 'first_name' in patient_column_names and 'last_name' in patient_column_names:
                        try:
                            cursor.execute(
                                "ALTER TABLE patients ADD COLUMN patient_name VARCHAR(255) NULL AFTER patient_uid")
                            cursor.execute(
                                "UPDATE patients SET patient_name = CONCAT(first_name, ' ', last_name) WHERE patient_name IS NULL")
                            print("✅ Added patient_name column")
                        except Error as e:
                            print(f"⚠️  Warning: {e}")

                    if 'contact_phone' in patient_column_names:
                        try:
                            cursor.execute(
                                "ALTER TABLE patients CHANGE contact_phone phone VARCHAR(32) NULL")
                            print("✅ Renamed contact_phone to phone")
                        except Error as e:
                            print(f"⚠️  Warning: {e}")

                # Create indexes if they don't exist
                print("🔧 Creating indexes...")
                indexes_to_create = [
                    ("idx_patients_age",
                     "CREATE INDEX idx_patients_age ON patients(age)"),
                    ("idx_patients_sex",
                     "CREATE INDEX idx_patients_sex ON patients(sex)"),
                    ("idx_vitals_target",
                     "CREATE INDEX idx_vitals_target ON patient_vitals_summary(target)"),
                    ("idx_vitals_chest_pain",
                     "CREATE INDEX idx_vitals_chest_pain ON patient_vitals_summary(chest_pain_type)"),
                    ("idx_vitals_bp", "CREATE INDEX idx_vitals_bp ON patient_vitals_summary(resting_bp)"),
                    ("idx_vitals_cholesterol",
                     "CREATE INDEX idx_vitals_cholesterol ON patient_vitals_summary(cholesterol)"),
                    ("idx_vitals_heart_rate",
                     "CREATE INDEX idx_vitals_heart_rate ON patient_vitals_summary(max_heart_rate)")
                ]

                for index_name, index_sql in indexes_to_create:
                    try:
                        cursor.execute(index_sql)
                        print(f"✅ Created index: {index_name}")
                    except Error as e:
                        if "Duplicate key name" in str(e):
                            print(f"ℹ️  Index already exists: {index_name}")
                        else:
                            print(
                                f"⚠️  Warning creating index {index_name}: {e}")

                connection.commit()
                print("✅ Database migration completed successfully!")

            else:
                print("✅ Database schema is already up to date!")

            # Verify final structure
            print("\n📋 Final table structure:")
            cursor.execute("DESCRIBE patient_vitals_summary")
            final_columns = cursor.fetchall()
            for col in final_columns:
                print(f"  - {col[0]}: {col[1]} ({col[2]})")

    except Error as e:
        print(f"❌ Error during migration: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("✅ Database connection closed.")


if __name__ == "__main__":
    print("🚀 Starting AegisCare Database Migration...")
    migrate_database()
    print("✨ Database migration complete!")
