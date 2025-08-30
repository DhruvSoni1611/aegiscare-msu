#!/usr/bin/env python3
"""
Quick Fix Script for AegisCare
This script immediately fixes the 'target column doesn't exist' error.
"""

import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def quick_fix():
    """Quick fix for the missing target column error"""
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
            print("🔧 Applying quick fix for missing 'target' column...")

            # Check if target column exists
            cursor.execute(
                "SHOW COLUMNS FROM patient_vitals_summary LIKE 'target'")
            column_exists = cursor.fetchone()

            if not column_exists:
                print("➕ Adding missing 'target' column...")
                try:
                    cursor.execute("""
                        ALTER TABLE patient_vitals_summary 
                        ADD COLUMN target INT NULL COMMENT 'Heart disease (1=yes, 0=no)'
                    """)
                    connection.commit()
                    print("✅ Successfully added 'target' column!")
                except Error as e:
                    print(f"❌ Error adding column: {e}")
                    return False
            else:
                print("✅ 'target' column already exists!")

            # Verify the fix
            cursor.execute("DESCRIBE patient_vitals_summary")
            columns = cursor.fetchall()
            target_column = None

            for col in columns:
                if col[0] == 'target':
                    target_column = col
                    break

            if target_column:
                print(
                    f"✅ Column 'target' verified: {target_column[1]} ({target_column[2]})")
                print("🎉 Quick fix applied successfully! The backend should now work.")
                return True
            else:
                print("❌ Column 'target' still not found after fix attempt.")
                return False

        else:
            print("❌ Could not connect to database")
            return False

    except Error as e:
        print(f"❌ Database error: {e}")
        return False
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


if __name__ == "__main__":
    print("🚀 AegisCare Quick Fix - Resolving 'target column' error...")
    success = quick_fix()

    if success:
        print("\n✨ Quick fix completed successfully!")
        print("🔄 You can now restart your backend server.")
    else:
        print("\n❌ Quick fix failed. Please try the migration script instead:")
        print("   python migrate_db.py")
