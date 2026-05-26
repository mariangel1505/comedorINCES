import os
import psycopg2
from psycopg2.extras import RealDictCursor

DB_CONFIG = {
    "host": os.environ.get("SGSC_DB_HOST", "localhost"),
    "port": os.environ.get("SGSC_DB_PORT", "5433"),
    "user": os.environ.get("SGSC_DB_USER", "postgres"),
    "password": os.environ.get("SGSC_DB_PASSWORD", "12345"),
    "database": os.environ.get("SGSC_DB_NAME", "sistema_comedor"),
}


def get_connection():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except psycopg2.OperationalError as error:
        raise ConnectionError(f"No se pudo conectar a PostgreSQL: {error}")


def execute_query(query, params=None, fetch_one=False, fetch_all=False, commit=False):
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(query, params)
            if commit:
                conn.commit()
            if fetch_one:
                return cursor.fetchone()
            if fetch_all:
                return cursor.fetchall()
    finally:
        conn.close()