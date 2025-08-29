import os
import pymysql
from dotenv import load_dotenv

load_dotenv()

MYSQL_HOST = os.getenv("MYSQL_HOST", "127.0.0.1")
MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3306"))
MYSQL_DB = os.getenv("MYSQL_DB", "aegiscare")
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "Dhruv.1603")


def get_conn():
    return pymysql.connect(
        host=MYSQL_HOST, port=MYSQL_PORT, user=MYSQL_USER, password=MYSQL_PASSWORD,
        database=MYSQL_DB, charset="utf8mb4", autocommit=False, cursorclass=pymysql.cursors.DictCursor
    )


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
