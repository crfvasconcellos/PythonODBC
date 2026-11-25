"""Conexão ODBC com PostgreSQL e controle transacional ACID."""
import os
from contextlib import contextmanager
import pyodbc
from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv(filename=".env", usecwd=True))


def conectar():
    conn_str = (
        f"DRIVER={{{os.getenv('DB_DRIVER', 'PostgreSQL Unicode(x64)')}}};"
        f"SERVER={os.getenv('DB_SERVER', 'localhost')};"
        f"PORT={os.getenv('DB_PORT', '5432')};"
        f"DATABASE={os.getenv('DB_DATABASE', 'biblioteca')};"
        f"UID={os.getenv('DB_USER', 'postgres')};"
        f"PWD={os.getenv('DB_PASSWORD', '')};"
    )
    conn = pyodbc.connect(conn_str, autocommit=False, timeout=10)
    conn.autocommit = False
    return conn


@contextmanager
def transacao():
    conn = conectar()
    cursor = conn.cursor()
    try:
        yield cursor
        conn.commit()
    except (pyodbc.Error, Exception):
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()
