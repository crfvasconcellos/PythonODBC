"""
Gerenciador de Conexão e Transações com PostgreSQL via pyodbc.
Centraliza credenciais (.env), controle manual de transação (autocommit=False)
e conversão padronizada de resultados para dicionários.
"""
import os
from contextlib import contextmanager
import pyodbc
from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv(filename=".env", usecwd=True))


def get_connection() -> pyodbc.Connection:
    """
    [CONCEITO AVALIADO] Conectividade ODBC e Controle Manual de Transação (ACID)
    [SLIDE/CAPÍTULO] Cap. 5 / Cap. 17 (Integração de Aplicação e Transações)
    [DESCRIÇÃO] Abre conexão com o PostgreSQL via pyodbc com autocommit desativado
                para garantir atomicidade via commit() e rollback() explícitos.
    """
    driver = os.getenv("DB_DRIVER", "PostgreSQL Unicode(x64)")
    server = os.getenv("DB_SERVER", "localhost")
    port = os.getenv("DB_PORT", "5432")
    database = os.getenv("DB_DATABASE", "biblioteca")
    user = os.getenv("DB_USER", "postgres")
    password = os.getenv("DB_PASSWORD", "")

    conn_str = (
        f"DRIVER={{{driver}}};"
        f"SERVER={server};"
        f"PORT={port};"
        f"DATABASE={database};"
        f"UID={user};"
        f"PWD={password};"
    )
    conn = pyodbc.connect(conn_str, autocommit=False, timeout=10)
    return conn


def fetch_as_dicts(cursor: pyodbc.Cursor) -> list[dict]:
    """Converte todas as linhas do cursor em uma lista de dicionários {coluna: valor}."""
    if not cursor.description:
        return []
    colunas = [col[0] for col in cursor.description]
    return [dict(zip(colunas, row)) for row in cursor.fetchall()]


@contextmanager
def transaction_scope():
    """
    Gerenciador de contexto transacional.
    Faz commit() em caso de sucesso, rollback() em caso de pyodbc.Error
    e fecha a conexão no bloco finally.
    """
    conn = get_connection()
    try:
        yield conn
        conn.commit()
    except pyodbc.Error as erro:
        conn.rollback()
        print(f"[ERRO DE BANCO / ROLLBACK EXECUTADO] {erro}")
        raise
    finally:
        conn.close()
