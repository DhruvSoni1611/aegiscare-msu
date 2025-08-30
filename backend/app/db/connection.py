import os
import pymysql
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Database configuration with fallback values
MYSQL_HOST = os.getenv("MYSQL_HOST", "127.0.0.1")
MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3306"))
# Make sure this matches your workbench database
MYSQL_DB = os.getenv("MYSQL_DB", "aegiscare")
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "Dhruv.1603")


def get_conn():
    """Get database connection with proper error handling"""
    try:
        # First try to connect without specifying database to check if MySQL is running
        conn = pymysql.connect(
            host=MYSQL_HOST,
            port=MYSQL_PORT,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            charset="utf8mb4",
            autocommit=False,
            cursorclass=pymysql.cursors.DictCursor
        )

        # Check if database exists, if not create it
        with conn.cursor() as cur:
            cur.execute(f"CREATE DATABASE IF NOT EXISTS `{MYSQL_DB}`")
            conn.commit()

        # Close the connection without database
        conn.close()

        # Now connect to the specific database
        conn = pymysql.connect(
            host=MYSQL_HOST,
            port=MYSQL_PORT,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DB,
            charset="utf8mb4",
            autocommit=False,
            cursorclass=pymysql.cursors.DictCursor
        )

        return conn

    except pymysql.Error as e:
        print(f"Database connection error: {e}")
        raise Exception(f"Failed to connect to database: {e}")


def init_database():
    """Initialize database tables"""
    try:
        conn = get_conn()
        with conn.cursor() as cur:
            # Read and execute schema
            schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
            with open(schema_path, 'r') as f:
                schema = f.read()
                # Split by semicolon and execute each statement
                statements = schema.split(';')
                for statement in statements:
                    statement = statement.strip()
                    if statement:
                        cur.execute(statement)
            conn.commit()
        conn.close()
        print("Database initialized successfully")
    except Exception as e:
        print(f"Failed to initialize database: {e}")
        raise


def exec_one(sql, params=None):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, params or ())
            conn.commit()
            return cur.lastrowid
    finally:
        conn.close()


def fetch_one(sql, params=None):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, params or ())
            return cur.fetchone()
    finally:
        conn.close()


def fetch_all(sql, params=None):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, params or ())
            return cur.fetchall()
    finally:
        conn.close()


def exec_many(sql, rows):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.executemany(sql, rows)
        conn.commit()
    finally:
        conn.close()
